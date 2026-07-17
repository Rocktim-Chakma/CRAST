from pathlib import Path
import csv
import re
import math
from collections import Counter

base_dir = Path(r"E:\New folder\npm_benign_raw_data")
out_file = base_dir.parent / "npm_benign_features_v2.csv"

pattern = re.compile(r'^\d{2}:\d{2}:\d{2}\.\d+\s+([a-zA-Z_][a-zA-Z0-9_]*)\(')

FILE_SYSCALLS = {
    "open", "openat", "read", "write", "close", "stat", "lstat", "fstat",
    "newfstatat", "lseek", "getdents", "getdents64", "rename", "renameat",
    "unlink", "unlinkat", "mkdir", "rmdir", "chmod", "fchmod", "chown",
    "fchown", "access", "faccessat"
}

PROCESS_SYSCALLS = {
    "execve", "clone", "fork", "vfork", "wait4", "waitpid", "getpid",
    "getppid", "kill", "ptrace", "exit", "exit_group"
}

NETWORK_SYSCALLS = {
    "socket", "connect", "bind", "listen", "accept", "accept4", "sendto",
    "sendmsg", "sendmmsg", "recvfrom", "recvmsg", "recv", "send",
    "setsockopt", "getsockopt", "getpeername", "getsockname", "shutdown"
}

MEMORY_SYSCALLS = {
    "mmap", "mprotect", "munmap", "brk", "mremap"
}

IO_SYSCALLS = {
    "read", "write", "pread64", "pwrite64", "readv", "writev", "ioctl",
    "poll", "ppoll", "select", "pselect6", "epoll_create", "epoll_create1",
    "epoll_ctl", "epoll_wait", "futex"
}

IMPORTANT_SYSCALLS = [
    "open", "openat", "read", "write", "close",
    "stat", "lstat", "fstat", "newfstatat",
    "execve", "clone", "fork", "vfork", "wait4",
    "socket", "connect", "sendto", "sendmsg", "recvfrom", "recvmsg",
    "unlink", "unlinkat", "rename", "renameat", "chmod", "chown",
    "mmap", "mprotect", "munmap", "brk",
    "ioctl", "poll", "futex", "faccessat"
]

def shannon_entropy(counter):
    total = sum(counter.values())
    if total == 0:
        return 0.0
    ent = 0.0
    for c in counter.values():
        p = c / total
        ent -= p * math.log2(p)
    return ent

def count_group(syscalls, group):
    return sum(1 for s in syscalls if s in group)

def unique_group(syscalls, group):
    return len(set(s for s in syscalls if s in group))

def first_position(syscalls, targets):
    for i, s in enumerate(syscalls):
        if s in targets:
            return i
    return -1

def normalized_position(index, total):
    if index < 0 or total == 0:
        return -1.0
    return index / total

rows = []

