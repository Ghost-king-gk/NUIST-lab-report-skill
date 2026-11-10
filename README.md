# Lab Report Skill for Codex

A shareable Codex skill that provides a complete, reusable LaTeX system for course laboratory reports. The repository contains the actual `.sty` template, cover assets, report scaffolding, compilation scripts, and an evidence discipline rather than only prompt instructions.

![Laboratory report cover preview](docs/preview-cover.png)

## Features

- Standard laboratory report cover and typography
- User-level LaTeX template; no per-project template copy
- Interactive personal installation
- Optional custom university wordmark and seal
- Evidence-first report structure
- Tables for multi-condition result matrices
- Code and terminal listings with consistent styling
- Missing-evidence and unresolved-placeholder checks
- Automatic PDF compilation, page rendering, and layout-warning checks
- Cross-platform LaTeX source with Windows PowerShell tooling

## Repository structure

```text
codex-lab-report-skill/
|-- SKILL.md
|-- install.ps1
|-- profile.example.json
|-- README.md
|-- LICENSE
|-- CHANGELOG.md
|-- agents/
|   `-- openai.yaml
|-- assets/
|   `-- latex/
|       `-- lab-report/
|           |-- labreport.sty
|           |-- main-template.tex
|           |-- README.md
|           `-- assets/
|               |-- university_wordmark.png
|               `-- university_logo.jpeg
|-- references/
|   `-- report-contract.md
`-- scripts/
    |-- new-lab-report.ps1
    `-- compile-report.ps1
```

## Requirements

- Codex with user-level skill discovery enabled
- TeX Live with `latexmk`, `pdflatex`, `pdftoppm`, and `pdfinfo`
- PowerShell 7 or Windows PowerShell

Check the LaTeX tools:

```powershell
latexmk -v
pdflatex -v
pdftoppm -v
pdfinfo -v
```

## Install and personalize

Clone the repository anywhere, then run the installer:

```powershell
git clone <YOUR_REPOSITORY_URL> codex-lab-report-skill
Set-Location codex-lab-report-skill
.\install.ps1
```

The installer asks for:

1. Student name
2. Student ID
3. Major
4. College or institution
5. Optional university wordmark image
6. Optional university seal or logo image

It installs the personalized skill to:

```powershell
$HOME\.agents\skills\lab-report
```

Personal fields are written to:

```text
$HOME\.agents\skills\lab-report\personal-profile.json
```

That file is excluded from Git. The shared repository contains only blank examples and neutral placeholder logos.

If either logo path is left blank, the installer uses the bundled placeholder assets. If an image is supplied, it is copied into the installed user-level skill and referenced by the local profile.

### Replace an existing installation

```powershell
.\install.ps1 -Force
```

The existing target folder is moved to a timestamped backup before installation.

## Create a report

From any project:

```powershell
& "$HOME\.agents\skills\lab-report\scripts\new-lab-report.ps1" `
  -ProjectRoot (Get-Location).Path `
  -Course "Computer Networks" `
  -LabNumber "2" `
  -Title "Virtual LAN and 802.1Q Trunking"
```

The student name, ID, major, college, and logo paths are loaded from `personal-profile.json`. Course, lab number, title, and report date remain report-specific.

The script creates:

```text
reports/Lab2_Computer_Networks/
|-- main.tex
|-- figures/
|-- evidence/
|-- build/
|-- compile-report.ps1
|-- report.config.json
`-- README.md
```

No shared LaTeX template is copied into the project.

## Build

Scaffold preview:

```powershell
Set-Location reports\Lab2_Computer_Networks
.\compile-report.ps1 -AllowPending
```

Final build:

```powershell
.\compile-report.ps1
```

The final build rejects:

- unresolved `\LabPending{...}` markers;
- missing `LabEvidenceFigure` files;
- Overfull or Underfull page boxes;
- LaTeX compilation failures.

It then renders every PDF page to `build\pages` and reports the PDF page count.

## Customize the cover

The installed profile can be edited later:

```text
$HOME\.agents\skills\lab-report\personal-profile.json
```

The shareable template itself is:

```text
$HOME\.agents\skills\lab-report\assets\latex\lab-report\labreport.sty
```

The report source can override the profile for one report:

```powershell
.\scripts\new-lab-report.ps1 `
  -Course "Physics" `
  -LabNumber "1" `
  -Title "Measurement" `
  -WordmarkFile "D:\branding\wordmark.png" `
  -SealFile "D:\branding\seal.jpeg"
```

## Privacy

The shared repository intentionally contains:

- no student name;
- no student ID;
- no personal contact information;
- no local absolute paths;
- no university logo or seal.

Personal information is requested only during installation and written to the installing user's own `$HOME\.agents\skills\lab-report` directory. It is not uploaded or transmitted by these scripts.

## License

MIT. See [LICENSE](LICENSE).
