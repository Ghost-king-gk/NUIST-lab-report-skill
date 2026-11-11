---
name: lab-report
description: Create and build flexible NUIST laboratory reports as editable DOCX and optional PDF from one Markdown source, with a fixed university cover, structured experiment body, results tables, optional figures, and final layout validation. Use for course lab reports. Do not use for standalone papers, theses, or documents without a laboratory-report cover and experiment structure.
license: MIT
metadata:
  category: education
  output: docx,pdf
  harnesses: Codex, Claude Code, OpenCode, Hermes, Pi, Oh My Pi, DSH, ZCode, WorkBuddy
---

# Lab Report

Create a polished laboratory report without putting report-generator scripts or build intermediates into the consuming project. One Markdown source drives both DOCX and PDF.

## Deliverable contract

- Default to an editable `.docx`.
- Produce PDF only when requested or when the submission requires it.
- Keep one content source: `report.md`. DOCX and PDF must not maintain separate report text.
- Keep the project clean. The reusable builder, cover assets, and validation helpers stay inside this skill.
- The final project contains experiment source code, its README, raw results, and final report files. It does not contain report-builder scripts, extracted slides, temporary renderers, page PNGs, caches, or failed build artifacts.

## Format decision

Keep DOCX and PDF in this single skill. They share the same cover, metadata, Markdown body, tables, figures, numbering, and evidence rules. Split skills would duplicate those invariants and allow the Word and PDF versions to drift.

Use:

- `docx` for the editable submission and layout-authoritative artifact;
- `pdf` for review, printing, or submission when a fixed-layout file is required;
- `docx,pdf` when both are required.

## Authority order

This skill controls the laboratory-report cover, A4 geometry, heading hierarchy, table treatment, caption style, and report structure. If the `documents` skill is also available, use it only for generic DOCX rendering, OOXML validation, accessibility checks, or PDF conversion. Do not apply the generic document skill's Letter page size, alternate cover, or style preset over this skill.

## Inputs

Identify:

- course, course short name, lab number, report title, report type, and language;
- task statement, required questions, and any required deliverable format;
- experiment source, measured results, tables, traces, or logs;
- optional user-provided diagrams, photographs, screenshots, or layout references;
- any user-defined section order or emphasis.

Cover identity is normally loaded from `personal-profile.json`. Do not invent student details, measurements, sources, or conclusions.

## Report workspace

Create a report with:

```powershell
python <skill-root>/scripts/report_tool.py new `
  --project-root <project-root> `
  --course "<course>" `
  --lab-number "<lab-number>" `
  --title "<report-title>" `
  --format docx
```

On Linux or WSL, use the Bash wrapper or `python3` directly:

```bash
bash <skill-root>/scripts/new-lab-report.sh \
  --project-root <project-root> \
  --course "<course>" \
  --lab-number "<lab-number>" \
  --title "<report-title>" \
  --format docx
```

The scaffold contains only:

```text
reports/<report>/
|-- README.md
|-- report.json
|-- report.md
|-- figures/
`-- output/
```

No `main.tex`, report builder, compiler wrapper, temporary directory, or figure generator is added to the consuming project. The shared tool generates optional LaTeX only inside a disposable build location.

Read [report-source.md](references/report-source.md) before editing `report.md`. Read [report-contract.md](references/report-contract.md) when deciding the scientific structure, evidence placement, or figure policy.

## Workflow

1. Inspect the task, source data, slides, code, and results. Separate observed facts from interpretation.
2. Keep only useful result files in `results/` or the project's existing result location. Do not retain extracted source archives or renderer caches.
3. Create or edit `report.json` for cover metadata and `report.md` for body content.
4. Put optional report images under `figures/` using stable relative paths. Keep generated analysis data and code in their normal project locations.
5. Replace every `[PENDING: ...]` marker before final delivery.
6. Build the requested outputs:

```powershell
python <skill-root>/scripts/report_tool.py build `
  --report-dir <report-dir> `
  --formats docx,pdf
```

Linux and WSL equivalent:

```bash
bash <skill-root>/scripts/compile-report.sh \
  --report-dir <report-dir> \
  --formats docx,pdf
```

Use `--allow-pending` only for a scaffold preview.

7. Inspect the final artifact. For DOCX, read [docx-format.md](references/docx-format.md). For PDF, read [pdf-export.md](references/pdf-export.md).
8. Render every final page to images outside the report project, inspect each page, and fix clipping, overlap, broken tables, orphan headings, missing glyphs, and unintended blank pages before delivery.

## Shell entry points

- Windows: `install.ps1`, `scripts/new-lab-report.ps1`, `scripts/compile-report.ps1`.
- Linux and WSL: `install.sh`, `scripts/new-lab-report.sh`, `scripts/compile-report.sh`.
- The Python entry points remain the canonical implementation: `python` on Windows and `python3` on Linux/WSL.

## DOCX and PDF build paths

- DOCX is generated directly from `report.md` with the shared NUIST cover and A4 report styles.
- PDF uses the same `report.md`. With `--pdf-backend auto`, the tool exports DOCX through LibreOffice when available; otherwise it builds a native LaTeX PDF through Pandoc and `latexmk`.
- Native LaTeX retains the existing `labreport.sty` cover. The generated TeX source and auxiliary files are temporary and removed after the build.

Use `--pdf-backend office` when the PDF must match the DOCX exactly. Use `--pdf-backend latex` when TeX sources are required or LibreOffice is unavailable.

## Figure policy

Figures are optional. Generate a chart only when data and the report question make a relationship easier to inspect than prose or a table. Preserve user-supplied images, captions, ordering, and intended composition. Every figure needs a specific caption and alternative text in DOCX.

## Writing discipline

- Separate measured results from interpretation.
- Use exact units, sample sizes, tolerances, effect sizes, and operating boundaries.
- Use tables for repeated comparisons and prose for mechanism and interpretation.
- State conflicting evidence directly and identify the variable that explains the disagreement.
- Do not describe simulated timing as hardware performance.
- Do not claim success from configuration alone when a behavioral test is required.
- Do not leave duplicate final archives or both editable and generated copies of the same artifact unless the user asks for both.

