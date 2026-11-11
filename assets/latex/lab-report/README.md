# User-level laboratory report template

This LaTeX template is part of the user-level `lab-report` skill. It includes the default NUIST wordmark and seal, a cover, and a flexible body outline. Reports load `labreport.sty` from this skill instead of copying a shared template into each project.

## Report source

```tex
\documentclass[11pt,a4paper]{article}
\usepackage{labreport}
```

Set metadata before `\LabMakeCover`:

```tex
\LabCourse{Course Name}
\LabCourseShort{Course Name}
\LabReportType{Experimental Report}
\LabNumber{1}
\LabTitle{Report Title}
\LabStudent{Sample Student}
\LabStudentID{000000000000}
\LabMajor{Sample Major}
\LabCollege{Sample College}
\LabDate{10 November 2026}
\LabHeaderRight{Laboratory 1}
```

Then:

```tex
\begin{document}
\LabMakeCover
\LabBeginMain
```

Use the generated `compile-report.ps1` in a report directory. It sets `TEXINPUTS` to this skill's template folder, compiles the PDF, rejects unresolved pending markers and missing figures, renders every page, and reports layout warnings.

## Flexible figures

`\LabFigure[width]{filename}{caption}{label}` provides a default float wrapper:

```tex
\LabFigure[0.85]{figure-file.png}{Caption text.}{fig:result}
```

Images are optional. Data charts, diagrams, photographs, screenshots, and other user-supplied assets can be used through `\LabFigure` or standard LaTeX `figure` and `\includegraphics` commands. The template imposes no required figure count or visual sequence.

Available public macros include `\LabPending`, `\LabFigure`, `\LabCoverField`, `\LabWordmarkFile`, `\LabSealFile`, `\LabHeaderLeft`, and `\LabHeaderRight`. The wordmark and seal macros can override the bundled NUIST branding for a different institution.
