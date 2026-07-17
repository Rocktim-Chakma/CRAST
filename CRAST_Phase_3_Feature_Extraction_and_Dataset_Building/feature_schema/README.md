# Feature Schema

This folder documents the final SysCall-derived feature schema used by CRAST.

The feature schema helps reviewers and users understand which columns are used
as model inputs and how the final NPM and PyPI feature matrices are aligned.

## File

| File | Purpose |
|---|---|
| `final_feature_schema.csv` | Lists the final feature columns used in the CRAST experiments. It provides the reference schema for the processed NPM, PyPI, and combined feature matrices. |

## Why This File Matters

CRAST compares and transfers behavior across two registries. Therefore, the
feature matrices for NPM and PyPI must use the same feature columns in the same
meaningful representation.

The schema file supports:

- checking that NPM and PyPI feature matrices are aligned,
- verifying that non-feature columns such as `sample_id`, `registry`, and `label`
  are handled separately,
- confirming the final model input feature set,
- auditing the relationship between extracted SysCall behavior and the paper
  experiments.

## Related Files

The final processed matrices are stored under:

```text
data/processed/npm_final_feature_matrix.csv
data/processed/pypi_final_feature_matrix.csv
data/processed/combined_final_feature_matrix.csv
```

The schema is also copied under:

```text
results/audit/final_feature_schema.csv
```

for reviewer convenience.
