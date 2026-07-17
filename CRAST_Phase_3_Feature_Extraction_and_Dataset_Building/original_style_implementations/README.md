# Original-Style Feature Extraction Implementations

This folder preserves registry- and class-specific feature extraction scripts in an
original-style form. During CRAST data preparation, the same SysCall feature
extraction logic was applied across NPM and PyPI traces. The scripts mainly differ
by input trace directory, output CSV path, registry identifier, and class label.

The reusable implementation is provided separately under `reusable_extractor/`.
These original-style files are kept to make the registry/class-wise processing
steps explicit and easier to audit.

## Files

| File | Purpose |
|---|---|
| `npm_benign_feature_extractor.py` | Extracts features from NPM benign trace folders and assigns label `0`. |
| `npm_malicious_feature_extractor.py` | Extracts features from NPM malicious trace folders and assigns label `1`. |
| `pypi_benign_feature_extractor.py` | Extracts features from PyPI benign trace folders and assigns label `0`. |
| `pypi_malicious_feature_extractor.py` | Extracts features from PyPI malicious trace folders and assigns label `1`. |
| `extract_npm_features_from_successful_runs.py` | Parses packages listed as successfully traced in NPM worker logs and extracts features only from completed trace outputs. |
| `extract_pypi_features_from_successful_runs.py` | Parses packages listed as successfully traced in PyPI worker logs and extracts features only from completed trace outputs. |

## Note on Successful-Run Extraction

The word `successful` refers to trace-collection status, not to benign or
malicious class labels. A successful run means the package installation/tracing
process completed and produced usable `trace.*` files. Failed, timed-out, or
incomplete runs were excluded from the final feature matrices.

The class-specific extractors are the main scripts for building benign and
malicious feature CSVs. The successful-run extractors are included as supporting
evidence for worker-side trace filtering and auditability.

## Why Both Class-Specific and Successful-Run Extractors Are Included

The class-specific extractors show how benign and malicious feature matrices were
built separately for each registry. The successful-run extractors document the
worker-side filtering step used to avoid parsing failed, timed-out, or incomplete
trace outputs. This separation makes the dataset-building process easier to
audit without mixing class labels with trace-execution status.
