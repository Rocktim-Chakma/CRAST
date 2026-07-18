# Package Collection and Validation Code

This folder contains the Phase 1 code used to audit and validate the final CRAST
feature matrices before model training and cross-registry evaluation.

Phase 1 focuses on dataset quality, label balance, feature consistency, and
leakage-oriented sanity checks.

## File

| File | Purpose |
|---|---|
| `data_quality_audit.py` | Runs dataset-level checks on the final NPM and PyPI feature matrices, including row counts, label distribution, missing/infinite values, duplicate or constant features, suspicious columns, and feature-schema consistency. |

## Main Inputs

The audit script uses the final processed feature matrices:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

## Main Outputs

The audit outputs are stored in the Phase 1 `results/` folder and may include:

```text
validation_summary.csv
dataset_quality_summary.csv
feature_cleaning_audit.csv
duplicate_feature_audit.csv
suspicious_column_audit.csv
constant_features_removed.csv
single_feature_discriminative_audit.csv
strict_same_registry_validation_audit.csv
cleaning_summary_report.txt
```

## Why This Phase Matters

Before training models, the artifact verifies that the processed feature matrices
are usable and consistent. This reduces the risk that the reported results are
caused by missing values, duplicate columns, constant features, or obvious
dataset leakage artifacts.
