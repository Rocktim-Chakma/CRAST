# CRAST Transfer Evaluation Code

This folder contains the Phase 5 scripts used for the final CRAST cross-registry
transfer evaluation and analysis.

Phase 5 builds on the Phase 4 direct-transfer baseline. Its goal is to evaluate
the final CRAST transfer strategy and analyze the stability and contribution of
its components.

## Files

| File | Purpose |
|---|---|
| `_common.py` | Shared helper code for loading the aligned NPM/PyPI feature matrices, parsing experiment arguments, and managing output paths. This file is imported by the other Phase 5 scripts. |
| `04_crast_transfer_final.py` | Runs the final CRAST transfer evaluation. It evaluates the final NPM→PyPI and PyPI→NPM transfer strategies and writes the final transfer summary and confusion-matrix tables. |
| `05_gamma_sensitivity.py` | Evaluates how sensitive CRAST is to the registry-bias penalty parameter `gamma`. This supports the stability analysis of the registry-aware feature-selection step. |
| `06_feature_group_ablation.py` | Runs feature-group ablation to measure the contribution of file, process, network, permission, memory, and related SysCall feature groups. |

## CRAST Feature-Selection Score

The transferable feature score used by CRAST is implemented in:

```text
Reusable_Code_Modules/src/crast/feature_selection.py
```

The score is:

```text
T(f) = U(f) - gamma * B(f)
```

where:

- `U(f)` is the malware-label utility of feature `f`,
- `B(f)` is the registry-discrimination bias of feature `f`,
- `gamma` controls how strongly registry-specific features are penalized.

Features with high malware utility and low registry bias are preferred for
cross-registry transfer.

## Final Direction-Specific Strategy

The final CRAST transfer evaluation uses direction-specific transfer strategies:

| Direction | Final strategy |
|---|---|
| NPM → PyPI | Top-5 source-selected percentile-rank fusion with rank-threshold transfer |
| PyPI → NPM | Extra Trees with mean/std score alignment |

The underlying transfer functions are implemented in:

```text
Reusable_Code_Modules/src/crast/transfer.py
```

## Main Outputs

The Phase 5 scripts write results such as:

```text
table_04_crast_final_transfer_summary.csv
table_05_cross_registry_confusion_matrices.csv
table_07_gamma_sensitivity.csv
table_08_feature_group_ablation.csv
```

Additional `supplement_*` files provide per-seed and component-level evidence
behind the main paper tables.
