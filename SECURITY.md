# Security Notice

The tracing scripts in this repository execute package installation workflows. Some package installation hooks may be malicious. Do not run these scripts on a personal or production system.

Recommended controls:

- Use dedicated disposable workers or virtual machines.
- Run as a non-root user.
- Block external inbound traffic.
- Restrict and monitor outbound traffic through a gateway firewall.
- Do not store SSH keys, API tokens, cloud credentials, or personal files on tracing workers.
- Use temporary HOME, cache, and workspace directories.
- Use Python virtual environments for PyPI package tracing where applicable.
- Apply strict execution timeouts.
- Store stdout, stderr, and strace logs separately.
- Reset or reimage workers after tracing untrusted packages.
- Do not redistribute raw malicious package artifacts.
