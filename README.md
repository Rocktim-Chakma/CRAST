# CRAST: Cross-Registry Anomalous SysCall Tracing

**CRAST** is a SysCall-based framework for studying cross-registry malicious
package detection between the **NPM** and **PyPI** ecosystems.

This repository contains the public research artifact for the paper:

**Unifying SysCall Behavior Across PyPI and NPM Registries for Malicious Package Detection**

The goal of CRAST is not only to detect malicious packages within one registry,
but also to evaluate whether install-time SysCall behavior learned from one
registry can transfer to another registry under a target-label-free setting.

---

## Overview

Open-source package registries such as NPM and PyPI are widely used in modern
software development. Malicious packages can abuse installation scripts, setup
routines, dependency installation, or build-time execution to access files,
spawn processes, modify permissions, contact external hosts, or manipulate the
host environment.

CRAST studies this problem using install-time SysCall tracing. Packages are
collected, label-screened, installed in a controlled tracing environment, and
converted into a shared SysCall-derived feature space. The framework then
evaluates both same-registry detection and cross-registry transfer.

The repository is organized according to the five phases used in the paper:

1. Package collection and label validation
2. SysCall trace collection
3. Feature extraction and dataset building
4. Model training and baseline evaluation
5. CRAST transfer evaluation and analysis

---

## Main Research Questions

CRAST is designed around the following questions:

- Can install-time SysCall behavior detect malicious packages within the same registry?
- Does SysCall-derived malicious behavior transfer from NPM to PyPI?
- Does SysCall-derived malicious behavior transfer from PyPI to NPM?
- Is cross-registry transfer symmetric, or does the transfer direction matter?
- Can registry-aware feature filtering and label-free score handling improve transfer?

---

## Key Findings

The final experiments use balanced and validated package sets:

| Registry | Benign | Malicious | Total |
|---|---:|---:|---:|
| NPM | 737 | 737 | 1,474 |
| PyPI | 737 | 737 | 1,474 |
| **Total** | **1,474** | **1,474** | **2,948** |

Main paper-level results:

| Setting | Direction | Main Result |
|---|---|---:|
| Same-registry | NPM → NPM | F1 ≈ 0.97 |
| Same-registry | PyPI → PyPI | F1 ≈ 0.92 |
| Direct source-only transfer | NPM → PyPI | F1 ≈ 0.67 |
| Direct source-only transfer | PyPI → NPM | F1 ≈ 0.89 |
| CRAST transfer strategy | NPM → PyPI | F1 ≈ 0.78 |
| CRAST transfer strategy | PyPI → NPM | F1 ≈ 0.94 |

The results show that cross-registry transfer is asymmetric. PyPI → NPM transfer
is stronger than NPM → PyPI transfer, and CRAST reduces but does not eliminate
the directional F1 gap.

---

## Repository Structure

```text
CRAST/
├── README.md
├── REPRODUCIBILITY.md
├── DATA_AVAILABILITY.md
├── SECURITY.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── run_all_paper_experiments.py
│
├── configs/
│   └── Configuration files used by the reproducible experiment scripts.
│
├── environment/
│   └── Environment notes and dependency information.
│
├── data/
│   ├── processed/
│   │   ├── npm_final_feature_matrix.csv
│   │   ├── pypi_final_feature_matrix.csv
│   │   └── combined_final_feature_matrix.csv
│   └── README.md
│
├── CRAST_Phase_1_Package_Collection_and_Validation/
│   ├── selected_package/
│   ├── summary/
│   ├── validation_protocol.md
│   └── README.md
│
├── CRAST_Phase_2_SysCall_Trace_Collection/
│   └── Tracing runners, tracing protocol, and trace-collection notes.
│
├── CRAST_Phase_3_Feature_Extraction_and_Dataset_Building/
│   └── Feature extraction, dataset construction, and schema-building files.
│
├── CRAST_Phase_4_Model_Training_and_Baseline_Evaluation/
│   └── Same-registry and direct cross-registry baseline experiments.
│
├── CRAST_Phase_5_CRAST_Transfer_Evaluation_and_Analysis/
│   └── CRAST transfer evaluation, fusion analysis, gamma sensitivity,
│       ablation studies, and final transfer results.
│
├── results/
│   ├── tables/
│   └── audit/
│
├── Figures/
│   └── Manuscript figures.
│
└── Reusable_Code_Modules/
    ├── experiments/
    └── src/
```

---

## Phase Summary

### Phase 1: Package Collection and Label Validation

This phase documents the package-selection and label-validation stage before
install-time tracing.

