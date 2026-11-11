"""Create and build NUIST laboratory reports with one shared Markdown source."""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = SKILL_ROOT / "personal-profile.json"
LATEX_ROOT = SKILL_ROOT / "assets" / "latex" / "lab-report"
DEFAULT_WORDMARK = LATEX_ROOT / "assets" / "university_wordmark.png"
DEFAULT_SEAL = LATEX_ROOT / "assets" / "university_logo.jpeg"
MARKDOWN_IMAGE = re.compile(
    r"^!\[(?P<caption>.*?)\]\((?P<path>[^)]+)\)"
    r"(?:\{(?P<attrs>[^}]*)\})?\s*$"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile() -> dict[str, Any]:
    if not PROFILE_PATH.is_file():
        return {}
    return load_json(PROFILE_PATH)


def slugify(value: str, fallback: str = "report") -> str:
    slug = re.sub(r"[^\w.-]+", "_", value.strip(), flags=re.UNICODE).strip("._-")
    return slug or fallback


def english_date(value: date) -> str:
    months = (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
    return f"{value.day} {months[value.month - 1]} {value.year}"


def resolve_path(value: str, base: Path, fallback: Path) -> Path:
    if not value:
        return fallback
    path = Path(value)
    if not path.is_absolute():
        path = base / path
    return Path(os.path.abspath(path))


def cover_assets(config: dict[str, Any], report_dir: Path, profile: dict[str, Any]) -> tuple[Path, Path]:
    wordmark = resolve_path(
        str(config.get("wordmark_file", "")),
        report_dir,
        resolve_path(str(profile.get("wordmark_file", "")), SKILL_ROOT, DEFAULT_WORDMARK),
    )
    seal = resolve_path(
        str(config.get("seal_file", "")),
        report_dir,
        resolve_path(str(profile.get("seal_file", "")), SKILL_ROOT, DEFAULT_SEAL),
    )
    if not wordmark.is_file():
        raise FileNotFoundError(f"University wordmark not found: {wordmark}")
    if not seal.is_file():
        raise FileNotFoundError(f"University seal not found: {seal}")
    return wordmark, seal


def default_basename(config: dict[str, Any]) -> str:
    lab = str(config.get("lab_number", "")).strip()
    report_type = str(config.get("report_type", "Experimental Report")).strip()
    student = str(config.get("student", "")).strip()
    student_id = str(config.get("student_id", "")).strip()
    raw = "_".join(part for part in (f"Lab{lab}", report_type.replace(" ", "_"), student.replace(" ", "_"), student_id) if part)
    return slugify(raw, "Laboratory_Report")


def report_config_path(report_dir: Path) -> Path:
    return report_dir / "report.json"


def content_path(report_dir: Path, config: dict[str, Any]) -> Path:
    return Path(os.path.abspath(report_dir / str(config.get("content", "report.md"))))


def command(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    if os.name == "nt" and name == "soffice":
        candidates = (
            Path(r"C:\Program Files\LibreOffice\program\soffice.exe"),
            Path(r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"),
        )
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
    return None


@contextmanager
def scratch_directory(prefix: str, parent: Path):
    base = Path(tempfile.gettempdir())
    probe = base / f".lab-report-probe-{os.getpid()}-{secrets.token_hex(3)}"
    try:
        probe.mkdir()
        (probe / "write-test").write_text("x", encoding="utf-8")
        (probe / "write-test").unlink()
        probe.rmdir()
    except OSError:
        shutil.rmtree(probe, ignore_errors=True)
        base = parent
    path = base / f"{prefix}{os.getpid()}-{secrets.token_hex(4)}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def build_content_template(config: dict[str, Any]) -> str:
    title = config.get("title", "Report Title")
    return f"""# Abstract

[PENDING: State the question, method, principal measured result, and conclusion.]

# 1 Introduction and Scope

Define the system under test, the experimental question, and the claims this report will support.

# 2 Experimental Environment and Method

Record the apparatus or software, variables, controls, procedure, parameters, and reproducibility details.

# 3 Results

Present the observations before interpretation. Use tables for exact values and figures for relationships that are easier to inspect visually.

# 4 Discussion

Connect each result to the mechanism under test. State the boundary conditions that decide the engineering or scientific choice.

# 5 Conclusion

[PENDING: State the accepted result and the remaining question for {title}.]

# References

[1] Course laboratory deck or task sheet.
"""


def create_report(args: argparse.Namespace) -> None:
    profile = load_profile()
    project_root = Path(os.path.abspath(args.project_root))
    if not project_root.is_dir():
        raise NotADirectoryError(f"Project root not found: {project_root}")

    student = args.student or str(profile.get("student_name", ""))
    student_id = args.student_id or str(profile.get("student_id", ""))
    major = args.major or str(profile.get("major", ""))
    college = args.college or str(profile.get("college", ""))
    if not student or not student_id:
        raise ValueError(
            "Student name and ID are required. Run install.ps1/install.sh or pass "
            "--student and --student-id."
        )

    directory_name = args.directory_name or slugify(f"Lab{args.lab_number}_{args.title}", "report")
    report_dir = project_root / "reports" / directory_name
    if report_dir.exists():
        raise FileExistsError(f"Report directory already exists: {report_dir}")
    (report_dir / "figures").mkdir(parents=True)
    (report_dir / "output").mkdir()

    format_map = {"docx": ["docx"], "pdf": ["pdf"], "both": ["docx", "pdf"]}
    config: dict[str, Any] = {
        "course": args.course,
        "course_short": args.course_short or args.course,
        "report_type": args.report_type,
        "lab_number": args.lab_number,
        "title": args.title,
        "student": student,
        "student_id": student_id,
        "major": major,
        "college": college,
        "date": args.date or english_date(date.today()),
        "content": "report.md",
        "output_dir": "output",
        "output_basename": args.output_basename or default_basename(
            {
                "lab_number": args.lab_number,
                "report_type": args.report_type,
                "student": student,
                "student_id": student_id,
            }
        ),
        "output_formats": format_map[args.format],
    }
    (report_dir_path := report_config_path(report_dir)).write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (report_dir / "report.md").write_text(build_content_template(config), encoding="utf-8")
    (report_dir / "README.md").write_text(
        f"""# {args.title}

Course: {args.course}

This report uses `report.md` as the single content source and `report.json` for cover metadata. The installed `lab-report` skill builds the final DOCX and optional PDF; no report-generator script belongs in this project.

## Build

Windows PowerShell:

```powershell
python <installed-skill>/scripts/report_tool.py build --report-dir . --formats docx,pdf
```

Linux or WSL:

```bash
python3 <installed-skill>/scripts/report_tool.py build --report-dir . --formats docx,pdf
```

## Layout

- `report.md`: report content
- `report.json`: cover metadata and output settings
- `figures/`: optional report images
- `output/`: final DOCX and PDF files
""",
        encoding="utf-8",
    )
    print(report_dir)


def validate_config(config: dict[str, Any]) -> None:
    required = ("course", "lab_number", "title", "student", "student_id")
    missing = [key for key in required if not str(config.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Missing report metadata: {', '.join(missing)}")
    if "[PENDING:" in json.dumps(config):
        raise ValueError("Report metadata contains a pending marker.")


def _tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def _latex_width(attributes: str) -> str:
    for item in attributes.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        if key.strip() != "width":
            continue
        value = value.strip().lower()
        if value.endswith("%"):
            fraction = float(value[:-1]) / 100.0
            return f"{fraction:.3f}\\linewidth"
        if value.endswith(("in", "cm", "mm")):
            return value
    return r"0.88\linewidth"


def markdown_for_latex(text: str) -> str:
    output: list[str] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.strip() == "::pagebreak":
            output.extend((r"\newpage{}", ""))
            continue
        image = MARKDOWN_IMAGE.match(line.strip())
        if image:
            caption = _tex_escape(image.group("caption").strip())
            path = image.group("path").strip().replace("\\", "/")
            width = _latex_width(image.group("attrs") or "")
            output.extend(
                (
                    r"\begin{center}",
                    rf"\includegraphics[width={width},height=0.34\textheight,keepaspectratio]{{\detokenize{{{path}}}}}",
                    r"\end{center}",
                    rf"\captionof{{figure}}{{{caption}}}",
                    "",
                )
            )
            continue
        output.append(line)
    return "\n".join(output)


def build_pdf_latex(
    report_dir: Path,
    config: dict[str, Any],
    content: Path,
    output_pdf: Path,
    assets: tuple[Path, Path],
    *,
    allow_pending: bool,
) -> int:
    pandoc = command("pandoc")
    latexmk = command("latexmk")
    if not pandoc:
        raise RuntimeError("Pandoc is required for the LaTeX PDF backend.")
    if not latexmk:
        raise RuntimeError("latexmk is required for the LaTeX PDF backend.")
    template_path = LATEX_ROOT / "report-wrapper.tex"
    if not template_path.is_file():
        raise FileNotFoundError(f"LaTeX wrapper template not found: {template_path}")

    with scratch_directory(".lab-report-build-", report_dir) as temp_dir:
        body_path = temp_dir / "body.tex"
        markdown = content.read_text(encoding="utf-8")
        if "[PENDING:" in markdown and not allow_pending:
            raise ValueError("Report content still contains [PENDING: ...] markers.")
        markdown = markdown_for_latex(markdown)
        pandoc_input = temp_dir / "content.md"
        pandoc_input.write_text(markdown, encoding="utf-8")
        subprocess.run(
            [
                pandoc,
                str(pandoc_input),
                "--from",
                "markdown+pipe_tables+link_attributes",
                "--to",
                "latex",
                "--syntax-highlighting=none",
                "--output",
                str(body_path),
                "--resource-path",
                str(report_dir),
            ],
            check=True,
            cwd=report_dir,
        )

        wordmark, seal = assets
        wrapper = template_path.read_text(encoding="utf-8")
        replacements = {
            "@@COURSE@@": _tex_escape(config.get("course", "")),
            "@@COURSESHORT@@": _tex_escape(config.get("course_short", config.get("course", ""))),
            "@@REPORTTYPE@@": _tex_escape(config.get("report_type", "Experimental Report")),
            "@@LABNUMBER@@": _tex_escape(config.get("lab_number", "")),
            "@@TITLE@@": _tex_escape(config.get("title", "")),
            "@@STUDENT@@": _tex_escape(config.get("student", "")),
            "@@STUDENTID@@": _tex_escape(config.get("student_id", "")),
            "@@MAJOR@@": _tex_escape(config.get("major", "")),
            "@@COLLEGE@@": _tex_escape(config.get("college", "")),
            "@@DATE@@": _tex_escape(config.get("date", "")),
            "@@HEADERLEFT@@": _tex_escape(config.get("course_short", config.get("course", ""))),
            "@@HEADERRIGHT@@": _tex_escape(
                config.get(
                    "header_right",
                    f"Lab {config.get('lab_number', '')} | {config.get('report_type', 'Experimental Report')}",
                )
            ),
            "@@WORDMARK@@": wordmark.as_posix(),
            "@@SEAL@@": seal.as_posix(),
            "@@REPORTDIR@@": report_dir.as_posix(),
        }
        for key, value in replacements.items():
            wrapper = wrapper.replace(key, value)
        main_path = temp_dir / "main.tex"
        main_path.write_text(wrapper, encoding="utf-8")

        environment = os.environ.copy()
        old_texinputs = environment.get("TEXINPUTS", "")
        environment["TEXINPUTS"] = os.pathsep.join(
            [str(LATEX_ROOT), str(report_dir), old_texinputs]
        )
        result = subprocess.run(
            [
                latexmk,
                "-pdf",
                "-interaction=nonstopmode",
                "-halt-on-error",
                main_path.name,
            ],
            cwd=temp_dir,
            env=environment,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()[-4000:]
            raise RuntimeError(f"latexmk failed with exit code {result.returncode}: {detail}")

        log_path = temp_dir / "main.log"
        if log_path.is_file():
            layout = re.findall(r"(?:Overfull|Underfull).*", log_path.read_text(encoding="utf-8", errors="replace"))
            if layout:
                raise RuntimeError("LaTeX layout warnings: " + " | ".join(layout[:5]))
        built_pdf = temp_dir / "main.pdf"
        if not built_pdf.is_file():
            raise FileNotFoundError("latexmk completed without producing a PDF.")
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built_pdf, output_pdf)
    return pdf_page_count(output_pdf)


def convert_with_office(docx_path: Path, output_pdf: Path) -> int:
    soffice = command("soffice")
    if not soffice:
        raise RuntimeError("LibreOffice was not found. Install LibreOffice or use a LaTeX PDF backend.")
    with scratch_directory(".lab-report-office-", docx_path.parent) as temp_dir:
        profile_dir = temp_dir / "profile"
        profile_dir.mkdir()
        result = subprocess.run(
            [
                soffice,
                "--headless",
                f"-env:UserInstallation={(profile_dir / 'user').resolve().as_uri()}",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp_dir),
                str(docx_path),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        built_pdf = temp_dir / f"{docx_path.stem}.pdf"
        if result.returncode != 0 or not built_pdf.is_file():
            message = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"LibreOffice PDF export failed: {message}")
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built_pdf, output_pdf)
    return pdf_page_count(output_pdf)


def pdf_page_count(path: Path) -> int:
    pdfinfo = command("pdfinfo")
    if not pdfinfo:
        return 0
    result = subprocess.run([pdfinfo, str(path)], check=False, capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def build_report(args: argparse.Namespace) -> None:
    from lab_report_docx import build_docx

    report_dir = Path(os.path.abspath(args.report_dir))
    config = load_json(report_config_path(report_dir))
    validate_config(config)
    profile = load_profile()
    assets = cover_assets(config, report_dir, profile)
    content = content_path(report_dir, config)
    if not content.is_file():
        raise FileNotFoundError(f"Report Markdown not found: {content}")
    output_dir = Path(os.path.abspath(report_dir / str(config.get("output_dir", "output"))))
    output_dir.mkdir(parents=True, exist_ok=True)
    basename = str(config.get("output_basename") or default_basename(config))
    formats = args.formats or ",".join(config.get("output_formats", ["docx"]))
    requested = {"docx", "pdf"} if formats.strip().lower() == "both" else {
        item.strip().lower() for item in formats.split(",") if item.strip()
    }
    unknown = requested - {"docx", "pdf"}
    if unknown:
        raise ValueError(f"Unsupported output formats: {', '.join(sorted(unknown))}")

    docx_path = output_dir / f"{basename}.docx"
    pdf_path = output_dir / f"{basename}.pdf"
    stats: dict[str, int] = {}
    if "docx" in requested:
        stats = build_docx(
            report_dir,
            config,
            content,
            docx_path,
            assets,
            allow_pending=args.allow_pending,
        )

    if "pdf" in requested:
        backend = args.pdf_backend
        if backend == "auto":
            backend = "office" if command("soffice") else "latex"
        if backend == "office":
            source_docx = docx_path
            if "docx" not in requested:
                with scratch_directory(".lab-report-docx-", output_dir) as temp_dir:
                    temp_docx = temp_dir / f"{basename}.docx"
                    build_docx(
                        report_dir,
                        config,
                        content,
                        temp_docx,
                        assets,
                        allow_pending=args.allow_pending,
                    )
                    pages = convert_with_office(temp_docx, pdf_path)
            else:
                pages = convert_with_office(source_docx, pdf_path)
        elif backend == "latex":
            pages = build_pdf_latex(
                report_dir,
                config,
                content,
                pdf_path,
                assets,
                allow_pending=args.allow_pending,
            )
        else:
            raise ValueError(f"Unsupported PDF backend: {backend}")
        print(f"PDF: {pdf_path} ({pages or 'unknown'} pages)")

    if "docx" in requested:
        print(f"DOCX: {docx_path}")
        print(f"Images: {stats.get('images', 0)}; tables: {stats.get('tables', 0)}")


def doctor() -> None:
    try:
        from importlib.metadata import version

        docx_status = f"python-docx {version('python-docx')}"
    except Exception as error:
        docx_status = f"missing ({error})"
    print(f"Skill root: {SKILL_ROOT}")
    print(f"python-docx: {docx_status}")
    for name in ("pandoc", "latexmk", "soffice", "pdftoppm", "pdfinfo"):
        location = command(name)
        print(f"{name}: {location or 'not found'}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Create and build NUIST laboratory reports.")
    commands = root.add_subparsers(dest="command", required=True)

    create = commands.add_parser("new", help="Create a report workspace.")
    create.add_argument("--project-root", default=".")
    create.add_argument("--course", required=True)
    create.add_argument("--lab-number", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--report-type", default="Experimental Report")
    create.add_argument("--student", default="")
    create.add_argument("--student-id", default="")
    create.add_argument("--major", default="")
    create.add_argument("--college", default="")
    create.add_argument("--course-short", default="")
    create.add_argument("--date", default="")
    create.add_argument("--directory-name", default="")
    create.add_argument("--output-basename", default="")
    create.add_argument("--format", choices=("docx", "pdf", "both"), default="docx")
    create.set_defaults(func=create_report)

    build = commands.add_parser("build", help="Build final report files.")
    build.add_argument("--report-dir", default=".")
    build.add_argument("--formats", default="", help="docx, pdf, both, or a comma-separated list")
    build.add_argument("--pdf-backend", choices=("auto", "office", "latex"), default="auto")
    build.add_argument("--allow-pending", action="store_true")
    build.set_defaults(func=build_report)

    check = commands.add_parser("doctor", help="Show available build dependencies.")
    check.set_defaults(func=lambda _args: doctor())
    return root


def main() -> None:
    args = parser().parse_args()
    try:
        args.func(args)
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()

