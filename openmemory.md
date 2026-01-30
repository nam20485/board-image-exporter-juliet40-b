## Overview
- Template repo for AI-orchestrated dynamic workflows.
- Uses remote instructions from `nam20485/agent-instructions` (branch `optimization`); local `local_ai_instruction_modules` mirror references.
- PowerShell-first environment; dockerized workflow agent available.
- Current app target: PCB Renderer CLI (Python 3.11) per `plan_docs/PCB Renderer CLI Specification.md`.

## Architecture
- Dynamic workflows executed via `orchestrate-dynamic-workflow` assignment; workflow/assignment definitions resolved from remote raw URLs before execution.
- GitHub operations follow tool priority: MCP GitHub → VS Code integration → `gh` CLI (last resort); PRs/branch protection respected.
- Testing/security: TruffleHog secret scan workflow; local scripts in `scripts/security/run-trufflehog.ps1|.sh`.
- Docker: `docker/Dockerfile`, `docker-compose.yml`, `.env.example`; image runs workflows read-only by default.
- Plan docs: architecture guide/details under `plan_docs/` (PCB renderer domain, validation rules, coordinate transforms).

## Components
- Dynamic Workflow Orchestrator: executes scripts/events from remote workflow files, enforces acceptance criteria, produces run reports.
- PCB Renderer domain (planned): Pydantic models for ECAD schema, normalization to mm, validation engine (14 invalid board cases), numpy-based transforms, matplotlib rendering, CLI (`render/validate/info`), tests (pytest + hypothesis + syrupy).
- Dev Tooling: PowerShell scripts for labels/milestones (`scripts/import-labels.ps1`, `scripts/create-milestones.ps1`); devcontainer config; GitHub workflows for lint/secret scan.

## Patterns
- Correctness-first, deterministic outputs; offline operation.
- Unit normalization to millimeters immediately after parse.
- Validation collects errors (no fail-fast) with structured codes.
- Rendering uses halo text effect for RefDes readability.
- Plan/issue creation uses `.github/ISSUE_TEMPLATE/application-plan.md`; milestones and epics linked to GitHub Project.

## User Defined Namespaces
- (None defined)