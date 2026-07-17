def infer_feature_group(feature_name: str) -> str:
    name = feature_name.lower()
    if any(k in name for k in ["open", "read", "write", "file", "path", "unlink", "rename", "chmod", "chown", "mkdir", "rmdir", "stat", "access"]):
        return "file_activity"
    if any(k in name for k in ["socket", "connect", "network", "dns", "inet", "outbound"]):
        return "network_activity"
    if any(k in name for k in ["exec", "fork", "clone", "process", "spawn", "shell", "bash", "sh_"]):
        return "process_execution"
    if any(k in name for k in ["tmp", "home", "hidden", "ssh", "profile", "bashrc", "node_modules", "site-packages", "cache"]):
        return "path_context"
    if any(k in name for k in ["ratio", "entropy", "score", "complexity", "pressure", "failed"]):
        return "aggregate_behavior"
    return "other"


def build_feature_groups(cols):
    groups = {}
    for c in cols:
        groups.setdefault(infer_feature_group(c), []).append(c)
    return groups
