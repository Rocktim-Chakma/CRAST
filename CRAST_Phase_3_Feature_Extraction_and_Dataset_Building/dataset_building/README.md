# Dataset Building Utilities

This folder contains the utility scripts used after feature extraction to build
the final machine-learning feature matrices for CRAST.

The workflow is:

```text
benign feature CSV + malicious feature CSV
        ↓
registry-level final feature matrix
        ↓
NPM final matrix + PyPI final matrix
        ↓
combined final feature matrix
        ↓
validation and trace inventory checks
```

## Files

| File | Purpose |
|---|---|
| `merge_class_features.py` | Merges benign and malicious feature CSVs into one registry-level feature matrix. For example, NPM benign + NPM malicious → `npm_final_feature_matrix.csv`. |
| `merge_registry_features.py` | Merges the final NPM and PyPI feature matrices into one combined feature matrix for schema checks and cross-registry analysis. |
| `validate_feature_matrix.py` | Checks a feature matrix for required columns, label distribution, missing values, infinite values, and numeric feature consistency. |
| `build_trace_inventory.py` | Builds a package-level inventory from raw trace folders, including the number of `trace.*` files per package/sample. |

## Main Outputs

The final processed matrices used by the paper are stored under:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

## Label Convention

| Label | Meaning |
|---|---|
| `0` | Benign package |
| `1` | Malicious package |

## Notes

The dataset-building utilities operate on extracted feature CSVs, not on raw
malicious package artifacts. Raw malicious packages are intentionally not
included in the public repository for safety and redistribution reasons.
