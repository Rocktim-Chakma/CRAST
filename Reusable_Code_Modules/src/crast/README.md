# CRAST Core Modules

This folder contains the core Python modules used by the reusable CRAST
implementation.

These modules are imported by the experiment scripts under:

```text
Reusable_Code_Modules/experiments/
```

## Files

| File | Purpose |
|---|---|
| `__init__.py` | Marks this folder as a Python package so the modules can be imported as `crast.*`. |
| `config.py` | Stores common experiment configuration values such as label column names, registry column names, non-feature columns, and default settings. |
| `io_utils.py` | Handles data loading, feature-column alignment, missing/infinite value handling, and feature matrix preparation. |
| `metrics.py` | Provides scoring and evaluation helpers such as score extraction, rank normalization, threshold selection, F1/precision/recall/AUC, and confusion-matrix calculation. |
| `models.py` | Defines the model factory functions used in the experiments, including tree-based models, linear models, and optional boosted models when available. |
| `feature_selection.py` | Implements CRAST registry-aware transferable feature scoring using `T(f) = U(f) - gamma * B(f)`. |
| `transfer.py` | Implements transfer evaluation logic, including source-only transfer, rank-based transfer, Top-5 rank fusion, and mean/std score alignment. |
| `data_audit.py` | Provides dataset-audit helpers for checking duplicated features, suspicious columns, missing values, and dataset consistency. |
| `feature_groups.py` | Defines behavioral feature groups used for feature-group ablation, such as file, process, network, permission, memory, and metadata features. |

## Core CRAST Formula

The transferable feature score is implemented in:

```text
feature_selection.py
```

as:

```text
T(f) = U(f) - gamma * B(f)
```

where:

- `U(f)` is the malware-label utility of feature `f`,
- `B(f)` is the registry-discrimination bias of feature `f`,
- `gamma` controls the penalty applied to registry-specific features.

## Transfer Logic

The final transfer logic is implemented in:

```text
transfer.py
```

The final paper setting uses:

| Direction | Transfer strategy |
|---|---|
| NPM → PyPI | Top-5 source-selected percentile-rank fusion with rank-threshold transfer |
| PyPI → NPM | Extra Trees with mean/std score alignment |
