# Reusable Code Modules

This folder contains the reusable, modular implementation of the CRAST pipeline.

The phase folders preserve the paper-artifact structure, while this folder
contains the shared source code and experiment scripts used to run the pipeline
in a cleaner reusable form.

## Folder Structure

| Folder | Purpose |
|---|---|
| `experiments/` | Runnable experiment scripts for data audit, same-registry validation, direct transfer baseline, final CRAST transfer, gamma sensitivity, and feature-group ablation. |
| `src/crast/` | Core CRAST Python modules for configuration, data loading, metrics, models, feature selection, transfer logic, data audit, and feature grouping. |
| `src/features/` | Reusable raw `strace` feature extractor. |
| `src/data/` | Dataset-building utilities for merging, validating, and inventorying feature matrices and trace outputs. |

## Relationship to Phase Folders

The phase folders are organized according to the five-phase CRAST framework used
in the manuscript. They are easier for reviewers to inspect step by step.

This folder is provided for users who want to run or reuse the code more
directly.

## Main Experiment Scripts

The scripts under `experiments/` correspond to the paper workflow:

```text
01_data_quality_audit.py
02_same_registry_validation.py
03_direct_transfer_baseline.py
04_crast_transfer_final.py
05_gamma_sensitivity.py
06_feature_group_ablation.py
run_all_paper_experiments.py
```

## Core Method Implementation

The central CRAST formula:

```text
T(f) = U(f) - gamma * B(f)
```

is implemented in:

```text
src/crast/feature_selection.py
```

The transfer strategies are implemented in:

```text
src/crast/transfer.py
```

including source-only transfer, rank-based transfer, rank fusion, and mean/std
score alignment.
