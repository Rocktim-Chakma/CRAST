# Central Result Tables

This folder provides reviewer-friendly central copies of the main paper result
tables.

The same result tables are also stored inside their corresponding phase folders.
The central copy is included so that readers can quickly find all manuscript-level
tables in one place without navigating through the full phase structure.

## Main Tables

| File | Purpose |
|---|---|
| `table_01_same_registry_model_comparison.csv` | Same-registry model comparison for NPM→NPM and PyPI→PyPI. |
| `table_02_group_aware_same_registry_validation.csv` | Group-aware same-registry validation summary. |
| `table_03_direct_cross_registry_baseline.csv` | Direct source-only NPM→PyPI and PyPI→NPM baseline results. |
| `table_04_crast_final_transfer_summary.csv` | Final CRAST transfer summary for both cross-registry directions. |
| `table_05_cross_registry_confusion_matrices.csv` | Manuscript-displayed integer confusion-matrix values for the final CRAST transfer configurations shown in Figure 4. |
| `table_06_rank_fusion_ablation.csv` | Rank-fusion ablation summary. |
| `table_07_gamma_sensitivity.csv` | Gamma sensitivity summary for registry-aware feature selection. |
| `table_08_feature_group_ablation.csv` | Feature-group ablation summary. |
| `supplement_direct_model_confusion_matrices.csv` | Direct model-wise confusion matrices from source-only transfer baselines, kept as supplementary audit output. |

## Note on Duplication

These files are intentionally duplicated from the phase-specific result folders.
The phase folders preserve the step-by-step artifact structure, while this folder
provides a compact result-table index for reviewers.
