# Phase 5 Results

This folder contains the final CRAST transfer evaluation results and supporting
analysis files.

Phase 5 evaluates the final cross-registry transfer strategy after the Phase 4
direct-transfer baseline.

## Main Result Tables

| File | Purpose |
|---|---|
| `table_04_crast_final_transfer_summary.csv` | Main final CRAST transfer result summary for NPM→PyPI and PyPI→NPM. |
| `table_05_cross_registry_confusion_matrices.csv` | Manuscript-displayed integer confusion-matrix values for the final CRAST transfer configurations shown in Figure 4. |
| `table_06_rank_fusion_ablation.csv` | Ablation of rank-fusion strategies used to support the final NPM→PyPI design. |
| `table_07_gamma_sensitivity.csv` | Sensitivity analysis for the registry-bias penalty parameter `gamma`. |
| `table_08_feature_group_ablation.csv` | Feature-group ablation results showing the contribution of different SysCall behavior groups. |

## Supplementary Files

| File | Purpose |
|---|---|
| `supplement_final_methods_by_seed.csv` | Per-seed results for the final CRAST transfer methods. |
| `supplement_selected_features_by_seed.csv` | Selected transferable features for each seed. |
| `supplement_feature_scores_by_seed.csv` | Feature utility, registry-bias, and transferability scores by seed. |
| `supplement_top5_model_selection_frequency.csv` | Frequency of models selected in the Top-5 rank-fusion ensemble. |
| `supplement_rank_fusion_ablation_by_seed.csv` | Per-seed rank-fusion ablation details. |
| `supplement_gamma_sensitivity_by_seed.csv` | Per-seed gamma sensitivity details. |
| `supplement_feature_group_ablation_by_seed.csv` | Per-seed feature-group ablation details. |

## Behavioral Analysis Files

| File | Purpose |
|---|---|
| `supplement_behavioral_distance_summary.csv` | Summary of behavioral distance between NPM and PyPI feature distributions. |
| `supplement_behavioral_diversity_by_feature_group.csv` | Behavioral diversity grouped by feature category. |
| `supplement_behavioral_diversity_by_registry.csv` | Behavioral diversity grouped by registry. |

## Verification File

| File | Purpose |
|---|---|
| `verification_paper_result_comparison.csv` | Compares artifact outputs against manuscript-reported values. |

## Final CRAST Strategy

The final direction-specific CRAST strategy is:

| Direction | Strategy |
|---|---|
| NPM → PyPI | Top-5 source-selected percentile-rank fusion with rank-threshold transfer |
| PyPI → NPM | Extra Trees with mean/std score alignment |

The transferable feature score is implemented as:

```text
T(f) = U(f) - gamma * B(f)
```

where `U(f)` is malware-label utility and `B(f)` is registry-discrimination bias.
