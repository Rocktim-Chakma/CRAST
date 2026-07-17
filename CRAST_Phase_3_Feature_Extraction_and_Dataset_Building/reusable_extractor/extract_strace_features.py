#!/usr/bin/env python3
"""Generic strace feature extractor for CRAST.

This consolidates registry/class-specific extractors into one configurable script.
"""
from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from pathlib import Path
import pandas as pd

SYSCALL_PATTERN = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z_][A-Za-z0-9_]*)\(")

GROUPS = {
    "file": {"open", "openat", "read", "write", "close", "stat", "lstat", "fstat", "access", "chmod", "chown", "unlink", "rename", "mkdir", "rmdir", "getdents", "getdents64", "readlink", "symlink"},
    "process": {"execve", "fork", "vfork", "clone", "wait4", "waitpid", "exit", "exit_group"},
    "network": {"socket", "connect", "bind", "listen", "accept", "accept4", "sendto", "recvfrom", "sendmsg", "recvmsg", "getsockname", "getpeername"},
    "memory": {"mmap", "mprotect", "munmap", "brk"},
    "io": {"ioctl", "fcntl", "poll", "select", "pselect6", "epoll_create", "epoll_ctl", "epoll_wait"},
}

IMPORTANT = sorted(set().union(*GROUPS.values()))
PATH_FLAGS = {
    "touched_tmp": ["/tmp", "tmp/"],
    "touched_home": ["/home", "home/"],
    "touched_hidden": ["/.", "./."],
    "touched_ssh": [".ssh", "id_rsa", "known_hosts"],
    "touched_profile": [".bashrc", ".profile", ".zshrc"],
    "touched_proc": ["/proc"],
    "touched_dev": ["/dev"],
    "touched_cache": ["cache", ".npm", "pip-cache", ".cache"],
    "touched_node_modules": ["node_modules"],
    "touched_site_packages": ["site-packages"],
    "touched_package_json": ["package.json"],
    "touched_lockfile": ["package-lock.json", "yarn.lock", "poetry.lock"],
}


def entropy(counter: Counter) -> float:
    total = sum(counter.values())
    if total <= 0:
        return 0.0
    return -sum((v / total) * math.log2(v / total) for v in counter.values() if v > 0)


def safe_ratio(a, b):
    return float(a) / float(b) if b else 0.0


def parse_trace_file(path: Path):
    syscalls = []
    failed = 0
    text_flags = Counter()
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = SYSCALL_PATTERN.search(line)
                if not m:
                    continue
                call = m.group(1)
                syscalls.append(call)
                if "= -1" in line:
                    failed += 1
                low = line.lower()
                for flag, needles in PATH_FLAGS.items():
                    if any(n in low for n in needles):
                        text_flags[flag] = 1
                if any(x in low for x in ["/bin/sh", "/bin/bash", "cmd.exe", "powershell"]):
                    text_flags["spawned_shell"] = 1
                if any(x in low for x in ["curl", "wget"]):
                    text_flags["used_curl_wget"] = 1
                if "git" in low:
                    text_flags["used_git"] = 1
    except OSError:
        pass
    return syscalls, failed, text_flags


def extract_sample_features(sample_dir: Path, registry: str, label: int, trace_glob: str):
    trace_files = sorted(sample_dir.glob(trace_glob))
    all_calls = []
    failed = 0
    flags = Counter()
    for tf in trace_files:
        calls, f, fl = parse_trace_file(tf)
        all_calls.extend(calls)
        failed += f
        flags.update(fl)
    counts = Counter(all_calls)
    total = len(all_calls)
    row = {
        "sample_id": sample_dir.name,
        "registry": registry,
        "label": int(label),
        "trace_file_count": len(trace_files),
        "total_syscalls": total,
        "unique_syscalls": len(counts),
        "failed_syscalls": failed,
        "failed_syscall_ratio": safe_ratio(failed, total),
        "syscall_entropy": entropy(counts),
    }
    for call in IMPORTANT:
        row[f"count_{call}"] = counts.get(call, 0)
    for group, names in GROUPS.items():
        group_count = sum(counts.get(n, 0) for n in names)
        row[f"{group}_syscall_count"] = group_count
        row[f"{group}_syscall_ratio"] = safe_ratio(group_count, total)
        row[f"{group}_unique_syscalls"] = sum(1 for n in names if counts.get(n, 0) > 0)
    for flag in PATH_FLAGS:
        row[flag] = int(flags.get(flag, 0) > 0)
    for flag in ["spawned_shell", "used_curl_wget", "used_git"]:
        row[flag] = int(flags.get(flag, 0) > 0)
    row["outbound_network"] = int(row.get("count_connect", 0) > 0 or row.get("network_syscall_count", 0) > 0)
    row["process_execution_ratio"] = safe_ratio(row.get("process_syscall_count", 0), total)
    row["network_activity_ratio"] = safe_ratio(row.get("network_syscall_count", 0), total)
    row["file_activity_ratio"] = safe_ratio(row.get("file_syscall_count", 0), total)
    row["path_suspicion_score"] = sum(row.get(k, 0) for k in ["touched_tmp", "touched_hidden", "touched_ssh", "touched_profile", "touched_proc", "touched_dev"])
    return row


def main():
    p = argparse.ArgumentParser(description="Extract CRAST features from per-sample strace folders")
    p.add_argument("--input", required=True, help="Folder containing one subfolder per package/sample")
    p.add_argument("--output", required=True, help="Output CSV path")
    p.add_argument("--registry", required=True, choices=["npm", "pypi", "NPM", "PyPI"])
    p.add_argument("--label", required=True, type=int, choices=[0, 1])
    p.add_argument("--trace-glob", default="trace.*")
    args = p.parse_args()
    root = Path(args.input)
    rows = []
    for sample_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        rows.append(extract_sample_features(sample_dir, args.registry, args.label, args.trace_glob))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
