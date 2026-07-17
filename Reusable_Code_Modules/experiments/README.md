# Reusable Experiment Scripts

This folder contains runnable experiment scripts for reproducing the CRAST paper
results using the processed NPM and PyPI feature matrices.

These scripts are the reusable counterparts of the phase-specific experiment
scripts. They are useful for running the pipeline from a single code location.

## Files

| File | Purpose |
|---|---|
| `_common.py` | Shared helper used by the experiment scripts for loading data, parsing arguments, reading configuration, and creating output folders. |
| `01_data_quality_audit.py` | Runs dataset sanity checks such as missing-value checks, label distribution checks, feature consistency checks, and audit summaries. |
| `02_same_registry_validation.py` | Runs same-registry validation for NPM→NPM and PyPI→PyPI. |
| `03_direct_transfer_baseline.py` | Runs direct source-only cross-registry baselines, such as NPM→PyPI and PyPI→NPM without CRAST adaptation. |
| `04_crast_transfer_final.py` | Runs the final CRAST transfer evaluation using the direction-specific strategies reported in the paper. |
| `05_gamma_sensitivity.py` | Runs sensitivity analysis for the registry-bias penalty parameter `gamma`. |
| `06_feature_group_ablation.py` | Runs feature-group ablation to evaluate the contribution of SysCall behavior groups. |
| `run_all_paper_experiments.py` | Runs the main experiment scripts sequentially. |

## Typical Usage

From the repository root:

```bash
python Reusable_Code_Modules/experiments/run_all_paper_experiments.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

Individual scripts can also be run separately with the same `--npm`, `--pypi`,
and `--out` arguments.

## Inputs

The scripts expect the final processed feature matrices:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
```

## Outputs

Outputs are CSV result tables written to the selected output directory. The
paper-ready copies of the main tables are stored under:

```text
results/tables/
```
