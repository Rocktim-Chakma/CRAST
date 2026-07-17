# Reusable Data Utilities

This folder contains reusable utilities for building and validating CRAST feature
matrices after feature extraction.

These scripts support the dataset-building workflow used in Phase 3.

## Files

| File | Purpose |
|---|---|
| `merge_class_features.py` | Merges benign and malicious feature CSV files into one registry-level final feature matrix. |
| `merge_registry_features.py` | Merges the final NPM and PyPI feature matrices into one combined feature matrix for schema checks and cross-registry analysis. |
| `validate_feature_matrix.py` | Validates a feature matrix by checking required columns, label distribution, missing values, infinite values, and numeric feature consistency. |
| `build_trace_inventory.py` | Builds an inventory of raw trace outputs, including package/sample names and the number of `trace.*` files found per sample. |

## Typical Workflow

```text
npm_benign_features.csv + npm_malicious_features.csv
        ↓
npm_final_feature_matrix.csv

pypi_benign_features.csv + pypi_malicious_features.csv
        ↓
pypi_final_feature_matrix.csv

npm_final_feature_matrix.csv + pypi_final_feature_matrix.csv
        ↓
combined_final_feature_matrix.csv
```

## Final Processed Matrices

The final processed matrices used in the paper are stored under:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

## Note

These scripts operate on extracted feature CSVs and trace-output folders. They do
not require raw malicious package artifacts.
