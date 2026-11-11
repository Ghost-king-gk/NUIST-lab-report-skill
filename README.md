# NUIST Lab Report Agent Skill

<p align="center">
  <a href="#english">English</a> ·
  <a href="#zh-cn">简体中文</a> ·
  <a href="HARNESSES.md">Harness paths</a> ·
  <a href="#installation">Install</a>
</p>

<p align="center">
  <img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-compatible-2ea44f">
  <img alt="DOCX and PDF" src="https://img.shields.io/badge/output-DOCX%20%2B%20PDF-1f4e79">
  <img alt="Harnesses" src="https://img.shields.io/badge/harnesses-9-6f42c1">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue">
</p>

A portable Agent Skill for producing university laboratory reports with a fixed NUIST A4 cover, a flexible experiment structure, optional figures, and an editable DOCX. PDF is generated from the same report source when required.

面向高校实验报告的可移植 Agent Skill：固定 NUIST A4 封面与报告版式，灵活组织实验内容、结果表和可选图片，默认输出可编辑 DOCX，并从同一内容源生成 PDF。

![Laboratory report cover preview](docs/preview-cover.png)

---

<a id="english"></a>

## English

### Why one skill

DOCX and PDF belong in one `lab-report` skill. Both outputs share the same cover metadata, A4 geometry, section hierarchy, evidence rules, tables, figures, captions, and report content. Two separate skills would duplicate those rules and allow the Word and PDF versions to diverge.

The skill separates the format into build modes:

- `docx`: editable and layout-authoritative deliverable;
- `pdf`: review or submission copy generated from the same `report.md`;
- `docx,pdf`: both deliverables.

### Shared-source workflow

```text
reports/<report>/
|-- README.md
|-- report.json       cover metadata and output settings
|-- report.md         single report content source
|-- figures/          optional report images
`-- output/           final DOCX and PDF
```

The consuming project does not receive the report builder, compiler wrapper, extracted slides, page renders, caches, or failed build artifacts. Those stay in the skill or a disposable build location.

### Components

| Component | Purpose |
|---|---|
| `SKILL.md` | Portable report workflow and format decision |
| `scripts/report_tool.py` | Scaffold, DOCX build, PDF export, and dependency check |
| `scripts/lab_report_docx.py` | Shared cover and Markdown-to-DOCX renderer |
| `scripts/new-lab-report.sh` / `compile-report.sh` | Bash entry points for Linux and WSL |
| `scripts/new-lab-report.ps1` / `compile-report.ps1` | PowerShell entry points for Windows |
| `references/report-source.md` | Supported Markdown syntax |
| `references/docx-format.md` | DOCX layout and acceptance checks |
| `references/pdf-export.md` | Office and LaTeX PDF backends |
| `references/report-contract.md` | Evidence structure and final checks |
| `assets/latex/lab-report/` | Shared cover, LaTeX style, and native PDF wrapper |

### Requirements

- Python 3.10 or newer
- Bash 4 or newer for Linux and WSL entry points
- `python-docx` for DOCX generation
- Optional PDF backend:
  - LibreOffice for DOCX-to-PDF export;
  - or Pandoc plus TeX Live for native LaTeX PDF.
- `pdfinfo` and `pdftoppm` for final PDF verification when available

```powershell
python <skill-root>/scripts/report_tool.py doctor
```

### Linux and WSL

Use `python3` and the Bash entry points in Linux or WSL. Install `python-docx` in the active Python environment:

```bash
python3 -m pip install --user python-docx
python3 <skill-root>/scripts/report_tool.py doctor
```

On Debian or Ubuntu, install `python3-pip` and `python3-venv` first when those modules are missing:

```bash
sudo apt install python3-pip python3-venv
```

If the system Python is externally managed, use a temporary virtual environment:

```bash
python3 -m venv .venv-lab-report
. .venv-lab-report/bin/activate
python -m pip install python-docx
```

The Bash installer uses the same harness paths as the PowerShell installer:

```bash
bash install.sh --harness codex
bash install.sh --harness codex,claude-code,opencode
bash install.sh --harness all --dry-run
bash install.sh --harness all
```

For a non-interactive WSL installation, pass the profile fields explicitly. Windows drive paths are translated by `wslpath`:

```bash
bash install.sh \
  --harness codex \
  --student-name "Sample Student" \
  --student-id 000000000000 \
  --major "Sample Major" \
  --college "Sample College"
