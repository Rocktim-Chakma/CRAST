# Configuration Files

This folder contains configuration files that document the main settings used in
the CRAST tracing, feature-extraction, and experiment pipeline.

The scripts also support command-line arguments, but these YAML files provide a
clear artifact-level record of the default paper settings.

## Files

| File | Purpose |
|---|---|
| `experiment.yaml` | Stores experiment-level settings such as random seeds, cross-validation folds, model settings, gamma value, top-k feature count, and label/registry column names. |
| `feature_extraction.yaml` | Stores feature-extraction settings such as trace file patterns, registry names, label mapping, and expected feature-extraction inputs/outputs. |
| `tracing.yaml` | Stores trace-collection settings such as timeout, `strace` options, temporary workspace behavior, and runtime-isolation notes for NPM and PyPI tracing. |

## Why These Configs Are Included

These files make the artifact easier to audit because they separate important
experimental assumptions from the code.

They help reviewers check:

- which random seeds and cross-validation settings were used,
- which gamma value was used for registry-aware feature selection,
- which columns are treated as labels or metadata,
- how trace collection and feature extraction were configured.

## Related Files

The final environment and fixed-run metadata are stored under:

```text
environment/
```

The main paper result tables are stored under:

```text
results/tables/
```
