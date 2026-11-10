---
name: lab-report
description: Create, standardize, compile, and visually verify course laboratory reports from a shared LaTeX template. Use for experimental reports, lab manuals, measurement reports, computational labs, and course practical reports that need a consistent cover, evidence handling, results tables, discussion, appendix, and PDF QA. Do not use for standalone papers, theses, or non-experimental documents.
license: MIT
metadata:
  category: education
  output: latex-pdf
  harnesses: Codex, Claude Code, OpenCode, Hermes, Pi, Oh My Pi, DSH, ZCode, WorkBuddy
---

# Lab Report

Create a reproducible laboratory report without inventing observations.

## Inputs

Identify:

- course and lab number;
- report title and language;
- apparatus, software, topology, dataset, or experimental setup;
- raw evidence location and required figures;
- claims the measurements can support.

Student name, ID, major, college, and optional institution images are normally loaded from the user's `personal-profile.json` after installation.

Minor missing presentation details may use sensible defaults. Do not guess measured values, configuration state, sample size, uncertainty, or causal conclusions.

## Template location

The LaTeX style, cover assets, and starter document live inside the user-level skill:

```text
<skill-root>/assets/latex/lab-report/
|-- labreport.sty
|-- main-template.tex
|-- README.md
`-- assets/
```

The cover ships with the bundled NUIST wordmark and seal. Reports reference this user-level assets folder through the generated compiler. Do not create or copy a `templates/latex/lab-report` directory inside each project.

Each report contains only its own content and evidence:

```text
reports/<Lab_Name>/
|-- main.tex
|-- figures/
|-- evidence/
|-- build/
`-- compile-report.ps1
```

Read [report-contract.md](references/report-contract.md) when deciding the report structure, evidence hierarchy, figure rules, result tables, or final acceptance checks.

## Personal profile

The shared repository stores no personal data. The repository installer personalizes the skill for each user.

The installer asks which harness or harnesses to populate, then asks for student name, student ID, major, college, and optional wordmark and seal images. It writes those values only into each selected user-level skill target:

```text
<installed-skill-root>/personal-profile.json
```

See `HARNESSES.md` for the supported harness paths. `College` is a per-user cover field and is never hardcoded in the shared skill.

`new-lab-report.ps1` loads this profile automatically. Explicit parameters such as `-Student`, `-StudentID`, `-WordmarkFile`, and `-SealFile` override the stored defaults for one report. If the profile is missing, do not invent personal data; instruct the user to run the repository installer or supply those parameters explicitly.

## Scaffold

For a new report directory, run:

```powershell
.\scripts\new-lab-report.ps1 `
  -ProjectRoot <project-root> `
  -Course "<course>" `
  -LabNumber "<lab number>" `
  -Title "<report title>"
```

The script loads the installed personal profile, generates the report from the user-level template assets, and writes a small local compiler wrapper. It refuses to overwrite an existing report directory and does not copy the LaTeX style into the project.

## Build the report

1. Inventory the evidence and record exact observed values.
2. Put raw evidence under `evidence/` and curated report images under `figures/`.
3. Replace every `\LabPending{...}` with verified prose, data, or an explicit unresolved issue.
4. Use `LabEvidenceFigure` for evidence images so missing files are visible during development.
5. Compile and inspect layout:

```powershell
.\compile-report.ps1 -AllowPending   # scaffold preview
.\compile-report.ps1                 # final check
```

The final mode rejects `[PENDING:` markers and missing `LabEvidenceFigure` files. It runs `latexmk`, checks for overfull or underfull boxes, renders page PNGs under `build/pages`, and reports the PDF page count.

## Writing discipline

- Separate observed facts from interpretation.
- Use exact units, sample counts, loss rates, effect sizes, tolerances, and boundary conditions.
- Use prose for the argument; reserve tables for multi-condition comparisons and lists for strict procedures.
- Give every figure a claim-bearing caption and refer to it in the text.
- State conflicting evidence and measurement limits directly.
- Do not describe a simulation as hardware timing or performance evidence.
- Do not claim success from configuration state alone when a behavioral test is required.


