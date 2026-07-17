# CRAST SysCall Tracing Protocol

This document describes the tracing protocol used to collect install-time
SysCall behavior from NPM and PyPI packages.

The goal of Phase 2 is to execute package installation in a controlled research
environment and record operating-system level behavior using `strace`.

## Common Tracing Controls

Both NPM and PyPI tracing use the same containment principle:

- run packages on dedicated worker machines,
- avoid personal or production systems,
- use package-specific temporary workspaces,
- separate trace files from stdout/stderr logs,
- apply fixed execution timeouts,
- record completed and failed executions,
- run without personal credentials or secrets,
- restrict network exposure at the worker/gateway environment level.

The exact runtime isolation differs by registry because NPM and PyPI use
different installation runtimes.

## NPM Tracing

NPM packages are installed through the Node/npm runtime.

For NPM, tracing uses:

- temporary package workspace,
- temporary `HOME` directory,
- package-specific npm cache directory,
- temporary `TMPDIR`,
- Node/npm package installation,
- `strace -ff` child-process tracing,
- fixed timeout,
- separated stdout/stderr logs,
- completed/failed package lists.

Python virtual environments are not the primary isolation mechanism for NPM,
because NPM packages are executed through Node/npm rather than Python/pip.

## PyPI Tracing

PyPI packages are installed through Python/pip.

For PyPI, tracing uses:

- temporary package workspace,
- temporary Python virtual environment,
- temporary `HOME` directory,
- package-specific pip cache directory,
- temporary `TMPDIR`,
- `python -m pip install` inside the virtual environment,
- `strace -ff` child-process tracing,
- fixed timeout,
- separated stdout/stderr logs,
- completed/failed package lists.

The temporary virtual environment is used directly for PyPI because PyPI
installation is Python/pip based.

## Trace Output

A traced run may produce files such as:

```text
trace.<pid>
run.stdout.log
run.stderr.log
completed_packages.txt
failed_packages.txt
```

The `trace.<pid>` files are produced by `strace -ff`, where each file corresponds
to a traced process or child process created during package installation.

## Excluded Runs

Packages that failed to install, timed out, or produced incomplete/empty trace
outputs were tracked in failed execution lists and excluded from the final
feature matrices.

Successful-run extraction refers only to trace-collection status. It does not
refer to benign or malicious class labels.

## Safety Notice

The tracing scripts may execute package lifecycle, setup, build, or install
hooks. These scripts should only be used in a controlled malware-analysis
environment. Do not run them on personal or production systems.
