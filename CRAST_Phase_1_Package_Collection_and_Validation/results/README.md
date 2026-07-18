# Package Collection and Validation Results

This folder contains the Phase 1 validation and audit outputs for the final CRAST
feature matrices.

These files document dataset quality checks performed before model training,
baseline evaluation, and CRAST transfer analysis.

## Files

| File | Purpose |
|---|---|
| `validation_summary.csv` | High-level validation summary for the processed NPM, PyPI, and combined feature matrices. |
| `dataset_quality_summary.csv` | Dataset-level quality summary, including row counts, feature counts, label balance, missing values, and other sanity checks. |
| `feature_cleaning_audit.csv` | Records feature-cleaning decisions and checks performed before model training. |
| `duplicate_feature_audit.csv` | Documents duplicate or redundant feature-column checks. |
| `suspicious_column_audit.csv` | Lists columns checked for possible leakage or suspicious metadata usage. |
| `constant_features_removed.csv` | Lists constant features removed or flagged during cleaning. |
| `single_feature_discriminative_audit.csv` | Checks whether any single feature is unusually discriminative, which can indicate leakage risk. |
| `strict_same_registry_validation_audit.csv` | Stores stricter same-registry validation/audit evidence. |
| `cleaning_summary_report.txt` | Human-readable summary of dataset-cleaning and validation decisions. |

## Why These Files Matter

These audit files support the credibility of the final experiments by showing
that the processed matrices were checked before training and transfer evaluation.

They help reviewers inspect whether:

- NPM and PyPI matrices have expected row and label distributions,
- feature columns are consistent,
- constant or suspicious columns were identified,
- obvious leakage-style issues were audited,
- final model inputs were prepared from cleaned feature matrices.

## Relationship to Later Phases

The validated matrices from Phase 1 are used in:

```text
Phase 4: Model Training and Baseline Evaluation
Phase 5: CRAST Transfer Evaluation and Analysis
```
