# Reproducibility

This document explains how to inspect and reproduce the public CRAST research
artifact for the paper:

**Unifying SysCall Behavior Across PyPI and NPM Registries for Malicious Package Detection**

CRAST evaluates install-time SysCall-derived behavior for malicious package
detection across the NPM and PyPI ecosystems. The repository is organized around
the five phases used in the manuscript: package collection and label validation,
SysCall trace collection, feature extraction, baseline evaluation, and final
CRAST transfer evaluation.

---

## Reproduction Scope

This public artifact is designed to reproduce and inspect the paper-level
analysis from processed SysCall-derived feature matrices and result files.

The artifact does not redistribute raw malicious package artifacts for safety
reasons. Therefore, the main reproduction path starts from the processed feature
matrices available under:

```text
data/processed/
```

The main reproduction entry point is:

```bash
python run_all_paper_experiments.py
```

This script uses the processed feature matrices, configuration files, and
reusable analysis modules included in the repository.

Some historical original-style scripts are retained only for auditability and may
contain machine-specific paths from the original experimental environment. They
are not intended as the primary reproduction entry point.

For normal reproduction, use:

```text
run_all_paper_experiments.py
configs/
Reusable_Code_Modules/
```

---

## Public Artifact Contents

The public repository includes:

- processed SysCall-derived feature matrices,
- final selected package lists,
- result tables,
- manuscript figures,
- experiment configuration files,
- reproducible analysis scripts,
- audit and verification metadata.

Raw malicious package artifacts are not redistributed.

Full raw trace-level artifacts may also be restricted when they contain sensitive
execution details, environment-specific paths, or potentially unsafe behavioral
records.

---

## Required Environment

The artifact is intended to run with a standard Python environment.

Install the required dependencies with:

```bash
pip install -r requirements.txt
```

The main analysis scripts use common Python data-processing and machine-learning
libraries such as pandas, NumPy, scikit-learn, and gradient-boosting libraries
where applicable.

---

## Main Reproduction Command

From the repository root, run:

```bash
python run_all_paper_experiments.py
```

This command reproduces the paper-level analysis from the processed feature
matrices and configuration files included in the repository.

The script is intended for result inspection and verification, not for
redistributing or executing raw malicious packages.

---

## Input Data

The processed feature matrices are stored in:

```text
data/processed/
```

Key files include:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

These files contain the final SysCall-derived feature representations used in
the paper-level experiments.

Non-behavioral fields such as package name, registry identifier, and class label
are used for dataset management and evaluation, but they are excluded from model
input where required to reduce leakage risk.

---

## Result Tables

Central paper-level result tables are stored in:

```text
results/tables/
```

Important files include:

| File | Purpose |
|---|---|
| `table_01_same_registry_model_comparison.csv` | Same-registry model comparison across candidate classifiers. |
| `table_02_group_aware_same_registry_validation.csv` | Main group-aware same-registry validation results. |
| `table_03_direct_cross_registry_baseline.csv` | Direct source-only cross-registry transfer baseline results. |
| `table_04_crast_final_transfer_summary.csv` | Final CRAST transfer results using the frozen direction-specific configurations. |
| `table_05_cross_registry_confusion_matrices.csv` | Final CRAST confusion-matrix values behind the manuscript confusion-matrix figure. This is an artifact result table, not a separate manuscript table. |
| `table_06_rank_fusion_ablation.csv` | Fusion strategy ablation results. |
| `table_07_gamma_sensitivity.csv` | Gamma sensitivity results for registry-aware feature filtering. |
| `table_08_feature_group_ablation.csv` | Feature-group ablation results. |
| `supplement_direct_model_confusion_matrices.csv` | Direct model-wise confusion matrices from source-only transfer baselines, retained as supplementary audit output. |

---

## Audit and Verification Files

Audit and verification files are stored in:

```text
results/audit/
```

These files support inspection of the final artifact and paper-level results.

Important files include:

```text
RUN_COMPLETE.json
artifact_hash_manifest.csv
final_feature_schema.csv
final_transfer_evaluation_by_seed.csv
final_transfer_evaluation_summary.csv
verification_paper_result_comparison.csv
```

