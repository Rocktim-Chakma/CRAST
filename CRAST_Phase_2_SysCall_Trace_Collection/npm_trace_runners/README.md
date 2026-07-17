# NPM Trace Runners

This folder contains the shell scripts used for collecting install-time SysCall
traces from NPM packages. All scripts execute package installation under
`strace`, store trace files separately, record stdout/stderr logs, and maintain
success/failed execution lists.

The repository includes both original-style runners and configurable runners.
The original-style runners preserve the worker-side execution workflow used
during data collection, while the configurable versions make the same workflow
easier to reuse with custom input/output paths.

## Files

| File | Purpose |
|---|---|
| `npm_worker_trace_runner.sh` | Original-style worker runner for tracing NPM packages from a worker-specific package list. It follows the Raspberry Pi worker execution style used during data collection. |
| `npm_worker_trace_runner_configurable.sh` | Configurable version of the worker runner. It supports user-defined package list, package directory, trace directory, log directory, and timeout settings. |
| `npm_archive_trace_runner.sh` | Original-style runner for tracing NPM package archives such as `.tgz` files. It extracts or installs archived packages and records install-time SysCall traces. |
| `npm_archive_trace_runner_configurable.sh` | Configurable version of the archive runner. It is intended for reproducible execution with user-defined archive, workspace, trace, and log paths. |

## Output

A successful trace run produces files such as:

```text
trace.<pid>
run.stdout.log
run.stderr.log
completed_packages.txt
failed_packages.txt
