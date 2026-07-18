# Environment and Fixed-Run Metadata

This folder contains environment, dependency, configuration, and dataset-file
metadata for the CRAST paper artifact.

These files help reviewers understand the software environment used for the
final experiments and verify that the artifact files are consistent.

## Files

| File | Purpose |
|---|---|
| `requirements_freeze.txt` | Full Python dependency freeze from the final experiment environment. This records exact package versions. |
| `fixed_config.json` | Fixed configuration used for the final confirmatory experiment run, including key parameters such as seeds, gamma, top-k, and final transfer settings. |
| `environment_manifest.json` | Summary of the runtime environment, including Python/platform/library metadata. |
| `dataset_file_manifest.json` | Dataset file manifest with file-level metadata such as size and hashes for the processed feature matrices. |

## Why This Folder Matters

The main `requirements.txt` file provides a lightweight installation guide.
This folder provides stricter final-run metadata for artifact review.

These files support:

- dependency/version inspection,
- configuration audit,
- dataset-file consistency checks,
- reproducibility documentation.

## Related Folders

The final processed matrices are stored under:

```text
data/processed/
```

The main result tables are stored under:

```text
results/tables/
```

The audit and verification outputs are stored under:

```text
results/audit/
```
