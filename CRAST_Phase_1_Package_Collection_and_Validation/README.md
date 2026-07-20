# Phase 1: Package Collection and Label Validation

This phase documents the package-selection and label-validation stage used before
install-time SysCall tracing.

The released artifact provides the final selected package lists used in the
experiments for four groups:

```text
selected_packages/npm_malicious_selected.csv
selected_packages/npm_benign_selected.csv
selected_packages/pypi_malicious_selected.csv
selected_packages/pypi_benign_selected.csv
```

## What This Phase Represents

Phase 1 is not the feature-matrix construction stage. The final SysCall-derived
feature matrices are produced after tracing and feature extraction, and are
stored under:

```text
data/processed/
```

This phase only documents which packages were retained for the final
experiments and how labels were screened before tracing.

## Validation Policy

Candidate malicious packages were screened using public evidence such as
advisory records, malware reports, registry status, repository metadata, and
other public security evidence where available.

Candidate benign packages were selected from official registry sources and were
treated as presumed benign only when no known malicious evidence was found during
screening.

Ambiguous or uncertain candidates were excluded rather than forced into either
class.

## What Is Not Redistributed

Raw malicious package artifacts are not redistributed for safety reasons. The
full excluded-candidate list is also not redistributed in this public artifact.
Only the final selected package lists and aggregate selected-package summary are
included.
