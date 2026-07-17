# Phase 4 Results

This folder contains the result tables and supporting audit files for Phase 4:
same-registry model validation and direct cross-registry baseline evaluation.

Phase 4 establishes the baseline behavior before applying the CRAST transfer
strategy in Phase 5.

## Main Result Tables

| File | Purpose |
|---|---|
| `table_01_same_registry_model_comparison.csv` | Compares model performance within the same registry, such as NPM→NPM and PyPI→PyPI. |
| `table_02_group_aware_same_registry_validation.csv` | Provides a stricter same-registry validation summary using the group-aware validation setting. |
| `table_03_direct_cross_registry_baseline.csv` | Reports direct source-only transfer results, such as NPM→PyPI and PyPI→NPM, without CRAST adaptation. |

## Supplementary Result Files

| File | Purpose |
|---|---|
| `supplement_direct_cross_registry_by_seed.csv` | Per-seed direct-transfer results used to support the summary table. |
| `supplement_source_only_best_model_per_direction.csv` | Records the best source-only baseline model for each transfer direction. |

## Registry Overlap Audit Files

| File | Purpose |
|---|---|
| `registry_overlap_audit_summary.csv` | Summarizes overlap checks between the NPM and PyPI package sets. |
| `registry_exact_name_overlap.csv` | Lists exact package-name overlaps, if any. |
| `registry_similar_name_overlap.csv` | Lists similar-name overlap checks used to support leakage analysis. |

## Interpretation

The same-registry tables show how well malicious-package detection works when
training and testing within the same ecosystem. The direct-transfer baseline
shows how performance changes when a model trained on one registry is evaluated
directly on the other registry.

These results motivate Phase 5, where CRAST applies registry-aware feature
selection and transfer adaptation.
