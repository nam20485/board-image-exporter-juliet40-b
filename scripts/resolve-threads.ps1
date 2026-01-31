<#
.SYNOPSIS
    Resolves review comment threads on a GitHub Pull Request.

.DESCRIPTION
    This script uses the GitHub GraphQL API to mark review comment threads as resolved.
    It can either fetch all unresolved threads from a PR or resolve specific thread IDs
    provided as arguments. After resolution, it verifies that no unresolved threads remain.

.PARAMETER PrNumber
    The Pull Request number to resolve threads for. If not provided, uses the active PR
    from the current branch.

.PARAMETER Owner
    The repository owner. Defaults to 'nam20485'.

.PARAMETER Repo
    The repository name. Defaults to 'board-image-exporter-juliet40-b'.

.PARAMETER ThreadIds
    Optional array of specific thread IDs to resolve. If not provided, fetches all
    unresolved threads from the PR.

.EXAMPLE
    .\resolve-threads.ps1 -PrNumber 8
    Resolves all unresolved threads on PR #8

.EXAMPLE
    .\resolve-threads.ps1 -PrNumber 8 -ThreadIds "PRRT_kwDORDp1Cc5r8kow","PRRT_kwDORDp1Cc5r8ko4"
    Resolves only the specified thread IDs on PR #8

.EXAMPLE
    .\resolve-threads.ps1
    Resolves all unresolved threads on the active PR for the current branch

.NOTES
    Requires GitHub CLI (gh) to be installed and authenticated.
    Author: GitHub Copilot
    Date: 2026-01-30
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, HelpMessage = "PR number to resolve threads for")]
    [int]$PrNumber,

    [Parameter(Mandatory = $false)]
    [string]$Owner = "nam20485",

    [Parameter(Mandatory = $false)]
    [string]$Repo = "board-image-exporter-juliet40-b",

    [Parameter(Mandatory = $false, HelpMessage = "Specific thread IDs to resolve")]
    [string[]]$ThreadIds
)

# If PR number not provided, try to get it from current branch
if (-not $PrNumber) {
    Write-Host "No PR number provided, detecting from current branch..." -ForegroundColor Yellow
    $prInfo = gh pr status --json number,headRefName 2>&1 | ConvertFrom-Json
    if ($prInfo.currentBranch.number) {
        $PrNumber = $prInfo.currentBranch.number
        Write-Host "Detected PR #$PrNumber" -ForegroundColor Green
    } else {
        Write-Host "Error: Could not detect PR number. Please provide -PrNumber parameter." -ForegroundColor Red
        exit 1
    }
}

# If no thread IDs provided, fetch all unresolved threads from the PR
if (-not $ThreadIds -or $ThreadIds.Count -eq 0) {
    Write-Host "Fetching unresolved threads from PR #$PrNumber..." -ForegroundColor Cyan
    
    $query = @"
{
  repository(owner: "$Owner", name: "$Repo") {
    pullRequest(number: $PrNumber) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
        }
      }
    }
  }
}
"@
    
    $result = gh api graphql -f query=$query | ConvertFrom-Json
    $allThreads = $result.data.repository.pullRequest.reviewThreads.nodes
    $ThreadIds = $allThreads | Where-Object { -not $_.isResolved } | Select-Object -ExpandProperty id
    
    if ($ThreadIds.Count -eq 0) {
        Write-Host "No unresolved threads found on PR #$PrNumber!" -ForegroundColor Green
        exit 0
    }
    
    Write-Host "Found $($ThreadIds.Count) unresolved thread(s)" -ForegroundColor Cyan
}

# Resolve threads
$count = 0
$resolved = 0
$failed = 0
$total = $ThreadIds.Count

foreach ($threadId in $ThreadIds) {
    $count++
    Write-Host "[$count/$total] Resolving $threadId..." -NoNewline
    
    try {
        $result = gh api graphql -F threadId=$threadId -f query='mutation($threadId: ID!) { resolveReviewThread(input: {threadId: $threadId}) { thread { id isResolved } } }' 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host " ✓" -ForegroundColor Green
            $resolved++
        } else {
            Write-Host " ✗" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host " ✗ Error: $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Total:    $total" -ForegroundColor White
Write-Host "  Resolved: $resolved" -ForegroundColor Green
Write-Host "  Failed:   $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Gray" })
Write-Host "========================================" -ForegroundColor Cyan

# Verify no unresolved threads remain
Write-Host "`nVerifying resolution status..." -ForegroundColor Cyan

$verifyQuery = @"
{
  repository(owner: "$Owner", name: "$Repo") {
    pullRequest(number: $PrNumber) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
        }
      }
    }
  }
}
"@

$verifyResult = gh api graphql -f query=$verifyQuery | ConvertFrom-Json
$remainingThreads = $verifyResult.data.repository.pullRequest.reviewThreads.nodes
$unresolvedCount = ($remainingThreads | Where-Object { -not $_.isResolved }).Count
$totalThreadCount = $remainingThreads.Count

Write-Host "PR #$PrNumber thread status:" -ForegroundColor Cyan
Write-Host "  Total threads:      $totalThreadCount" -ForegroundColor White
Write-Host "  Resolved threads:   $($totalThreadCount - $unresolvedCount)" -ForegroundColor Green
Write-Host "  Unresolved threads: $unresolvedCount" -ForegroundColor $(if ($unresolvedCount -gt 0) { "Red" } else { "Green" })

if ($unresolvedCount -gt 0) {
    Write-Host "`n✗ ERROR: $unresolvedCount unresolved thread(s) remain on PR #$PrNumber!" -ForegroundColor Red
    Write-Host "The following threads are still unresolved:" -ForegroundColor Yellow
    $remainingThreads | Where-Object { -not $_.isResolved } | ForEach-Object {
        Write-Host "  - $($_.id)" -ForegroundColor Yellow
    }
    exit 1
}

if ($failed -eq 0) {
    Write-Host "`n✓ All review threads successfully resolved and verified!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n✗ Some threads failed to resolve ($failed failures)" -ForegroundColor Red
    exit 1
}
