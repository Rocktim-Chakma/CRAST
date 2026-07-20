# Data Availability

This repository provides the public CRAST research artifact for the paper:

**Unifying SysCall Behavior Across PyPI and NPM Registries for Malicious Package Detection**

## Publicly Available Files

The public artifact includes:

- processed SysCall-derived feature matrices,
- final selected package lists,
- result tables,
- manuscript figures,
- experiment configuration files,
- reproducible analysis scripts,
- audit and verification metadata.

The processed feature matrices are available under:

```text
data/processed/

The central result tables are available under:

```text
results/tables/
```

Audit and verification files are available under:

```text
results/audit/
```

## Raw Malicious Package Artifacts

Raw malicious package artifacts are not publicly redistributed.

This restriction is intentional because redistributing malicious packages may
create safety risks and may enable misuse.

## Raw Trace-Level Artifacts

Full raw trace-level artifacts may also be restricted when they contain sensitive
execution details, environment-specific paths, or potentially unsafe behavioral
records.

Instead, the public artifact provides processed SysCall-derived feature matrices
and reproducible analysis code so that the paper-level results can be inspected
and verified without redistributing harmful package artifacts.

## Benign Package Status

Benign packages in this artifact should be interpreted as **presumed benign**
for the time and scope of the experiment. They were selected from official
registry sources when no known malicious evidence was found during screening.

The artifact does not claim that these packages are guaranteed safe forever.

## Reproducibility

The main reproduction entry point is:

```bash
python run_all_paper_experiments.py
```

The repository also includes phase-specific scripts and reusable modules for
inspection.

Some historical original-style scripts are retained only for auditability and
may contain machine-specific paths from the original experimental environment.
For normal reproduction, use the configurable scripts and modules under:

```text
Reusable_Code_Modules/
configs/
run_all_paper_experiments.py
```

## Contact

For questions about restricted raw artifacts or additional verification details,
please contact the corresponding author listed in the manuscript.
