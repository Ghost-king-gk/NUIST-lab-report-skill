# Laboratory report contract

## Evidence hierarchy

Prefer raw observations over summaries:

1. Primary measurements, logs, screenshots, traces, datasets, and configuration exports.
2. Method and apparatus records that establish the measurement conditions.
3. Author-written summaries and discussion.
4. Generic background material.

Do not fabricate a missing observation. Leave a visible `\LabPending{...}` marker or state the unresolved variable.

## Standard structure

Adapt section names to the discipline while preserving this argument chain:

1. Abstract: question, setup, measured result, conclusion.
2. Introduction and scope: question, system boundary, claims under test.
3. Environment and method: equipment, software, variables, controls, procedure, reproducibility details.
4. Results: measurements before interpretation.
5. Discussion: mechanism, boundary conditions, contradictions, limitations.
6. Conclusion: accepted result, uncertainty, next discriminating test.
7. Appendix: command summaries, evidence manifests, derivations, or extended tables.

## Evidence placement

```text
evidence/   raw captures and machine-readable exports
figures/    curated, captioned images inserted into main.tex
build/      generated PDFs, logs, auxiliaries, and page renders
```

Keep filenames stable and descriptive. Figure captions should state what was measured, under which condition, and what claim the visual supports.

## Results tables

Use a table when several conditions share the same variables. Include the measured value, condition, and comparison or boundary. For binary network tests, record sent, received, and loss rate rather than only “success” or “failure.”

## Final acceptance

- The PDF compiles without errors.
- No unintended `[PENDING:` markers remain.
- Every referenced evidence image exists.
- No overfull or underfull boxes appear in the log.
- Every page is visually inspected after rendering to PNG.
- Claims match the actual evidence and distinguish causal evidence from mechanistic hypothesis.
