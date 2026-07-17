import re
import numpy as np
import pandas as pd
from .config import LABEL_COL, PACKAGE_COL


def make_package_group(package_names):
    groups = []
    for name in package_names.astype(str):
        g = name.lower()
        g = re.sub(r"\.(tgz|tar\.gz|zip|whl)$", "", g)
        g = re.sub(r"[-_]?v?\d+(\.\d+){1,4}.*$", "", g)
        g = re.sub(r"\s+", "", g)
        groups.append(g if g else name.lower())
    return np.array(groups)


def duplicate_conflict_audit(df, feature_cols, name):
    X = df[feature_cols].copy()
    hashes = pd.util.hash_pandas_object(X, index=False)
    if PACKAGE_COL in df.columns:
        tmp = df[[PACKAGE_COL, LABEL_COL]].copy()
    else:
        tmp = df[[LABEL_COL]].copy()
        tmp[PACKAGE_COL] = np.arange(len(tmp)).astype(str)
    tmp["feature_hash"] = hashes
    grp = (
        tmp.groupby("feature_hash")
        .agg(
            registry=(LABEL_COL, lambda s: name),
            count=(LABEL_COL, "size"),
            n_labels=(LABEL_COL, "nunique"),
            labels=(LABEL_COL, lambda s: sorted(set(s))),
            packages=(PACKAGE_COL, lambda s: list(s)[:10]),
        )
        .sort_values(["n_labels", "count"], ascending=[False, False])
    )
    dup_only = grp[grp["count"] > 1]
    cross_label = dup_only[dup_only["n_labels"] > 1]
    return dup_only.reset_index(), cross_label.reset_index()
