---
name: lab-report
description: Create and visually verify flexible course laboratory reports from a shared LaTeX cover and body outline. Use for lab reports that need consistent cover metadata, an adaptable structure, optional task-specific data visualizations, user-supplied images, and final PDF layout checks. Do not use for standalone papers, theses, or documents without a report cover and structured body.
license: MIT
metadata:
  category: education
  output: latex-pdf
  harnesses: Codex, Claude Code, OpenCode, Hermes, Pi, Oh My Pi, DSH, ZCode, WorkBuddy
---

# Lab Report

Use a stable LaTeX cover and a flexible body scaffold. The skill handles presentation and structure; the user controls the report argument, section emphasis, and visual assets.

## Inputs

Identify:

- course, lab number, report title, and language;
- task statement, required questions, and desired sections;
- available data, tables, observations, or results that may justify a chart;
- optional user-provided images, diagrams, photographs, screenshots, or layout references;
- any user-defined outline or visual direction.

Student name, ID, major, college, and optional institution images are normally loaded from the user's `personal-profile.json` after installation.

Presentation details that are missing may use sensible defaults. Do not invent data, measurements, sources, or conclusions.

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

Each report contains its source, optional figures, and build output:

```text
reports/<Lab_Name>/
|-- main.tex
|-- figures/
|-- build/
`-- compile-report.ps1
```

The `figures/` directory may stay empty. Read [report-contract.md](references/report-contract.md) for the default outline, figure policy, and final checks.

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

## Workflow

1. Read the task and choose an outline. Start from the template and add, remove, merge, or reorder sections when the task or user requests it.
2. Use tables for precise comparisons and figures for relationships that are easier to inspect visually.
3. When data supports a chart, create a task-specific visualization and place the resulting file under `figures/`.
4. Accept user-provided images and layout ideas directly. Use `\LabFigure` when its default float wrapper helps, or standard LaTeX figure and `\includegraphics` commands for custom layouts.
5. Replace every `\LabPending{...}` with finished prose or a deliberate unresolved statement.
6. Compile and inspect layout:

```powershell
.\compile-report.ps1 -AllowPending   # scaffold preview
.\compile-report.ps1                 # final check
```

Final mode rejects `[PENDING:` markers, missing `\LabFigure` files, overfull or underfull boxes, and LaTeX errors. It renders page PNGs under `build/pages` and reports the PDF page count.

## Figure policy

Figures are optional. Do not require a fixed figure count or a prescribed image sequence. Generate a data chart only when the available data and the report question make that chart informative. Preserve user-supplied images, captions, ordering, and placement unless the user asks for editorial guidance.

## Writing discipline

- Separate reported data from interpretation.
- Use exact units, sample counts, effect sizes, tolerances, and boundary conditions when available.
- Use prose for the argument; reserve tables for multi-condition comparisons and lists for strict procedures.
- Give every figure a caption that identifies the data or concept shown and its relevance.
- State conflicting results and measurement limits directly.
- Do not describe a simulation as hardware timing or performance data.
- Do not claim success from configuration state alone when a behavioral test is required.

