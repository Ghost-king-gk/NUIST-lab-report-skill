# Report Content and Evidence Contract

## Stable core

The shared skill owns three stable elements:

1. the NUIST A4 cover;
2. the laboratory-report typography and heading hierarchy;
3. the evidence and final-delivery discipline.

The user or task controls section order, technical emphasis, figure selection, and optional appendix material.

## Default outline

Adapt this sequence to the actual assignment:

1. Abstract: question, setup, principal measured result, conclusion.
2. Introduction and scope: system boundary and claims under test.
3. Experimental environment and method: apparatus or software, variables, controls, procedure, parameters, and reproducibility.
4. Results: measurements before interpretation.
5. Discussion: mechanism, boundary conditions, conflicts, and limitations.
6. Conclusion: accepted result, uncertainty, and remaining discriminating test.
7. References and optional appendix: evidence, derivations, extended tables, code, or trace material.

A task-provided outline overrides the default.

## Evidence hierarchy

Prefer:

1. raw traces, run logs, measurements, screenshots, datasets, and configuration exports;
2. method records that establish the measurement conditions;
3. author-written summaries;
4. background material.

Never invent a missing measured value. If a required observation is unavailable and cannot be recovered in scope, use `[PENDING: ...]` during drafting and resolve it before final delivery.

## Results and figures

Use a table when several conditions share the same variables. Include units and the comparison basis in the heading or caption.

Generate a figure only when it adds a relationship that exact values do not expose quickly: trends, distributions, residuals, sensitivity, uncertainty, or mechanism.

Preserve user-provided visuals. Do not impose a fixed count, sequence, or chart style.

Every figure caption should state what was measured, under which condition, and what claim the visual supports.

## Final checks

- Cover metadata matches the profile and task.
- The body follows the task requirements and any user outline.
- No `[PENDING: ...]` markers remain.
- Every referenced image exists.
- Results and conclusions match supplied evidence.
- DOCX and PDF use the same `report.md`.
- No report-builder scripts or temporary render artifacts remain in the consuming project.
- Final DOCX and PDF pages are visually inspected.
