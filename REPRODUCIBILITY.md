# Reproducibility Guide

This artifact package follows the five-phase CRAST framework.

## Final datasets

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

## Full run

```bash
python run_all_paper_experiments.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

## Individual experiment scripts

Same-registry validation:

```bash
python Reusable_Code_Modules/experiments/02_same_registry_validation.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

Direct source-only cross-registry baseline:

```bash
python Reusable_Code_Modules/experiments/03_direct_transfer_baseline.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

Final CRAST transfer:

```bash
python Reusable_Code_Modules/experiments/04_crast_transfer_final.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

Gamma sensitivity:

```bash
python Reusable_Code_Modules/experiments/05_gamma_sensitivity.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

Feature-group ablation:

```bash
python Reusable_Code_Modules/experiments/06_feature_group_ablation.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

The result files produced by these scripts use the same canonical naming style as `results/tables/`.
