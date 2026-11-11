# Changelog

## 2.0.1 - 2026-11-11

- Added Linux, Bash, and WSL entry points for installation, scaffolding, and report builds.
- Added `install.sh`, shared shell helpers, and thin Bash wrappers around the canonical Python tool.
- Documented `python3`, WSL `/mnt` paths, non-interactive profile installation, and shell-specific verification commands.
- Enforced LF line endings for shell scripts through `.gitattributes`.

## 2.0.0 - 2026-11-11

- Consolidated DOCX and PDF delivery into one `lab-report` skill.
- Added a shared `report.md` source and `report.json` metadata contract.
- Added a reusable python-docx builder with the NUIST A4 cover, A4 body geometry, tables, figures, code, equations, and accessibility metadata.
- Added Office and native LaTeX PDF backends from the same report source.
- Added `report_tool.py` for scaffold creation, final builds, and dependency checks.
- Moved report generation logic out of consuming projects and removed intermediate artifacts from final report trees.
- Established that the NUIST cover and report contract override generic `documents` skill styling.

## 1.2.0 - 2026-11-10

- Refocused the skill on the shared LaTeX cover and a flexible body outline.
- Removed the fixed source-capture directory and capture-first report workflow.
- Replaced the legacy figure macro with optional `LabFigure` support for generated charts and user-supplied images.
- Updated scaffolding, compiler validation, bilingual documentation, and the default report outline.

## 1.1.1 - 2026-11-10

- Renamed the repository to `NUIST-lab-report-skill`.

## 1.1.0 - 2026-11-10

- Added cross-harness installation for Codex, Claude Code, OpenCode, Hermes, Pi, Oh My Pi, DSH, ZCode, and WorkBuddy.
- Added bilingual README with top navigation links.
- Added a harness path matrix and installer dry-run mode.
- Kept NUIST wordmark and seal in the shared cover.
- Kept College and all other student fields as installer-provided local profile values.

## 1.0.1 - 2026-11-10

- Keep the NUIST wordmark and seal in the shared skill cover.
- Restrict interactive installation to the student fields and optional branding overrides.

## 1.0.0 - 2026-11-10

- Initial shareable `lab-report` skill.
- User-level LaTeX style and cover template.
- Personalized installation through `install.ps1`.
- Initial report contract and project scaffolding.
- Compilation, pending-marker checks, missing-figure checks, layout checks, and page rendering.
