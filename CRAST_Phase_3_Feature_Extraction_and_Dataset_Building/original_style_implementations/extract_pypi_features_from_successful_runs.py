from pathlib import Path
import csv
import re
from collections import Counter

# Original-style PyPI successful-run feature extractor.
# This script follows the same successful-run filtering idea as the NPM worker
# success extractor, but is adapted for PyPI trace outputs.
#
# "successful" here means trace collection/install execution completed and the
# package appears in a success/completed list. It does NOT mean benign/malicious.
#
# Update BASE_DIR, WORKERS, and label/registry if your local folder names differ.

BASE_DIR = Path(r"D:\pypi logs")
WORKERS = ["worker1", "worker2", "worker3", "worker4", "worker5"]
OUTPUT_CSV = BASE_DIR / "pypi_success_features_expanded.csv"

REGISTRY = "pypi"

FILE_SYSCALLS = {
    "open", "openat", "read", "write", "close", "stat", "lstat", "fstat",
    "newfstatat", "access", "faccessat", "unlink", "unlinkat", "rename",
    "renameat", "mkdir", "mkdirat", "rmdir"
}
NETWORK_SYSCALLS = {
    "socket", "connect", "accept", "bind", "listen",
    "sendto", "recvfrom", "sendmsg", "recvmsg"
}
PROCESS_SYSCALLS = {
    "execve", "clone", "fork", "vfork", "wait4", "kill"
}
PERM_SYSCALLS = {
    "chmod", "fchmod", "fchmodat", "chown", "fchown", "fchownat"
}
MEMORY_SYSCALLS = {"mmap", "munmap", "mprotect", "brk"}
DIRECTORY_SYSCALLS = {"mkdir", "mkdirat", "rmdir", "chdir", "getcwd"}
LINK_SYSCALLS = {"link", "linkat", "symlink", "symlinkat", "rename", "renameat"}
FD_SYSCALLS = {"dup", "dup2", "dup3", "pipe", "pipe2", "close"}
METADATA_SYSCALLS = {"stat", "lstat", "fstat", "newfstatat", "access", "faccessat"}

SHELL_TOKENS = ["sh", "bash", "dash", "zsh"]
PKG_MGR_TOKENS = ["pip", "pip3", "python", "python3", "python3.8", "python3.10", "python3.11"]
NET_TOOL_TOKENS = ["curl", "wget"]
SCRIPT_ENGINE_TOKENS = ["python", "python3", "node"]
SYSTEM_TOOL_TOKENS = ["chmod", "tar", "unzip", "base64", "git"]


def safe_div(a, b):
    return a / b if b else 0.0


def parse_success_file(success_path: Path):
    items = []
    if not success_path.exists():
        return items

    with success_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(line)
    return items


def find_trace_group(logs_dir: Path, package_name: str):
    # Supported patterns:
    #   package.trace.1234
    #   package_python.trace.1234
    #   package_py310.trace.1234
    #   package/trace.1234
    trace_files = sorted(logs_dir.glob(f"{package_name}*.trace.*"))

    if not trace_files:
        package_dir = logs_dir / package_name
        if package_dir.exists():
            trace_files = sorted(package_dir.glob("trace.*"))

    runtime = "python"
    err_candidates = [
        logs_dir / f"{package_name}.err",
        logs_dir / f"{package_name}_python.err",
        logs_dir / f"{package_name}_py310.err",
        logs_dir / package_name / "run.stderr.log",
        logs_dir / package_name / "stderr.log",
    ]
    err_file = next((p for p in err_candidates if p.exists()), None)

    return {
        "trace_files": trace_files,
        "runtime": runtime,
        "err_file": err_file,
    }


