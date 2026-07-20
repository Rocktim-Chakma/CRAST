# Package Label Validation Protocol

This document summarizes the package-label screening logic used before
install-time tracing.

## Malicious Packages

Candidate malicious packages were retained only when they had supporting public
evidence, such as:

- advisory or vulnerability records,
- public malware reports,
- registry status or removal evidence,
- repository or metadata evidence where available,
- related public security research evidence.

Raw malicious package artifacts are not redistributed.

## Benign Packages

Candidate benign packages were selected from official registry sources. They are
treated as presumed benign when no known malicious evidence was found in the
consulted public sources during screening.

The artifact does not claim that benign packages are guaranteed safe forever.
They are presumed benign for the time and scope of the experiment.

## Exclusion Policy

Ambiguous or uncertain candidates were excluded rather than forced into either
the benign or malicious class.

The public artifact provides only the final selected package lists used in the
experiments. The full excluded-candidate list is not redistributed.
