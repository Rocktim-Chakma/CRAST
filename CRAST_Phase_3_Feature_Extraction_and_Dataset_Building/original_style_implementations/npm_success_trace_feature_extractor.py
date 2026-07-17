from pathlib import Path
import csv
import re
from collections import Counter, defaultdict

BASE_DIR = Path(r"D:\npm malicious logs")
WORKERS = ["worker1", "worker2", "worker3", "worker4", "worker5"]
OUTPUT_CSV = BASE_DIR / "npm_success_features_expanded.csv"

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
PKG_MGR_TOKENS = ["npm", "npx", "yarn", "pnpm"]
NET_TOOL_TOKENS = ["curl", "wget"]
SCRIPT_ENGINE_TOKENS = ["node", "python", "python3"]
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
    trace_files = sorted(logs_dir.glob(f"{package_name}_node*.trace.*"))

    runtimes = set()
    for tf in trace_files:
        m = re.match(rf"^{re.escape(package_name)}_(node\d+)\.trace\.\d+$", tf.name)
        if m:
            runtimes.add(m.group(1))

    runtime = sorted(runtimes)[0] if runtimes else "unknown"
    err_file = logs_dir / f"{package_name}_{runtime}.err" if runtime != "unknown" else None

    return {
        "trace_files": trace_files,
        "runtime": runtime,
        "err_file": err_file if err_file and err_file.exists() else None,
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
        "touched_node_modules": 0,
        "touched_package_json": 0,
        "touched_lockfile": 0,
        "touched_cache": 0,
        "touched_config": 0,
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
                        elif ".npmrc" in pl:
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

                    if ".npmrc" in pl:
                        path_counts["npmrc_path_count"] += 1

                    if any(x in pl for x in [".bashrc", ".profile", ".zshrc", ".bash_profile", ".npmrc"]):
                        path_counts["startup_hidden_path_count"] += 1

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

                    if "node_modules" in pl:
                        flags["touched_node_modules"] = 1
                        path_counts["node_modules_path_count"] += 1

                    if pl.endswith("package.json") or "package.json" in pl:
                        flags["touched_package_json"] = 1
                        path_counts["package_json_path_count"] += 1

                    if "package-lock.json" in pl or "yarn.lock" in pl or "pnpm-lock" in pl:
                        flags["touched_lockfile"] = 1
                        path_counts["lockfile_path_count"] += 1

                    if ".cache" in pl or "/cache/" in pl:
                        flags["touched_cache"] = 1
                        path_counts["cache_path_count"] += 1

                    if ".config" in pl or "/config/" in pl:
                        flags["touched_config"] = 1
                        path_counts["config_path_count"] += 1

                if sc == "connect":
                    flags["outbound_network"] = 1

                if sc == "execve":
                    em = exec_target_pattern.search(s)
                    if em:
                        tgt = em.group(1).lower()
                        exec_targets[tgt] += 1

                    if any(x in low for x in ['"sh"', '"bash"', '"dash"', '"zsh"', '/sh"', '/bash"', '/dash"', '/zsh"']):
                        flags["spawned_shell"] = 1
                    if any(x in low for x in ['"npm"', '"npx"', '"yarn"', '"pnpm"', '/npm"', '/npx"', '/yarn"', '/pnpm"']):
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
    fd_manipulation_count = sum(syscall_counts[s] for s in FD_SYSCALLS)
    metadata_syscall_count = sum(syscall_counts[s] for s in METADATA_SYSCALLS)
    ipc_syscall_count = syscall_counts["pipe"] + syscall_counts["pipe2"]

    file_create_count = syscall_counts["open"] + syscall_counts["openat"] + syscall_counts["mkdir"] + syscall_counts["mkdirat"]
    file_delete_count = syscall_counts["unlink"] + syscall_counts["unlinkat"] + syscall_counts["rmdir"]
    file_rename_count = syscall_counts["rename"] + syscall_counts["renameat"]
    file_permission_change_count = permission_syscall_count
    directory_create_count = syscall_counts["mkdir"] + syscall_counts["mkdirat"]
    directory_delete_count = syscall_counts["rmdir"]

    child_process_exec_count = syscall_counts["execve"]
    unique_exec_targets = len(exec_targets)
    shell_exec_count = sum(v for k, v in exec_targets.items() if any(tok in k for tok in SHELL_TOKENS))
    script_engine_exec_count = sum(v for k, v in exec_targets.items() if any(tok in k for tok in SCRIPT_ENGINE_TOKENS))
    network_tool_exec_count = sum(v for k, v in exec_targets.items() if any(tok in k for tok in NET_TOOL_TOKENS))
    system_tool_exec_count = sum(v for k, v in exec_targets.items() if any(tok in k for tok in SYSTEM_TOOL_TOKENS))

    top_counts = sorted(syscall_counts.values(), reverse=True)
    top1_syscall_ratio = safe_div(top_counts[0] if len(top_counts) > 0 else 0, total_syscalls)
    top3_syscall_ratio = safe_div(sum(top_counts[:3]), total_syscalls)
    top5_syscall_ratio = safe_div(sum(top_counts[:5]), total_syscalls)

    row = {
        "total_lines": total_lines,
        "total_syscalls": total_syscalls,
        "unique_syscalls": len(syscall_counts),
        "trace_shard_count": len(trace_files),
        "avg_lines_per_shard": safe_div(total_lines, len(trace_files)),
        "avg_syscalls_per_shard": safe_div(total_syscalls, len(trace_files)),
        "max_lines_in_single_shard": max(shard_line_counts) if shard_line_counts else 0,
        "min_lines_in_single_shard": min(shard_line_counts) if shard_line_counts else 0,

        "open_count": syscall_counts["open"],
        "openat_count": syscall_counts["openat"],
        "read_count": syscall_counts["read"],
        "write_count": syscall_counts["write"],
        "close_count": syscall_counts["close"],
        "stat_count": syscall_counts["stat"],
        "lstat_count": syscall_counts["lstat"],
        "newfstatat_count": syscall_counts["newfstatat"],
        "access_count": syscall_counts["access"],
        "faccessat_count": syscall_counts["faccessat"],

        "execve_count": syscall_counts["execve"],
        "clone_count": syscall_counts["clone"],
        "fork_count": syscall_counts["fork"],
        "vfork_count": syscall_counts["vfork"],
        "wait4_count": syscall_counts["wait4"],
        "kill_count": syscall_counts["kill"],

        "socket_count": syscall_counts["socket"],
        "connect_count": syscall_counts["connect"],
        "accept_count": syscall_counts["accept"],
        "bind_count": syscall_counts["bind"],
        "listen_count": syscall_counts["listen"],
        "sendto_count": syscall_counts["sendto"],
        "recvfrom_count": syscall_counts["recvfrom"],
        "sendmsg_count": syscall_counts["sendmsg"],
        "recvmsg_count": syscall_counts["recvmsg"],

        "unlink_count": syscall_counts["unlink"],
        "unlinkat_count": syscall_counts["unlinkat"],
        "rename_count": syscall_counts["rename"],
        "renameat_count": syscall_counts["renameat"],
        "mkdir_count": syscall_counts["mkdir"],
        "mkdirat_count": syscall_counts["mkdirat"],
        "rmdir_count": syscall_counts["rmdir"],
        "symlink_count": syscall_counts["symlink"],
        "symlinkat_count": syscall_counts["symlinkat"],
        "link_count": syscall_counts["link"],
        "linkat_count": syscall_counts["linkat"],

        "chmod_count": syscall_counts["chmod"],
        "fchmod_count": syscall_counts["fchmod"],
        "fchmodat_count": syscall_counts["fchmodat"],
        "chown_count": syscall_counts["chown"],
        "fchown_count": syscall_counts["fchown"],
        "fchownat_count": syscall_counts["fchownat"],

        "chdir_count": syscall_counts["chdir"],
        "getcwd_count": syscall_counts["getcwd"],
        "dup_count": syscall_counts["dup"],
        "dup2_count": syscall_counts["dup2"],
        "dup3_count": syscall_counts["dup3"],
        "pipe_count": syscall_counts["pipe"],
        "pipe2_count": syscall_counts["pipe2"],

        "mmap_count": syscall_counts["mmap"],
        "munmap_count": syscall_counts["munmap"],
        "mprotect_count": syscall_counts["mprotect"],
        "brk_count": syscall_counts["brk"],

        "file_syscall_count": file_syscall_count,
        "network_syscall_count": network_syscall_count,
        "process_syscall_count": process_syscall_count,
        "permission_syscall_count": permission_syscall_count,
        "memory_syscall_count": memory_syscall_count,
        "directory_syscall_count": directory_syscall_count,
        "link_syscall_count": link_syscall_count,
        "fd_manipulation_count": fd_manipulation_count,
        "metadata_syscall_count": metadata_syscall_count,
        "ipc_syscall_count": ipc_syscall_count,

        "file_create_count": file_create_count,
        "file_delete_count": file_delete_count,
        "file_rename_count": file_rename_count,
        "file_permission_change_count": file_permission_change_count,
        "directory_create_count": directory_create_count,
        "directory_delete_count": directory_delete_count,

        "tmp_path_count": path_counts["tmp_path_count"],
        "home_path_count": path_counts["home_path_count"],
        "hidden_path_count": path_counts["hidden_path_count"],
        "sensitive_hidden_path_count": path_counts["sensitive_hidden_path_count"],
        "ssh_path_count": path_counts["ssh_path_count"],
        "bashrc_path_count": path_counts["bashrc_path_count"],
        "profile_path_count": path_counts["profile_path_count"],
        "npmrc_path_count": path_counts["npmrc_path_count"],
        "startup_hidden_path_count": path_counts["startup_hidden_path_count"],
        "etc_path_count": path_counts["etc_path_count"],
        "proc_path_count": path_counts["proc_path_count"],
        "dev_path_count": path_counts["dev_path_count"],
        "var_path_count": path_counts["var_path_count"],
        "node_modules_path_count": path_counts["node_modules_path_count"],
        "package_json_path_count": path_counts["package_json_path_count"],
        "lockfile_path_count": path_counts["lockfile_path_count"],
        "cache_path_count": path_counts["cache_path_count"],
        "config_path_count": path_counts["config_path_count"],

        "child_process_exec_count": child_process_exec_count,
        "unique_exec_targets": unique_exec_targets,
        "shell_exec_count": shell_exec_count,
        "script_engine_exec_count": script_engine_exec_count,
        "network_tool_exec_count": network_tool_exec_count,
        "system_tool_exec_count": system_tool_exec_count,

        "unique_to_total_ratio": safe_div(len(syscall_counts), total_syscalls),
        "file_ratio": safe_div(file_syscall_count, total_syscalls),
        "network_ratio": safe_div(network_syscall_count, total_syscalls),
        "process_ratio": safe_div(process_syscall_count, total_syscalls),
        "permission_ratio": safe_div(permission_syscall_count, total_syscalls),
        "memory_ratio": safe_div(memory_syscall_count, total_syscalls),
        "metadata_ratio": safe_div(metadata_syscall_count, total_syscalls),
        "read_ratio": safe_div(syscall_counts["read"], total_syscalls),
        "write_ratio": safe_div(syscall_counts["write"], total_syscalls),
        "open_ratio": safe_div(syscall_counts["open"] + syscall_counts["openat"], total_syscalls),
        "exec_ratio": safe_div(syscall_counts["execve"], total_syscalls),
        "connect_ratio": safe_div(syscall_counts["connect"], total_syscalls),
        "write_to_read_ratio": safe_div(syscall_counts["write"], syscall_counts["read"]),
        "exec_to_process_ratio": safe_div(syscall_counts["execve"], process_syscall_count),
        "network_to_file_ratio": safe_div(network_syscall_count, file_syscall_count),
        "permission_to_file_ratio": safe_div(permission_syscall_count, file_syscall_count),

        "top1_syscall_ratio": top1_syscall_ratio,
        "top3_syscall_ratio": top3_syscall_ratio,
        "top5_syscall_ratio": top5_syscall_ratio,

        "spawned_multiple_children": 1 if (syscall_counts["clone"] + syscall_counts["fork"] + syscall_counts["vfork"]) > 1 else 0,
        "socket_then_connect_flag": 1 if syscall_counts["socket"] > 0 and syscall_counts["connect"] > 0 else 0,
        "send_without_recv_flag": 1 if (syscall_counts["sendto"] + syscall_counts["sendmsg"]) > 0 and (syscall_counts["recvfrom"] + syscall_counts["recvmsg"]) == 0 else 0,
        "recv_without_send_flag": 1 if (syscall_counts["recvfrom"] + syscall_counts["recvmsg"]) > 0 and (syscall_counts["sendto"] + syscall_counts["sendmsg"]) == 0 else 0,
        "high_network_ratio_flag": 1 if safe_div(network_syscall_count, total_syscalls) > 0.05 else 0,
        "multi_file_touch_flag": 1 if (file_create_count + file_delete_count + file_rename_count) > 10 else 0,
        "high_write_ratio_flag": 1 if safe_div(syscall_counts["write"], total_syscalls) > 0.10 else 0,
        "hidden_file_touch_flag": flags["touched_hidden_path"],
        "ssh_touch_flag": flags["touched_ssh"],
        "bashrc_touch_flag": flags["touched_bashrc"],
        "profile_touch_flag": flags["touched_profile"],
        "tmp_then_exec_flag": 1 if flags["touched_tmp"] and syscall_counts["execve"] > 0 else 0,
        "writes_to_hidden_location_flag": 1 if flags["touched_hidden_path"] and syscall_counts["write"] > 0 else 0,
        "writes_to_startup_location_flag": 1 if (flags["touched_bashrc"] or flags["touched_profile"]) and syscall_counts["write"] > 0 else 0,
        "permission_change_after_write_flag": 1 if syscall_counts["write"] > 0 and permission_syscall_count > 0 else 0,
        "exec_after_download_flag": 1 if flags["used_curl_wget"] and syscall_counts["execve"] > 0 else 0,
        "open_then_read_flag": 1 if syscall_counts["open"] + syscall_counts["openat"] > 0 and syscall_counts["read"] > 0 else 0,
        "open_then_write_flag": 1 if syscall_counts["open"] + syscall_counts["openat"] > 0 and syscall_counts["write"] > 0 else 0,
        "write_then_exec_flag": 1 if syscall_counts["write"] > 0 and syscall_counts["execve"] > 0 else 0,
        "connect_then_write_flag": 1 if syscall_counts["connect"] > 0 and syscall_counts["write"] > 0 else 0,
        "connect_then_exec_flag": 1 if syscall_counts["connect"] > 0 and syscall_counts["execve"] > 0 else 0,
        "tmp_then_write_flag": 1 if flags["touched_tmp"] and syscall_counts["write"] > 0 else 0,

        "process_spawn_intensity": safe_div(process_syscall_count, total_syscalls),
        "file_touch_intensity": safe_div(file_create_count + file_delete_count + file_rename_count, total_syscalls),
        "network_activity_intensity": safe_div(network_syscall_count, total_syscalls),
        "path_suspicion_score": (
            flags["touched_tmp"] + flags["touched_hidden_path"] + flags["touched_sensitive_hidden_path"] +
            flags["touched_ssh"] + flags["touched_bashrc"] + flags["touched_profile"] +
            flags["touched_etc"] + flags["touched_proc"]
        ),
        "stealth_score": (
            flags["touched_hidden_path"] + flags["touched_sensitive_hidden_path"] +
            flags["touched_ssh"] + (1 if safe_div(network_syscall_count, total_syscalls) > 0.05 else 0) +
            (1 if syscall_counts["execve"] > 0 else 0)
        ),
        "execution_complexity_score": unique_exec_targets + shell_exec_count + script_engine_exec_count + network_tool_exec_count,
        "filesystem_pressure_score": file_syscall_count + file_create_count + file_delete_count + file_rename_count,
    }

    row.update(flags)
    return row


def build_dataset():
    rows = []
    summary = defaultdict(int)

    for worker in WORKERS:
        success_path = BASE_DIR / worker / "results" / worker / "success.txt"
        logs_dir = BASE_DIR / worker / "logs_safe" / worker

        success_entries = parse_success_file(success_path)
        print(f"[{worker}] success entries: {len(success_entries)}")

        for package_name in success_entries:
            grp = find_trace_group(logs_dir, package_name)
            trace_files = grp["trace_files"]

            if not trace_files:
                summary["missing_trace_group"] += 1
                continue

            feats = parse_trace_files(trace_files)
            summary["parsed_ok"] += 1

            rows.append({
                "package_name": package_name,
                "runtime": grp["runtime"],
                "label": 1,
                "registry": "npm",
                "status_success": 1,
                "err_found": 1 if grp["err_file"] else 0,
                **feats
            })

    return rows, summary


def write_csv(rows, output_csv: Path):
    if not rows:
        print("No rows to write.")
        return

    fieldnames = list(rows[0].keys())
    for row in rows[1:]:
        for k in row.keys():
            if k not in fieldnames:
                fieldnames.append(k)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV written: {output_csv}")


if __name__ == "__main__":
    rows, summary = build_dataset()
    write_csv(rows, OUTPUT_CSV)

    print("\nSummary")
    print("-------")
    print(f"Total rows: {len(rows)}")
    for k, v in summary.items():
        print(f"{k}: {v}")