The hash manifest should be regenerated only after all final repository edits are
complete.

---

## Phase-Level Reproduction Structure

The repository is organized into five paper-aligned phases.

### Phase 1: Package Collection and Label Validation

```text
CRAST_Phase_1_Package_Collection_and_Validation/
```

This phase documents the package-selection and label-validation stage.

It includes final selected package lists for:

```text
selected_packages/npm_malicious_selected.csv
selected_packages/npm_benign_selected.csv
selected_packages/pypi_malicious_selected.csv
selected_packages/pypi_benign_selected.csv
```

Candidate benign packages should be interpreted as presumed benign for the time
and scope of the experiment, not guaranteed safe forever.

### Phase 2: SysCall Trace Collection

```text
CRAST_Phase_2_SysCall_Trace_Collection/
```

This phase contains tracing runners, tracing protocol notes, and trace-collection
documentation.

NPM packages are traced through the Node.js/npm installation workflow.

PyPI packages are traced through the Python/pip installation workflow.

### Phase 3: Feature Extraction and Dataset Building

```text
CRAST_Phase_3_Feature_Extraction_and_Dataset_Building/
```

This phase contains feature extraction, dataset construction, schema generation,
and feature-cleaning logic.

Some original-style scripts may contain local paths from the original
experimental environment and are retained only for auditability.

### Phase 4: Model Training and Baseline Evaluation

```text
CRAST_Phase_4_Model_Training_and_Baseline_Evaluation/
```

This phase contains same-registry model comparison, group-aware same-registry
validation, and direct source-only cross-registry transfer baselines.

### Phase 5: CRAST Transfer Evaluation and Analysis

```text
CRAST_Phase_5_CRAST_Transfer_Evaluation_and_Analysis/
```

This phase contains the final CRAST transfer evaluation and analysis, including:

- registry-aware feature filtering,
- Top-5 percentile-rank fusion,
- mean/std score alignment,
- gamma sensitivity,
- fusion ablation,
- feature-group ablation,
- imbalanced target evaluation,
- behavioral-dispersion analysis.

---

## Target-Label-Free Transfer Setting

The final CRAST transfer experiments follow a target-label-free prediction
setting.

During the confirmatory transfer evaluation, target-registry class labels are not
used for:

- feature filtering,
- model fitting,
- threshold construction,
- score alignment,
- rank fusion,
- prediction generation.

Target labels are used only after predictions are finalized to compute
evaluation metrics such as accuracy, precision, recall, F1-score, and confusion
matrices.

---

## Expected Paper-Level Results

The main paper-level result pattern is:

| Setting | Direction | Expected Result |
|---|---|---:|
| Same-registry | NPM → NPM | F1 ≈ 0.97 |
| Same-registry | PyPI → PyPI | F1 ≈ 0.92 |
| Direct source-only transfer | NPM → PyPI | F1 ≈ 0.67 |
| Direct source-only transfer | PyPI → NPM | F1 ≈ 0.89 |
| CRAST transfer strategy | NPM → PyPI | F1 ≈ 0.78 |
| CRAST transfer strategy | PyPI → NPM | F1 ≈ 0.94 |

Small formatting differences may occur depending on rounding, but the reproduced
summary should match the paper-level result pattern.

---

## Security and Safety Notes

This repository is a research artifact.

It does not redistribute raw malicious package artifacts.

Do not execute unknown package artifacts outside a controlled and isolated
analysis environment.

The released artifact supports inspection and reproducibility through processed
feature matrices, reusable code, result tables, figures, and audit files.

---

## Limitations of Reproduction

This public artifact is intended to reproduce the paper-level analysis from
processed features.

It does not fully recreate the original raw trace-collection environment because:

- raw malicious packages are not redistributed,
- some raw trace artifacts may contain sensitive execution details,
- original tracing used a controlled experimental environment,
- historical scripts may include local paths retained only for auditability.

The processed feature matrices and reusable scripts are provided so that the
reported results can be inspected and verified without redistributing unsafe
artifacts.

---

## Contact

For questions about reproduction, restricted raw artifacts, or additional
verification details, please contact the corresponding author listed in the
manuscript.
