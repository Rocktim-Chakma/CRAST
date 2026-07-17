# CRAST: Cross-Registry Anomalous SysCall Tracing

This repository is the paper artifact package for **CRAST**, a cross-registry malicious package detection framework for the NPM and PyPI ecosystems using install-time SysCall traces.

The repository is organized according to the five phases used in the paper framework. The goal is to keep the artifact clear, reproducible, and aligned with the manuscript rather than to preserve local worker paths or exploratory notebook history.

## Five-phase artifact structure

```text
CRAST_Phase_1_Package_Collection_and_Validation/
CRAST_Phase_2_SysCall_Trace_Collection/
CRAST_Phase_3_Feature_Extraction_and_Dataset_Building/
CRAST_Phase_4_Model_Training_and_Baseline_Evaluation/
CRAST_Phase_5_CRAST_Transfer_Evaluation_and_Analysis/
```

## Main processed feature matrices

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

These CSV files contain the final processed feature matrices used for the paper experiments. Raw malicious package artifacts are not redistributed for safety reasons.

## Main result tables

```text
results/tables/table_01_same_registry_model_comparison.csv
results/tables/table_02_group_aware_same_registry_validation.csv
results/tables/table_03_direct_cross_registry_baseline.csv
results/tables/table_04_crast_final_transfer_summary.csv
results/tables/table_05_cross_registry_confusion_matrices.csv
results/tables/table_06_rank_fusion_ablation.csv
results/tables/table_07_gamma_sensitivity.csv
results/tables/table_08_feature_group_ablation.csv
```

## Reproducing the paper-aligned scripts

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the full experiment pipeline:

```bash
python run_all_paper_experiments.py \
  --npm data/processed/npm_final_feature_matrix.csv \
  --pypi data/processed/pypi_final_feature_matrix.csv \
  --out reproduced_results
```

For a quick smoke test, run one lightweight script with the sample CSV files:

```bash
python Reusable_Code_Modules/experiments/02_same_registry_validation.py \
  --npm data/sample/npm_sample_features.csv \
  --pypi data/sample/pypi_sample_features.csv \
  --out reproduced_sample_results \
  --models ExtraTrees \
  --seeds 42 \
  --n-estimators 20 \
  --n-splits 2
```

## Data and security note

The repository includes code, configuration, processed feature matrices, final result tables, figures, and audit metadata. Raw malicious package archives are not included because redistributing malware artifacts creates safety and ethical risks. Trace collection scripts are provided for controlled research environments only; see `SECURITY.md`.
