# CRAST Trace Collection Protocol

The trace collection workflow used dedicated worker machines and fixed-time package installation tracing.

Core workflow:

1. prepare a package-specific temporary workspace;
2. configure temporary runtime/cache paths where applicable;
3. execute package installation under `strace`;
4. follow child processes with `strace -ff`;
5. store trace files using a `trace` prefix, resulting in `trace.<pid>` files;
6. store stdout and stderr separately;
7. enforce a fixed timeout;
8. record completed and failed package lists.

NPM and PyPI runs used the same overall trace collection logic. Worker-specific scripts differed mainly in package list paths, package directories, result directories, and runtime versions.
