# Manuscript Figures

This folder contains only the figures included in the CRAST manuscript:

**Unifying SysCall Behavior Across PyPI and NPM Registries for Malicious Package Detection**

The figures are provided in PDF format for manuscript submission and artifact
inspection.

## Figure Files

| File | Manuscript Figure | Description |
|---|---|---|
| `figure_01_threat_model.pdf` | Figure 1 | CRAST threat model and cross-registry observation setting. |
| `figure_02_crast_framework.pdf` | Figure 2 | Overall CRAST framework for SysCall-based malicious package detection across NPM and PyPI. |
| `figure_03_execution_environment.pdf` | Figure 3 | Controlled execution and tracing environment used for install-time SysCall collection. |
| `figure_04_confusion_matrices_npm_to_pypi.pdf` | Figure 4(a) | Confusion matrix for the best NPM→PyPI CRAST transfer configuration. |
| `figure_05_confusion_matrices_pypi_to_npm.pdf` | Figure 4(b) | Confusion matrix for the best PyPI→NPM CRAST transfer configuration. |

## Notes

Figures 1–3 are conceptual manuscript diagrams.

The confusion-matrix panels are based on the final CRAST transfer results
reported in:

```text
results/tables/table_05_cross_registry_confusion_matrices.csv
```

The confusion-matrix values correspond to the two final direction-specific CRAST
configurations:

```text
NPM → PyPI: Top-5 percentile-rank fusion
PyPI → NPM: Extra Trees with mean/std score alignment
```

Although the two confusion-matrix panels are stored as separate PDF files in
this artifact, they correspond to the two panels of the same manuscript figure.

This folder intentionally excludes exploratory, intermediate, or unused figures
that are not included in the manuscript.