```

Create and build with the same commands:

```bash
bash <skill-root>/scripts/new-lab-report.sh \
  --project-root . \
  --course "Course Name" \
  --lab-number "1" \
  --title "Report Title" \
  --format both

bash <skill-root>/scripts/compile-report.sh \
  --report-dir ./reports/<report> \
  --formats docx,pdf
```

The wrappers use `python3` by default. Set `PYTHON=python` when the active interpreter has a different executable name.

WSL projects stored under `/mnt/<drive>/...` work in place. Keep the skill and report directories on the Linux filesystem when possible; use `/mnt/...` only when the project must remain on the Windows drive.

### Installation

<a id="installation"></a>

```powershell
git clone <YOUR_REPOSITORY_URL> NUIST-lab-report-skill
Set-Location NUIST-lab-report-skill
.\install.ps1
```

The installer writes the student profile and optional branding into the selected local skill directories. The shared repository contains no personal profile.

```powershell
.\install.ps1 -Harness codex
.\install.ps1 -Harness codex,claude-code,opencode
.\install.ps1 -Harness all -DryRun
```

Linux and WSL use the equivalent Bash installer:

```bash
bash install.sh --harness codex
bash install.sh --harness all --dry-run
```

### Create a report

```powershell
python .\scripts\report_tool.py new `
  --project-root . `
  --course "Course Name" `
  --lab-number "1" `
  --title "Report Title" `
  --format both
```

The scaffold loads the installed personal profile for student name, ID, major, and college.

### Build

```powershell
python <skill-root>/scripts/report_tool.py build `
  --report-dir .\reports\<report> `
  --formats docx,pdf
```

Linux and WSL can call the Bash wrapper:

```bash
bash <skill-root>/scripts/compile-report.sh \
  --report-dir ./reports/<report> \
  --formats docx,pdf
```

PDF backends:

```powershell
--pdf-backend auto    # LibreOffice first, LaTeX fallback
--pdf-backend office  # match the DOCX
--pdf-backend latex   # native TeX PDF
```

Final mode rejects unresolved `[PENDING: ...]` markers. Generated DOCX files include alternative text for images, repeating table headers, the standard A4 cover, and page numbering.

### Authority rule

When the generic `documents` skill is also available, it may be used for rendering, OOXML repair, comments, or accessibility checks. It must not replace the NUIST cover, A4 geometry, typography, or report structure defined here.

---

<a id="zh-cn"></a>

## 简体中文

### 为什么合成一个 skill

DOCX 与 PDF 应保留在同一个 `lab-report` skill 中。两种输出共享封面元数据、A4 版式、章节层级、证据规则、表格、图片、图注和正文内容。拆成两个 skill 会重复维护这些约束，并使 Word 与 PDF 容易产生内容漂移。

输出模式分别为：

- `docx`：默认可编辑交付，也是版式基准；
- `pdf`：从同一份 `report.md` 生成；
- `docx,pdf`：同时输出两种格式。

### 单一内容源

