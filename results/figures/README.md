# Result Figures

This folder contains reviewer-friendly copies of the main figures generated from
the CRAST experiments.

The figures summarize key visual results from the paper, such as final
cross-registry confusion matrices and final transfer-performance comparisons.

## Files

| File | Purpose |
|---|---|
| `figure_01_confusion_matrix_npm_to_pypi.png` | Confusion matrix for the final NPM→PyPI CRAST transfer evaluation. |
| `figure_02_confusion_matrix_pypi_to_npm.png` | Confusion matrix for the final PyPI→NPM CRAST transfer evaluation. |
| `figure_03_final_cross_registry_performance.png` | Visual comparison of final cross-registry transfer performance. |

## Note

The numeric values behind these figures are available in:

```text
results/tables/table_04_crast_final_transfer_summary.csv
results/tables/table_05_cross_registry_confusion_matrices.csv
```

The figures are included for quick inspection, while the CSV tables provide the
machine-readable result values used in the manuscript.
