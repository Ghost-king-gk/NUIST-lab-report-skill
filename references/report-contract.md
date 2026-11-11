# Report outline and figure policy

## Stable core

The shared template provides two fixed elements: the LaTeX cover and a flexible body outline. Course-specific sections, project-specific content, image requirements, and a prescribed content sequence are not part of the template.

## Default outline

Adapt the order and depth to the task:

1. Abstract: task, method, principal result, conclusion.
2. Task and Objectives: question, requested deliverables, scope.
3. Background and Principles: concepts and formulas needed to understand the method.
4. Method and Implementation: apparatus, software, procedure, parameters, controls, and reproducibility details.
5. Results and Data Analysis: measurements or generated results, followed by their interpretation.
6. Discussion: mechanisms, boundary conditions, contradictions, and limitations.
7. Conclusion: accepted result, uncertainty, and remaining question.
8. Appendix and references: optional derivations, extended tables, code listings, and sources.

Users may add, remove, merge, or reorder sections. A user-provided outline takes precedence over this default.

## Data figures

Create a visualization when the available data make a relationship clearer than prose or a table. Useful targets include trends, comparisons, distributions, residuals, sensitivity, uncertainty, and parameter boundaries.

Use the user's data and preserve its scale, units, filtering, and provenance. Do not invent values, smooth over missing data, or imply a measurement that was not supplied. A table is preferable when exact values matter more than a visual pattern.

Figures are optional. The template does not require a fixed number, type, or sequence of images.

## User-supplied visuals

Accept custom diagrams, photographs, screenshots, rendered simulations, plots, and other image assets. Users decide which images to include, how many to use, and where they belong. Preserve their intended composition when it remains readable in the final PDF.

Use `\LabFigure` for the standard figure wrapper:

```tex
\LabFigure[0.85]{figure-file.png}{Caption text.}{fig:label}
```

For a custom layout, use a standard `figure` environment and `\includegraphics` directly. Both approaches are supported.

## Final checks

- The cover metadata matches the user's profile and report.
- The body follows the task requirements and any user-defined outline.
- No unintended `[PENDING:` markers remain.
- Every referenced image exists.
- No overfull or underfull boxes appear in the log.
- Every rendered page is visually inspected.
- Reported results and conclusions match the supplied data.