```text
reports/<报告目录>/
|-- README.md
|-- report.json       封面元数据与输出设置
|-- report.md         唯一报告正文源
|-- figures/          可选图片
`-- output/           最终 DOCX 与 PDF
```

实验项目不包含报告生成器、编译包装脚本、解压课件、逐页图片、缓存或失败构建文件。生成逻辑保留在本 skill 内，中间文件进入可清理的临时位置。

### 核心组件

| 组件 | 作用 |
|---|---|
| `SKILL.md` | 可移植报告流程与格式选择 |
| `scripts/report_tool.py` | 创建项目、构建 DOCX/PDF、检查依赖 |
| `scripts/lab_report_docx.py` | 统一封面与 Markdown-to-DOCX 渲染 |
| `scripts/new-lab-report.sh` / `compile-report.sh` | Linux 与 WSL 的 Bash 入口 |
| `scripts/new-lab-report.ps1` / `compile-report.ps1` | Windows 的 PowerShell 入口 |
| `references/report-source.md` | Markdown 语法与图片、表格、公式约定 |
| `references/docx-format.md` | DOCX 版式与验收 |
| `references/pdf-export.md` | Office 与 LaTeX PDF 后端 |
| `references/report-contract.md` | 证据结构与最终检查 |
| `assets/latex/lab-report/` | 共享封面、LaTeX 样式和原生 PDF 包装模板 |

### 环境要求

- Python 3.10 或更高版本
- Linux 与 WSL 入口需要 Bash 4 或更高版本
- DOCX 生成需要 `python-docx`
- PDF 后端任选其一：
  - LibreOffice；或
  - Pandoc 与 TeX Live
- 建议安装 `pdfinfo`、`pdftoppm`，用于最终 PDF 检查

```powershell
python <skill-root>/scripts/report_tool.py doctor
```

### Linux 与 WSL

在 Linux 或 WSL 中使用 `python3` 和 Bash 入口。先为当前 Python 环境安装 `python-docx`：

```bash
python3 -m pip install --user python-docx
python3 <skill-root>/scripts/report_tool.py doctor
```

Debian/Ubuntu 缺少 `pip` 或 `venv` 时先安装：

```bash
sudo apt install python3-pip python3-venv
```

如果系统 Python 启用了 externally managed 限制，使用临时虚拟环境：

```bash
python3 -m venv .venv-lab-report
. .venv-lab-report/bin/activate
python -m pip install python-docx
```

Bash 安装器使用与 PowerShell 安装器相同的 harness 路径：

```bash
bash install.sh --harness codex
bash install.sh --harness codex,claude-code,opencode
bash install.sh --harness all --dry-run
bash install.sh --harness all
```

WSL 中可以直接传入个人资料，避免交互输入；Windows 路径会通过 `wslpath` 转换：

```bash
bash install.sh \
  --harness codex \
  --student-name "张三" \
  --student-id 000000000000 \
  --major "专业名称" \
  --college "学院名称"
```

创建和构建命令如下：

```bash
bash <skill-root>/scripts/new-lab-report.sh \
  --project-root . \
  --course "课程名称" \
  --lab-number "1" \
  --title "报告题目" \
  --format both

bash <skill-root>/scripts/compile-report.sh \
  --report-dir ./reports/<报告目录> \
  --formats docx,pdf
```

包装器默认使用 `python3`。如果当前解释器名称不同，设置 `PYTHON=python`。

位于 `/mnt/<盘符>/...` 的 WSL 项目可以原地使用。项目不需要迁移到 Linux 文件系统；如果构建速度或权限成为问题，再把项目复制到 `$HOME` 下的工作目录。

### 安装

```powershell
git clone <YOUR_REPOSITORY_URL> NUIST-lab-report-skill
Set-Location NUIST-lab-report-skill
.\install.ps1
```

安装器会把学生资料和可选校徽写入本机目标 skill 目录，共享仓库不包含 `personal-profile.json`。

Linux 和 WSL 使用 Bash 安装器：

```bash
bash install.sh --harness codex
bash install.sh --harness all --dry-run
bash install.sh --harness all
```

### 创建与构建

```powershell
python .\scripts\report_tool.py new `
  --project-root . `
  --course "课程名称" `
  --lab-number "1" `
  --title "报告题目" `
  --format both
```

```powershell
python <skill-root>/scripts/report_tool.py build `
  --report-dir .\reports\<报告目录> `
  --formats docx,pdf
```

Linux 和 WSL 的等价命令：

```bash
bash <skill-root>/scripts/compile-report.sh \
  --report-dir ./reports/<报告目录> \
  --formats docx,pdf
```

正式构建会拒绝残留的 `[PENDING: ...]`。DOCX 默认包含 A4 封面、页码、图片替代文本、重复表头和统一标题层级。

### 版式优先级

同时安装通用 `documents` skill 时，后者只能用于渲染、OOXML 修复、批注或无障碍检查，不能用其 Letter 纸张、通用封面或样式预设覆盖本 skill 的 NUIST 封面与报告结构。

### 许可证

MIT，详见 [LICENSE](LICENSE)。
