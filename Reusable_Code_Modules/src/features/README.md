# Feature Extraction Module

This folder contains the reusable feature-extraction code used to convert raw
`strace` outputs into package-level SysCall feature rows.

## File

| File | Purpose |
|---|---|
| `extract_strace_features.py` | Parses raw `trace.*` files and generates a CSV feature matrix with one row per package/sample. |

## Input

The expected input is a directory containing package-level trace folders or raw
`trace.*` files produced by `strace -ff`.

Example:

```text
sample_package/
├── trace.6297
├── trace.6299
├── trace.6301
├── run.stdout.log
└── run.stderr.log
```

## Output

The output is a feature CSV. Each row represents one package/sample.

Typical columns include:

```text
sample_id
registry
label
total_syscalls
unique_syscalls
failed_syscalls
count_execve
count_openat
count_connect
file_ratio
network_ratio
process_ratio
```

## Label Convention

| Label | Meaning |
|---|---|
| `0` | Benign package |
| `1` | Malicious package |

## Relationship to Phase 3

The Phase 3 folder contains registry-specific and original-style extractor
wrappers for auditability. This folder contains the reusable extractor used when
the same feature-extraction logic is run with configurable input/output paths.
