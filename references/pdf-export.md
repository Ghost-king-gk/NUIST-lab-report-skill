# PDF Export

PDF uses the same `report.md` and `report.json` as DOCX.

## Backends

### Office export

Use `--pdf-backend office` when LibreOffice is available and the PDF must match the DOCX. The tool creates a temporary DOCX, exports PDF, and removes the temporary files.

### Native LaTeX

Use `--pdf-backend latex` when:

- LibreOffice is unavailable;
- TeX-native equations are required;
- the user explicitly asks for LaTeX source or a TeX-built PDF.

The tool converts the Markdown body with Pandoc, applies the shared `labreport.sty` cover and layout, compiles in a temporary directory, and copies only the final PDF to `output/`.

### Automatic selection

`--pdf-backend auto` prefers LibreOffice and falls back to LaTeX.

## Required tools

Office backend:

- LibreOffice `soffice`

LaTeX backend:

- `pandoc`
- `latexmk`
- TeX Live packages already required by `labreport.sty`

Rendering QA:

- `pdfinfo`
- `pdftoppm`

Run:

```powershell
python <skill-root>/scripts/report_tool.py doctor
```

## Final checks

- Compile succeeds without overfull or underfull layout warnings.
- Every page is rendered and inspected.
- Cover metadata matches the DOCX.
- Headings and figures are not duplicated by cross-format numbering.
- No TeX, Pandoc, or PDF-conversion intermediates remain in the report project.

