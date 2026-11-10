# User-level laboratory report template

This LaTeX template is part of the user-level `lab-report` skill. Reports load `labreport.sty` from this skill instead of copying a shared template into each project.

## Report source

```tex
\documentclass[11pt,a4paper]{article}
\usepackage{labreport}
```

Set metadata before `\LabMakeCover`:

```tex
\LabCourse{Computer Networks}
\LabCourseShort{Computer Networks}
\LabReportType{Experimental Report}
\LabNumber{4}
\LabTitle{Dynamic Routing}
\LabStudent{Sample Student}
\LabStudentID{000000000000}
\LabMajor{Sample Major}
\LabCollege{Sample College}
\LabDate{10 November 2026}
\LabHeaderRight{Laboratory 4}
```

Then:

```tex
\begin{document}
\LabMakeCover
\LabBeginMain
```

Use the generated `compile-report.ps1` in a report directory. It sets `TEXINPUTS` to this skill's template folder, compiles the PDF, rejects unresolved pending markers and missing evidence figures, renders every page, and reports layout warnings.

`LabEvidenceFigure` renders `figures/<filename>` when available and a visible missing-evidence box otherwise:

```tex
\LabEvidenceFigure[0.88]{result.png}{Save the verified screenshot here.}
```

Available public macros include `\LabPending`, `\LabCoverField`, `\LabWordmarkFile`, `\LabSealFile`, `\LabHeaderLeft`, and `\LabHeaderRight`.
