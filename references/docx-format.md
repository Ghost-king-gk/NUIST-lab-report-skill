# DOCX Format and Validation

## Shared cover

The DOCX backend must preserve the NUIST A4 cover:

- 3.35 in university wordmark;
- centered black 24 pt `Experimental Report`;
- 1.10 in university seal;
- right-aligned labels and underlined values for Course, Project, Student, Student ID, Major, and College;
- bold 18 pt date at the bottom.

Do not apply Letter paper, a generic title cover, or the `documents` skill's alternate design preset.

## Body

- A4, 25 mm margins.
- Times New Roman body at 10.5 pt.
- Arial headings in `#1F4E79`.
- Running header with course short name on the left and `Lab <number> | Experimental Report` on the right.
- Centered page number in the footer.
- Tables use navy headers, white header text, light-gray borders, alternating body shading, and repeated header rows.
- Code uses a monospaced 7.4 pt style.

## Build

```powershell
python <skill-root>/scripts/report_tool.py build `
  --report-dir <report-dir> `
  --formats docx
```

The builder writes only the final DOCX under `output/`.

## Acceptance checks

- Cover fields are complete and read from the current profile.
- All images have alternative text.
- Tables have repeating header rows.
- No unresolved pending markers remain.
- Headings are not orphaned at page bottoms.
- Tables, code blocks, and figures do not clip or overlap.
- Final project contains no build scripts or DOCX construction code.

If the `documents` skill is available, use its renderer and accessibility audit after the build. Its generic design rules do not override this skill's cover or page geometry.

