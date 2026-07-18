# Paper Figures

This folder contains paper-facing figure copies used for quick visual inspection
of the CRAST artifact.

The numeric values behind the figures are available in the CSV result tables
under `results/tables/`.

## Files

| File | Purpose |
|---|---|
| `figure_01_confusion_matrix_npm_to_pypi.png` | Confusion matrix for the final NPM→PyPI CRAST transfer evaluation. |
| `figure_02_confusion_matrix_pypi_to_npm.png` | Confusion matrix for the final PyPI→NPM CRAST transfer evaluation. |
| `figure_03_final_cross_registry_performance.png` | Visual summary of final cross-registry transfer performance. |

## Related Files

The machine-readable result values are stored under:

```text
results/tables/table_04_crast_final_transfer_summary.csv
results/tables/table_05_cross_registry_confusion_matrices.csv
```

Reviewer-friendly copies of the same figures are also available under:

```text
results/figures/
```

The `Figures/` folder is kept for paper-style artifact navigation, while
`results/figures/` keeps the figures grouped with the rest of the generated
result artifacts.