def parse_trace_files(trace_files):
    syscall_counts = Counter()
    exec_targets = Counter()
    path_counts = Counter()
    total_lines = 0
    total_syscalls = 0
    shard_line_counts = []

    flags = {
        "touched_tmp": 0,
        "touched_home": 0,
        "touched_hidden_path": 0,
        "touched_sensitive_hidden_path": 0,
        "touched_ssh": 0,
        "touched_bashrc": 0,
        "touched_profile": 0,
        "touched_etc": 0,
        "touched_proc": 0,
        "touched_dev": 0,
        "touched_var": 0,
        "touched_cache": 0,
        "touched_config": 0,

        # PyPI/Python-specific path indicators
        "touched_site_packages": 0,
        "touched_dist_info": 0,
        "touched_egg_info": 0,
        "touched_setup_py": 0,
        "touched_pyproject": 0,
        "touched_requirements": 0,
        "touched_pyvenv_cfg": 0,
        "touched_venv_path": 0,

        "spawned_shell": 0,
        "package_manager_invocation": 0,
        "used_curl_wget": 0,
        "spawned_node_python": 0,
        "used_git": 0,
        "used_chmod_command": 0,
        "used_tar_command": 0,
        "used_unzip_command": 0,
        "used_base64_command": 0,
        "used_sh_c_flag": 0,
        "outbound_network": 0,
    }

    syscall_pattern = re.compile(r'(?<![A-Za-z0-9_])([a-zA-Z_][a-zA-Z0-9_]*)\(')
    quoted_path_pattern = re.compile(r'"([^"]+)"')
    exec_target_pattern = re.compile(r'execve\("([^"]+)"')

    for tf in trace_files:
        shard_lines = 0

        with tf.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                total_lines += 1
                shard_lines += 1
                s = line.strip()
                low = s.lower()

                m = syscall_pattern.search(s)
                if not m:
                    continue

                sc = m.group(1)
                syscall_counts[sc] += 1
                total_syscalls += 1

                for p in quoted_path_pattern.findall(s):
                    pl = p.lower()

                    if "/tmp" in pl:
                        flags["touched_tmp"] = 1
                        path_counts["tmp_path_count"] += 1

                    if "/home/" in pl:
                        flags["touched_home"] = 1
                        path_counts["home_path_count"] += 1

                    hidden_match = re.search(r'/\.[^/\s"\']+', pl)
                    if hidden_match:
                        flags["touched_hidden_path"] = 1
                        path_counts["hidden_path_count"] += 1

                        sensitive_hidden = False
                        if ".ssh" in pl:
                            sensitive_hidden = True
                        elif ".bashrc" in pl:
                            sensitive_hidden = True
                        elif ".profile" in pl:
                            sensitive_hidden = True
                        elif ".pypirc" in pl or "pip.conf" in pl:
                            sensitive_hidden = True
                        elif re.search(r'/\.(config|local|cache)/', pl):
                            sensitive_hidden = True
                        elif re.search(r'/\.[^/]+rc$', pl):
                            sensitive_hidden = True

                        if sensitive_hidden:
                            flags["touched_sensitive_hidden_path"] = 1
                            path_counts["sensitive_hidden_path_count"] += 1

                    if ".ssh" in pl:
                        flags["touched_ssh"] = 1
                        path_counts["ssh_path_count"] += 1

                    if ".bashrc" in pl:
                        flags["touched_bashrc"] = 1
                        path_counts["bashrc_path_count"] += 1

                    if ".profile" in pl:
                        flags["touched_profile"] = 1
                        path_counts["profile_path_count"] += 1

                    if pl.startswith("/etc/") or "/etc/" in pl:
                        flags["touched_etc"] = 1
                        path_counts["etc_path_count"] += 1

                    if pl.startswith("/proc/") or "/proc/" in pl:
                        flags["touched_proc"] = 1
                        path_counts["proc_path_count"] += 1

                    if pl.startswith("/dev/") or "/dev/" in pl:
                        flags["touched_dev"] = 1
                        path_counts["dev_path_count"] += 1

                    if pl.startswith("/var/") or "/var/" in pl:
                        flags["touched_var"] = 1
                        path_counts["var_path_count"] += 1

                    if ".cache" in pl or "/cache/" in pl:
                        flags["touched_cache"] = 1
                        path_counts["cache_path_count"] += 1

                    if ".config" in pl or "/config/" in pl:
                        flags["touched_config"] = 1
                        path_counts["config_path_count"] += 1

                    if "site-packages" in pl:
                        flags["touched_site_packages"] = 1
                        path_counts["site_packages_path_count"] += 1

                    if ".dist-info" in pl:
                        flags["touched_dist_info"] = 1
                        path_counts["dist_info_path_count"] += 1

                    if ".egg-info" in pl:
                        flags["touched_egg_info"] = 1
                        path_counts["egg_info_path_count"] += 1

                    if pl.endswith("setup.py") or "/setup.py" in pl:
                        flags["touched_setup_py"] = 1
                        path_counts["setup_py_path_count"] += 1

                    if "pyproject.toml" in pl:
                        flags["touched_pyproject"] = 1
                        path_counts["pyproject_path_count"] += 1

                    if "requirements.txt" in pl:
                        flags["touched_requirements"] = 1
                        path_counts["requirements_path_count"] += 1

                    if "pyvenv.cfg" in pl:
                        flags["touched_pyvenv_cfg"] = 1
                        path_counts["pyvenv_cfg_path_count"] += 1

                    if "/venv/" in pl or "/.venv/" in pl or "\\venv\\" in pl or "\\.venv\\" in pl:
                        flags["touched_venv_path"] = 1
                        path_counts["venv_path_count"] += 1

                if sc == "connect":
                    flags["outbound_network"] = 1

                if sc == "execve":
                    em = exec_target_pattern.search(s)
                    if em:
                        tgt = em.group(1).lower()
                        exec_targets[tgt] += 1

                    if any(x in low for x in ['"sh"', '"bash"', '"dash"', '"zsh"', '/sh"', '/bash"', '/dash"', '/zsh"']):
                        flags["spawned_shell"] = 1
                    if any(x in low for x in ['"pip"', '"pip3"', '/pip"', '/pip3"', '"python"', '"python3"', '/python"', '/python3"']):
                        flags["package_manager_invocation"] = 1
                    if any(x in low for x in ['"curl"', '"wget"', '/curl"', '/wget"']):
                        flags["used_curl_wget"] = 1
                    if any(x in low for x in ['"node"', '"python"', '"python3"', '/node"', '/python"', '/python3"']):
                        flags["spawned_node_python"] = 1
                    if any(x in low for x in ['"git"', '/git"']):
                        flags["used_git"] = 1
                    if any(x in low for x in ['"chmod"', '/chmod"']):
                        flags["used_chmod_command"] = 1
                    if any(x in low for x in ['"tar"', '/tar"']):
                        flags["used_tar_command"] = 1
                    if any(x in low for x in ['"unzip"', '/unzip"']):
                        flags["used_unzip_command"] = 1
                    if any(x in low for x in ['"base64"', '/base64"']):
                        flags["used_base64_command"] = 1
                    if ',"-c"' in low or '"-c"' in low:
                        flags["used_sh_c_flag"] = 1

        shard_line_counts.append(shard_lines)

    file_syscall_count = sum(syscall_counts[s] for s in FILE_SYSCALLS)
    network_syscall_count = sum(syscall_counts[s] for s in NETWORK_SYSCALLS)
    process_syscall_count = sum(syscall_counts[s] for s in PROCESS_SYSCALLS)
    permission_syscall_count = sum(syscall_counts[s] for s in PERM_SYSCALLS)
    memory_syscall_count = sum(syscall_counts[s] for s in MEMORY_SYSCALLS)
    directory_syscall_count = sum(syscall_counts[s] for s in DIRECTORY_SYSCALLS)
    link_syscall_count = sum(syscall_counts[s] for s in LINK_SYSCALLS)
    fd_syscall_count = sum(syscall_counts[s] for s in FD_SYSCALLS)
    metadata_syscall_count = sum(syscall_counts[s] for s in METADATA_SYSCALLS)

    row = {
        "trace_file_count": len(trace_files),
        "trace_line_count": total_lines,
        "trace_shard_min_lines": min(shard_line_counts) if shard_line_counts else 0,
        "trace_shard_max_lines": max(shard_line_counts) if shard_line_counts else 0,
        "trace_shard_avg_lines": round(safe_div(sum(shard_line_counts), len(shard_line_counts)), 6),

        "total_syscalls": total_syscalls,
        "unique_syscalls": len(syscall_counts),
        "file_syscall_count": file_syscall_count,
        "network_syscall_count": network_syscall_count,
        "process_syscall_count": process_syscall_count,
        "permission_syscall_count": permission_syscall_count,
        "memory_syscall_count": memory_syscall_count,
        "directory_syscall_count": directory_syscall_count,
        "link_syscall_count": link_syscall_count,
        "fd_syscall_count": fd_syscall_count,
        "metadata_syscall_count": metadata_syscall_count,

        "file_ratio": round(safe_div(file_syscall_count, total_syscalls), 6),
        "network_ratio": round(safe_div(network_syscall_count, total_syscalls), 6),
        "process_ratio": round(safe_div(process_syscall_count, total_syscalls), 6),
        "permission_ratio": round(safe_div(permission_syscall_count, total_syscalls), 6),
        "memory_ratio": round(safe_div(memory_syscall_count, total_syscalls), 6),
        "directory_ratio": round(safe_div(directory_syscall_count, total_syscalls), 6),
        "link_ratio": round(safe_div(link_syscall_count, total_syscalls), 6),
        "fd_ratio": round(safe_div(fd_syscall_count, total_syscalls), 6),
        "metadata_ratio": round(safe_div(metadata_syscall_count, total_syscalls), 6),

        "top_exec_target_count": exec_targets.most_common(1)[0][1] if exec_targets else 0,
        "unique_exec_targets": len(exec_targets),
    }

    for k, v in flags.items():
        row[k] = v

    for k, v in path_counts.items():
        row[k] = v

    important_syscalls = sorted(
        FILE_SYSCALLS | NETWORK_SYSCALLS | PROCESS_SYSCALLS | PERM_SYSCALLS |
        MEMORY_SYSCALLS | DIRECTORY_SYSCALLS | LINK_SYSCALLS | FD_SYSCALLS |
        METADATA_SYSCALLS
    )
    for sc in important_syscalls:
        row[f"count_{sc}"] = syscall_counts.get(sc, 0)
        row[f"ratio_{sc}"] = round(safe_div(syscall_counts.get(sc, 0), total_syscalls), 6)

    row["path_suspicion_score"] = (
        flags["touched_sensitive_hidden_path"]
        + flags["touched_ssh"]
        + flags["touched_etc"]
        + flags["touched_proc"]
        + flags["touched_dev"]
        + flags["used_sh_c_flag"]
    )

    row["stealth_score"] = (
        flags["touched_hidden_path"]
        + flags["touched_sensitive_hidden_path"]
        + flags["used_base64_command"]
        + flags["used_sh_c_flag"]
    )

    row["execution_complexity_score"] = (
        flags["spawned_shell"]
        + flags["package_manager_invocation"]
        + flags["spawned_node_python"]
        + flags["used_git"]
        + flags["used_tar_command"]
        + flags["used_unzip_command"]
    )

    row["filesystem_pressure_score"] = (
        row["file_ratio"]
        + row["directory_ratio"]
        + row["metadata_ratio"]
        + row["link_ratio"]
    )

    row["outbound_or_tool_network_score"] = (
        flags["outbound_network"]
        + flags["used_curl_wget"]
    )

    return row


