# NUIST Lab Report Agent Skill

<p align="center">
  <a href="#english">English</a> ·
  <a href="#zh-cn">简体中文</a> ·
  <a href="HARNESSES.md">Harness paths</a> ·
  <a href="#installation">Install</a> ·
  <a href="#privacy">Privacy</a>
</p>

<p align="center">
  <img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-2ea44f">
  <img alt="LaTeX" src="https://img.shields.io/badge/output-LaTeX%20%2B%20PDF-008080">
  <img alt="Harnesses" src="https://img.shields.io/badge/harnesses-9-6f42c1">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

A portable Agent Skill for producing LaTeX laboratory reports with a polished NUIST cover, a flexible body outline, optional task-specific data charts, and room for user-supplied visual ideas. It supports Codex, Claude Code, OpenCode, Hermes, Pi, Oh My Pi, DSH, ZCode, and WorkBuddy.

面向高校实验报告的可移植 Agent Skill：提供统一的 NUIST LaTeX 封面、灵活的正文大纲、按任务生成的数据图，以及容纳用户自定义图片和排版想法的接口。

![Laboratory report cover preview](docs/preview-cover.png)

---

<a id="english"></a>

## English

### What this repository provides

The skill keeps two elements stable: the LaTeX cover and the report structure. Course content, section emphasis, chart choices, and image composition remain editable. The template ships no course-specific project and imposes no fixed image count or visual sequence.

| Component | Purpose |
|---|---|
| `SKILL.md` | Harness-neutral instructions for report generation |
| `assets/latex/lab-report/labreport.sty` | Cover, headers, typography, tables, code listings, and figure wrapper |
| `assets/latex/lab-report/main-template.tex` | Cover metadata and flexible body outline |
| `scripts/new-lab-report.ps1` | Creates a report directory and local compiler wrapper |
| `scripts/compile-report.ps1` | Compiles, validates, and renders the PDF |
| `references/report-contract.md` | Default outline, optional figure policy, and final checks |
| `install.ps1` | Installs a personalized copy for one or more harnesses |
| `HARNESSES.md` | Lists user-level and project-level discovery paths |

### Default report outline

The starter document uses this sequence:

1. Abstract
2. Task and Objectives
3. Background and Principles
4. Method and Implementation
5. Results and Data Analysis
6. Discussion
7. Conclusion
8. Optional appendix and references

Sections can be merged, removed, reordered, or replaced when the task or user requests a different argument structure.

### Data figures and user images

Figures are optional. If the supplied data support a useful comparison, trend, distribution, residual pattern, sensitivity result, or uncertainty display, the agent can generate a task-specific chart and place it under `figures/`.

Users choose whether images appear, how many to include, and how they are composed. Custom diagrams, photographs, screenshots, rendered simulations, and plots are accepted through the default figure wrapper:

```tex
\LabFigure[0.85]{figure-file.png}{Caption text.}{fig:result}
```

Standard LaTeX `figure` and `\includegraphics` commands remain available for custom layouts.

### Harness support

The skill targets Codex, Claude Code, OpenCode, Hermes, Pi, Oh My Pi, DSH, ZCode, and WorkBuddy. Native installation paths and project-level alternatives are listed in [HARNESSES.md](HARNESSES.md).

### Requirements

- A harness that supports Agent Skills or a compatible `SKILL.md` directory
- TeX Live with `latexmk`, `pdflatex`, `pdftoppm`, and `pdfinfo`
- PowerShell 7 or Windows PowerShell

```powershell
latexmk -v
pdflatex -v
pdftoppm -v
pdfinfo -v
```

### Installation

<a id="installation"></a>

```powershell
git clone <YOUR_REPOSITORY_URL> NUIST-lab-report-skill
Set-Location NUIST-lab-report-skill
.\install.ps1
```

The installer asks for one or more harness targets, then stores the student name, student ID, major, college, and optional custom branding in the local skill directory.

```powershell
.\install.ps1 -Harness codex
.\install.ps1 -Harness codex,claude-code,opencode
.\install.ps1 -Harness all
.\install.ps1 -Harness all -DryRun
```

Use `-TargetPath` for another compatible skill root. Existing targets require `-Force`; the installer creates a timestamped backup before replacement.

### Create a report

```powershell
.\scripts\new-lab-report.ps1 `
  -ProjectRoot (Get-Location).Path `
  -Course "Course Name" `
  -LabNumber "1" `
  -Title "Report Title"
```

The script loads the installed personal profile and creates:

```text
reports/<lab-name>/
|-- main.tex
|-- figures/
|-- build/
|-- compile-report.ps1
|-- report.config.json
`-- README.md
```

`figures/` can remain empty. The shared LaTeX style stays in the user-level skill and is loaded through the generated compiler wrapper.

### Build and verify

```powershell
.\compile-report.ps1 -AllowPending
.\compile-report.ps1
```

`-AllowPending` supports scaffold previews. Final mode rejects unresolved `\LabPending{...}` markers, missing images referenced through `\LabFigure`, LaTeX errors, and Overfull or Underfull layout boxes. The compiler renders every PDF page to `build/pages/` and reports the page count.

### Privacy

<a id="privacy"></a>

The shared repository contains the institutional NUIST wordmark and seal. Student fields and custom branding are written only to the installing user's local skill:

```text
<installed-skill-root>/personal-profile.json
```

The shared repository contains no student name, student ID, personal contact information, local absolute paths, or personal branding files.

### Repository map

```text
NUIST-lab-report-skill/
|-- SKILL.md
|-- HARNESSES.md
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
|-- docs/
|   `-- preview-cover.png
|-- references/
|   `-- report-contract.md
`-- scripts/
    |-- new-lab-report.ps1
    `-- compile-report.ps1
