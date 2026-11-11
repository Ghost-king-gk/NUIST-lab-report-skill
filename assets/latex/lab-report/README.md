# Shared LaTeX report assets

This directory contains the NUIST cover, typography, tables, code, figures, and native PDF wrapper used by the `lab-report` skill.

`report-wrapper.tex` is an internal build template for `scripts/report_tool.py`. Report authors normally edit `report.md`, not TeX. When a native LaTeX PDF is requested, the tool converts the Markdown body with Pandoc, fills this wrapper with `report.json`, compiles in a temporary directory, and copies only the final PDF into the report project.

The public `labreport.sty` macros remain available for explicit LaTeX customization:

- `\LabMakeCover`
- `\LabBeginMain`
- `\LabFigure`
- `\LabPending`
- `\LabWordmarkFile`
- `\LabSealFile`

Keep the shared style and branding here. Do not copy generator scripts or build intermediates into a report project. Bash and WSL builds use the same `scripts/report_tool.py` implementation as PowerShell builds.