def main():
    rows = []

    for worker in WORKERS:
        worker_dir = BASE_DIR / worker
        if not worker_dir.exists():
            continue

        success_candidates = [
            worker_dir / "success.txt",
            worker_dir / "completed_packages.txt",
            worker_dir / "completed.txt",
        ]
        success_file = next((p for p in success_candidates if p.exists()), None)
        if success_file is None:
            continue

        logs_dir_candidates = [
            worker_dir / "logs",
            worker_dir / "logs_safe",
            worker_dir / "traces",
            worker_dir,
        ]
        logs_dir = next((p for p in logs_dir_candidates if p.exists()), worker_dir)

        for package_name in parse_success_file(success_file):
            group = find_trace_group(logs_dir, package_name)
            trace_files = group["trace_files"]

            if not trace_files:
                continue

            features = parse_trace_files(trace_files)

            row = {
                "sample_id": package_name,
                "registry": REGISTRY,
                "worker": worker,
                "runtime": group["runtime"],
                "status_success": 1,
            }
            row.update(features)
            rows.append(row)

    if not rows:
        print("No successful PyPI trace rows parsed.")
        return

    # Use stable union of columns because path-count columns can vary per sample.
    fieldnames = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print("Total successful PyPI samples:", len(rows))
    print("Total columns:", len(fieldnames))
    print("Saved to:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
