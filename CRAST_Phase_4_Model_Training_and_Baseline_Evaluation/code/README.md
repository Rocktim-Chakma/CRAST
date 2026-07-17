# Model Training and Baseline Evaluation Code

This folder contains the Phase 4 scripts used for same-registry model validation
and direct cross-registry baseline evaluation.

Phase 4 establishes two key points:

1. Models can detect malicious packages well within the same registry.
2. Direct source-only transfer across registries is weaker, motivating the CRAST
   transfer strategy evaluated in Phase 5.

## Files

| File | Purpose |
|---|---|
| `_common.py` | Shared helper code for loading aligned NPM/PyPI feature matrices, parsing command-line arguments, selecting model lists, and managing output paths. This file is imported by the Phase 4 scripts. |
| `02_same_registry_validation.py` | Runs same-registry validation. It evaluates models on NPM→NPM and PyPI→PyPI settings using the final feature matrices. |
| `03_direct_transfer_baseline.py` | Runs the direct source-only cross-registry baseline. It trains on one registry and evaluates directly on the other registry without CRAST transfer adaptation. |

## Evaluation Settings

The scripts use the final processed feature matrices:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
```

The label convention is:

| Label | Meaning |
|---|---|
| `0` | Benign package |
| `1` | Malicious package |

## Main Outputs

The Phase 4 scripts write result tables such as:

```text
table_01_same_registry_model_comparison.csv
table_02_group_aware_same_registry_validation.csv
table_03_direct_cross_registry_baseline.csv
```

Additional supplementary files may contain per-seed details and registry-overlap
audit information.

## Relationship to Phase 5

Phase 4 does not apply CRAST transfer adaptation. It provides the baseline
evidence showing that direct cross-registry transfer is more difficult than
same-registry detection. Phase 5 then evaluates the CRAST transfer strategy.