for folder in sorted(base_dir.iterdir()):
    if not folder.is_dir():
        continue

    syscalls = []
    failed_syscalls = 0
    trace_files = sorted(folder.glob("trace.*"))

    for trace_file in trace_files:
        with open(trace_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = pattern.match(line)
                if m:
                    sc = m.group(1)
                    syscalls.append(sc)
                    if "= -1" in line:
                        failed_syscalls += 1

    total_syscalls = len(syscalls)
    unique_syscalls = len(set(syscalls))
    counts = Counter(syscalls)

    if total_syscalls == 0:
        continue

    top3 = counts.most_common(3)
    top1_ratio = top3[0][1] / total_syscalls if len(top3) >= 1 else 0.0
    top3_ratio = sum(x[1] for x in top3) / total_syscalls if len(top3) > 0 else 0.0

    file_ops_count = count_group(syscalls, FILE_SYSCALLS)
    process_ops_count = count_group(syscalls, PROCESS_SYSCALLS)
    network_ops_count = count_group(syscalls, NETWORK_SYSCALLS)
    memory_ops_count = count_group(syscalls, MEMORY_SYSCALLS)
    io_ops_count = count_group(syscalls, IO_SYSCALLS)

    row = {
        "sample_id": folder.name,
        "label": 0,
        "trace_file_count": len(trace_files),

        "total_syscalls": total_syscalls,
        "unique_syscalls": unique_syscalls,
        "failed_syscalls": failed_syscalls,
        "failed_syscall_ratio": round(failed_syscalls / total_syscalls, 6),

        "top1_syscall_ratio": round(top1_ratio, 6),
        "top3_syscall_ratio": round(top3_ratio, 6),
        "trace_entropy": round(shannon_entropy(counts), 6),

        "file_ops_count": file_ops_count,
        "process_ops_count": process_ops_count,
        "network_ops_count": network_ops_count,
        "memory_ops_count": memory_ops_count,
        "io_ops_count": io_ops_count,

        "file_ops_unique": unique_group(syscalls, FILE_SYSCALLS),
        "process_ops_unique": unique_group(syscalls, PROCESS_SYSCALLS),
        "network_ops_unique": unique_group(syscalls, NETWORK_SYSCALLS),
        "memory_ops_unique": unique_group(syscalls, MEMORY_SYSCALLS),
        "io_ops_unique": unique_group(syscalls, IO_SYSCALLS),

        "file_ops_ratio": round(file_ops_count / total_syscalls, 6),
        "process_ops_ratio": round(process_ops_count / total_syscalls, 6),
        "network_ops_ratio": round(network_ops_count / total_syscalls, 6),
        "memory_ops_ratio": round(memory_ops_count / total_syscalls, 6),
        "io_ops_ratio": round(io_ops_count / total_syscalls, 6),

        "first_execve_pos": round(normalized_position(first_position(syscalls, {"execve"}), total_syscalls), 6),
        "first_connect_pos": round(normalized_position(first_position(syscalls, {"connect"}), total_syscalls), 6),
        "first_socket_pos": round(normalized_position(first_position(syscalls, {"socket"}), total_syscalls), 6),
        "first_write_pos": round(normalized_position(first_position(syscalls, {"write"}), total_syscalls), 6),
        "first_unlink_pos": round(normalized_position(first_position(syscalls, {"unlink", "unlinkat"}), total_syscalls), 6),
        "first_rename_pos": round(normalized_position(first_position(syscalls, {"rename", "renameat"}), total_syscalls), 6),
        "first_mprotect_pos": round(normalized_position(first_position(syscalls, {"mprotect"}), total_syscalls), 6),
        "first_clone_pos": round(normalized_position(first_position(syscalls, {"clone", "fork", "vfork"}), total_syscalls), 6),

        "has_execve": 1 if counts.get("execve", 0) > 0 else 0,
        "has_connect": 1 if counts.get("connect", 0) > 0 else 0,
        "has_socket": 1 if counts.get("socket", 0) > 0 else 0,
        "has_write": 1 if counts.get("write", 0) > 0 else 0,
        "has_unlink": 1 if (counts.get("unlink", 0) + counts.get("unlinkat", 0)) > 0 else 0,
        "has_rename": 1 if (counts.get("rename", 0) + counts.get("renameat", 0)) > 0 else 0,
        "has_chmod": 1 if counts.get("chmod", 0) > 0 else 0,
        "has_mprotect": 1 if counts.get("mprotect", 0) > 0 else 0,

        "has_process_spawn_and_network": 1 if (
            (counts.get("execve", 0) + counts.get("clone", 0) + counts.get("fork", 0) + counts.get("vfork", 0)) > 0
            and network_ops_count > 0
        ) else 0,

        "has_file_write_and_network": 1 if (
            counts.get("write", 0) > 0 and network_ops_count > 0
        ) else 0,
    }

    for sc in IMPORTANT_SYSCALLS:
        row[f"count_{sc}"] = counts.get(sc, 0)
        row[f"ratio_{sc}"] = round(counts.get(sc, 0) / total_syscalls, 6)

    for k in [25, 50, 100]:
        window = syscalls[:k]
        w_total = len(window)

        if w_total == 0:
            row[f"early{k}_unique"] = 0
            row[f"early{k}_file_count"] = 0
            row[f"early{k}_process_count"] = 0
            row[f"early{k}_network_count"] = 0
            row[f"early{k}_has_execve"] = 0
            row[f"early{k}_has_connect"] = 0
            row[f"early{k}_has_write"] = 0
        else:
            row[f"early{k}_unique"] = len(set(window))
            row[f"early{k}_file_count"] = count_group(window, FILE_SYSCALLS)
            row[f"early{k}_process_count"] = count_group(window, PROCESS_SYSCALLS)
            row[f"early{k}_network_count"] = count_group(window, NETWORK_SYSCALLS)
            row[f"early{k}_has_execve"] = 1 if "execve" in window else 0
            row[f"early{k}_has_connect"] = 1 if "connect" in window else 0
            row[f"early{k}_has_write"] = 1 if "write" in window else 0

    rows.append(row)

if not rows:
    print("No rows parsed.")
    raise SystemExit

fieldnames = list(rows[0].keys())

with open(out_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Total npm_benign samples:", len(rows))
print("Total features:", len(fieldnames))
print("Saved to:", out_file)