It includes the final selected package lists for:

- NPM malicious packages
- NPM benign packages
- PyPI malicious packages
- PyPI benign packages

Candidate malicious packages were screened using public evidence such as
advisory records, malware reports, registry status, repository metadata, and
other public security evidence where available.

Candidate benign packages were selected from official registry sources and
treated as presumed benign when no known malicious evidence was found during
screening.

Ambiguous or uncertain candidates were excluded rather than forced into either
class.

### Phase 2: SysCall Trace Collection

This phase contains the tracing protocol and tracing runners used to collect
install-time SysCall behavior.

NPM packages are traced through the Node.js/npm installation workflow.

PyPI packages are traced through the Python/pip installation workflow.

The tracing pipeline records install-time behavior such as:

- file activity,
- process creation,
- command execution,
- network-related SysCalls,
- permission changes,
- sensitive path access,
- SysCall failure behavior.

### Phase 3: Feature Extraction and Dataset Building

This phase converts raw SysCall traces into fixed-length package-level feature
vectors.

The extracted features include:

- raw SysCall counts,
- grouped behavior counts,
- path-sensitive indicators,
- suspicious execution flags,
- network-related features,
- permission-related features,
- ratio-based features.

The same feature schema is used for both NPM and PyPI to support fair
cross-registry transfer evaluation.

### Phase 4: Model Training and Baseline Evaluation

This phase contains the same-registry and direct source-only baseline
experiments.

Same-registry experiments evaluate detection performance within the same
registry.

Direct cross-registry experiments train on one registry and test directly on the
other registry without CRAST transfer adaptation.

### Phase 5: CRAST Transfer Evaluation and Analysis

This phase contains the final CRAST transfer strategy and analysis.

CRAST applies:

- registry-aware transferable feature filtering,
- label-free score alignment,
- source-selected Top-5 percentile-rank fusion for NPM → PyPI,
- Extra Trees with mean/std score alignment for PyPI → NPM,
- multi-seed confirmatory evaluation.

This phase also includes gamma sensitivity, fusion ablation, feature-group
ablation, imbalanced target evaluation, and behavioral-dispersion analysis.

---

## Reproducibility and Original-Style Scripts

The repository is organized according to the five phases used in the paper
framework. The goal is to keep the artifact clear, reproducible, and aligned
with the manuscript.

Some historical original-style scripts are retained only for auditability and to
show how earlier local processing was performed. These scripts may contain
machine-specific paths from the original experimental environment. They are not
intended as the primary reproduction entry point.

For normal reproduction and inspection, use the configurable scripts and modules
under:

```text
Reusable_Code_Modules/
run_all_paper_experiments.py
configs/
```

The public artifact includes processed SysCall-derived feature matrices, result
tables, manuscript figures, audit metadata, and reproducible analysis code. Raw malicious
package artifacts are not redistributed for safety reasons.

---

## Installation

Create and activate a Python environment, then install the required packages:

```bash
pip install -r requirements.txt
```

The experiments use standard Python machine-learning and data-processing
libraries such as pandas, NumPy, scikit-learn, and gradient-boosting libraries
where applicable.

---

## Main Reproduction Entry Point

The main paper-level reproduction script is:

```bash
python run_all_paper_experiments.py
```

This script is intended to reproduce the paper-level analysis from the processed
feature matrices and configuration files included in the public artifact.

The processed feature matrices are located in:

```text
data/processed/
```

The central paper-level result tables are located in:

```text
results/tables/
```

The audit and verification files are located in:

```text
results/audit/
```

---

## Important Result Tables

Central result tables are stored under:

```text
results/tables/
```

Key files include:

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

## Data Availability

The public artifact includes processed SysCall-derived feature matrices, result
tables, manuscript figures, audit files, and reproducible analysis code.

Raw malicious package artifacts are not publicly released to avoid potential
misuse and redistribution of harmful software.

Full raw trace-level artifacts may also be restricted when they contain sensitive
execution details. The processed feature matrices and result-analysis code are
provided to support inspection and result verification.

---

## Security Notice

This repository is a research artifact for malicious package detection.

It does **not** redistribute raw malicious packages.

Do not execute unknown package artifacts outside a controlled and isolated
analysis environment.

The scripts and data are provided for academic inspection, reproducibility, and
research validation.

---

## Citation

Use the citation metadata in:

```text
CITATION.cff
```

when citing this repository or the CRAST artifact.

---

## License

See:

```text
LICENSE
```

for license information.

---

## Contact

For questions about the artifact, dataset, or experiments, please contact the
corresponding author listed in the manuscript.
