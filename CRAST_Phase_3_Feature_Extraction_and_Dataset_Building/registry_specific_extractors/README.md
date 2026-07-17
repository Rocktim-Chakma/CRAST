# Registry-Specific Feature Extractors

This folder contains explicit registry- and class-specific wrappers for feature
extraction. The same SysCall feature extraction logic is applied to all four
dataset partitions, while the input directory, output CSV path, registry name,
and class label are set separately.

These files make the four dataset-building branches visible in the artifact:

- NPM benign
- NPM malicious
- PyPI benign
- PyPI malicious

## Files

| File | Purpose |
|---|---|
| `extract_npm_benign_features.py` | Extracts SysCall features from NPM benign trace folders and assigns label `0`. |
| `extract_npm_malicious_features.py` | Extracts SysCall features from NPM malicious trace folders and assigns label `1`. |
| `extract_pypi_benign_features.py` | Extracts SysCall features from PyPI benign trace folders and assigns label `0`. |
| `extract_pypi_malicious_features.py` | Extracts SysCall features from PyPI malicious trace folders and assigns label `1`. |

## Label Convention

| Label | Meaning |
|---|---|
| `0` | Benign package |
| `1` | Malicious package |

## Why These Wrappers Exist

The reusable extractor under `../reusable_extractor/` can process any registry
and class by changing command-line arguments. However, these wrapper scripts are
kept to make the paper artifact explicit: each registry/class subset has a
separate entry point and produces a separate intermediate feature CSV before
dataset merging.

This avoids ambiguity about how the final NPM and PyPI feature matrices were
constructed.
