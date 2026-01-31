# Scripts Directory

This directory contains utility scripts for repository automation and management.

## Available Scripts

### resolve-threads.ps1

Resolves review comment threads on GitHub Pull Requests using the GitHub GraphQL API.

**Usage:**

```powershell
# Resolve all unresolved threads on current branch's PR
.\resolve-threads.ps1

# Resolve all unresolved threads on a specific PR
.\resolve-threads.ps1 -PrNumber 8

# Resolve specific thread IDs on a PR
.\resolve-threads.ps1 -PrNumber 8 -ThreadIds "PRRT_xxx","PRRT_yyy"

# Get help
Get-Help .\resolve-threads.ps1 -Full
```

**Features:**
- Automatically detects PR number from current branch if not provided
- Fetches all unresolved threads if no specific thread IDs provided
- Resolves threads via GitHub GraphQL API
- Verifies completion and fails if any unresolved threads remain
- Provides detailed progress and summary reporting

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Appropriate repository permissions to resolve review threads

**Exit Codes:**
- `0`: Success - all threads resolved
- `1`: Failure - some threads failed to resolve or unresolved threads remain

---

### create-milestones.ps1

Creates GitHub milestones for the project.

**Usage:**
```powershell
.\create-milestones.ps1
```

---

### import-labels.ps1

Imports GitHub labels from a configuration file.

**Usage:**
```powershell
.\import-labels.ps1
```

---

### test-github-permissions.ps1

Tests GitHub CLI authentication and repository permissions.

**Usage:**
```powershell
.\test-github-permissions.ps1
```

---

### update-remote-indices.ps1

Updates remote instruction indices for the dynamic workflow system.

**Usage:**
```powershell
.\update-remote-indices.ps1
```

---

## Common Prerequisites

All scripts require:
1. **PowerShell** (5.1 or later, PowerShell 7+ recommended)
2. **GitHub CLI** (`gh`) installed and authenticated:
   ```powershell
   gh auth login
   ```
3. Appropriate repository permissions for the operations being performed

## Contributing

When adding new scripts to this directory:
1. Include proper comment-based help (`.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`)
2. Use `[CmdletBinding()]` for advanced parameter handling
3. Provide clear error messages and exit codes
4. Update this README with usage information
5. Test the script thoroughly before committing

## Support

For issues or questions, please create an issue in the repository or contact the maintainers.
