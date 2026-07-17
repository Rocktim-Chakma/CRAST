# Audit and Verification Files

This folder contains audit and verification artifacts for the CRAST paper
experiments.

These files are included to make the repository easier to inspect and to support
the reproducibility claims made in the manuscript.

## Files

| File | Purpose |
|---|---|
| `RUN_COMPLETE.json` | Records completion metadata for the final confirmatory experiment run. |
| `verification_paper_result_comparison.csv` | Compares repository/artifact outputs against manuscript-reported values. |
| `final_feature_schema.csv` | Central copy of the final model input feature schema. |
| `final_transfer_evaluation_summary.csv` | Summary of final CRAST transfer evaluation results. |
| `final_transfer_evaluation_by_seed.csv` | Per-seed final transfer evaluation details. |
| `artifact_hash_manifest.csv` | Hash manifest used to document artifact files and support integrity checks. |

## Why These Files Are Included

The main result tables show the reported performance values. The audit files
provide supporting evidence about the final run, selected feature schema, and
artifact consistency.

These files are not raw malware artifacts. They are metadata and verification
outputs derived from the final processed feature matrices and experiment runs.
