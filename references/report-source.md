# Report Markdown Source

`report.md` is the single content source for DOCX and PDF.

## Supported blocks

### Headings

Use `##` for subsections and `###` for third-level headings. Keep numbering in the heading text when the report needs explicit numbers:

```markdown
# 3 Results
## 3.1 Measured waiting times
### Queue operation counts
```

The DOCX and PDF backends preserve the heading text without adding a second numbering layer.

### Paragraphs and inline formatting

Use blank lines between paragraphs. Supported inline formatting:

- `**bold**`
- `*italic*`
- `` `code` ``
- `[link text](https://example.com)`

### Lists

```markdown
- first item
- second item

1. first step
2. second step
```

### Tables

Place an optional caption line immediately before the table:

```markdown
Table: Queue operations at each measured size.

| Players | Operations | Median time |
|---:|---:|---:|
| 250 | 2,990 | 0.81 ms |
| 16,000 | 191,990 | 31.21 ms |
```

The first row is the header. DOCX tables use a dark-blue header, light-gray borders, alternating body shading, and a repeating header row.

### Figures

```markdown
![Waiting-time distribution](figures/waiting_time.png){width=85%}
```

The caption is the image alt text. Supported width units are `%`, `in`, `cm`, and `mm`. Use a relative path under `figures/`.

### Code

````markdown
```python
def service_time(pages, rate):
    return pages * 60 / rate
```
````

### Equations

Use display math for formulas:

```markdown
$$
W_q = \lambda [E(S^2)-E(S)] / [2(1-\rho)]
$$
```

DOCX preserves the formula as centered mathematical text. The LaTeX PDF backend preserves the native equation.

### Page control

Insert:

```markdown
::pagebreak
```

to start appendix material or a large evidence section on a new page.

## Pending markers

Draft incomplete claims as:

```text
[PENDING: replace with measured value and condition]
```

Final builds reject unresolved markers.