```

### License

MIT. See [LICENSE](LICENSE).

---

<a id="zh-cn"></a>

## 简体中文

### 仓库定位

这个仓库面向高校实验报告，提供一套可移植的 LaTeX 报告工作流。固定部分是 NUIST 封面、封面字段和正文骨架；课程内容、章节侧重、数据图选择、图片数量和版式由具体任务与用户决定。

仓库不内置课程项目案例，不规定图片数量，也不要求固定的全部视觉顺序。Agent 负责把用户提供的任务、数据、图片和排版想法组织成可编译的 PDF 报告。

### 核心组件

| 组件 | 作用 |
|---|---|
| `SKILL.md` | 与 harness 无关的报告生成指令 |
| `assets/latex/lab-report/labreport.sty` | 封面、页眉、字体、表格、代码块和图片包装宏 |
| `assets/latex/lab-report/main-template.tex` | 封面字段和可调整的正文大纲 |
| `scripts/new-lab-report.ps1` | 创建报告目录与本地编译入口 |
| `scripts/compile-report.ps1` | 编译、检查并逐页渲染 PDF |
| `references/report-contract.md` | 默认大纲、可选图片策略和最终检查 |
| `install.ps1` | 为一个或多个 harness 安装个性化副本 |
| `HARNESSES.md` | 列出各 harness 的用户级与项目级路径 |

### 默认正文大纲

起始模板采用以下顺序：

1. 摘要
2. 任务与目标
3. 背景与原理
4. 方法与实现
5. 结果与数据分析
6. 讨论
7. 结论
8. 可选附录与参考文献

具体任务允许合并、删减、重排或替换章节。用户给出的正文大纲优先于默认结构。

### 数据图与用户自定义图片

图片不是必需项。用户提供数据后，Agent 可以根据数据是否存在趋势、组间差异、分布特征、残差结构、敏感性或不确定性，决定是否生成任务相关的数据图，并把文件放入 `figures/`。

图片数量、类型、构图和插入位置由用户决定。示意图、照片、截图、仿真渲染图和其他自绘图片都可以通过默认图片宏加入：

```tex
\LabFigure[0.85]{figure-file.png}{图片说明}{fig:result}
```

需要自定义排版时，可以直接使用标准 LaTeX `figure` 环境和 `\includegraphics`。技能会保留用户自己的图片组织和版式意图。

### 支持的 Harness

技能支持 Codex、Claude Code、OpenCode、Hermes、Pi、Oh My Pi、DSH、ZCode 和 WorkBuddy。各 harness 的原生安装路径与项目级替代路径见 [HARNESSES.md](HARNESSES.md)。

### 环境要求

- 支持 Agent Skills 或兼容 `SKILL.md` 目录的 harness
- 已安装 TeX Live，并包含 `latexmk`、`pdflatex`、`pdftoppm`、`pdfinfo`
- PowerShell 7 或 Windows PowerShell

```powershell
latexmk -v
pdflatex -v
pdftoppm -v
pdfinfo -v
```

### 安装

```powershell
git clone <YOUR_REPOSITORY_URL> NUIST-lab-report-skill
Set-Location NUIST-lab-report-skill
.\install.ps1
```

安装器会询问目标 harness，并把姓名、学号、专业、学院和可选的自定义校徽写入本机 skill 目录。

```powershell
.\install.ps1 -Harness codex
.\install.ps1 -Harness codex,claude-code,opencode
.\install.ps1 -Harness all
.\install.ps1 -Harness all -DryRun
```

使用 `-TargetPath` 可以安装到其它兼容目录。目标已存在时必须配合 `-Force`，安装器会先创建带时间戳的备份。

### 创建报告

```powershell
.\scripts\new-lab-report.ps1 `
  -ProjectRoot (Get-Location).Path `
  -Course "课程名称" `
  -LabNumber "1" `
  -Title "报告题目"
```

脚本会读取本机个人资料并生成：

```text
reports/<报告目录>/
|-- main.tex
|-- figures/
|-- build/
|-- compile-report.ps1
|-- report.config.json
`-- README.md
```

`figures/` 可以为空。共享 LaTeX 样式保留在用户级 skill 中，由生成的编译入口加载，不复制到报告项目。

### 编译与验收

```powershell
.\compile-report.ps1 -AllowPending
.\compile-report.ps1
```

`-AllowPending` 用于生成未完成的脚手架预览。正式模式会拒绝残留的 `\LabPending{...}`、通过 `\LabFigure` 引用但不存在的图片、LaTeX 编译错误，以及 Overfull 或 Underfull 版面。编译完成后，每一页都会渲染到 `build/pages/`，并输出 PDF 页数。

### 隐私与本地资料

<a id="zh-privacy"></a>

共享仓库保留 NUIST 校名艺术字和校徽。学生字段与自定义校徽只写入安装者本机的 skill 目录：

```text
<installed-skill-root>/personal-profile.json
```

共享仓库不包含学生姓名、学号、个人联系方式、本机绝对路径或个人校徽文件。

### 目录结构

```text
NUIST-lab-report-skill/
|-- SKILL.md
|-- HARNESSES.md
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
|-- docs/
|   `-- preview-cover.png
|-- references/
|   `-- report-contract.md
`-- scripts/
    |-- new-lab-report.ps1
    `-- compile-report.ps1
```

### 许可证

MIT，详见 [LICENSE](LICENSE)。
