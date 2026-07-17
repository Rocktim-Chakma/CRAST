import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


def normalize_01(values):
    values = np.asarray(values, dtype=float)
    lo = np.nanmin(values)
    hi = np.nanmax(values)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi == lo:
        return np.zeros_like(values, dtype=float)
    return (values - lo) / (hi - lo)


def rank01(scores):
    return pd.Series(scores).rank(method="average", pct=True).to_numpy()


def get_model_score(model, X):
    if hasattr(model, "predict_proba"):
        score = model.predict_proba(X)[:, 1]
    elif hasattr(model, "decision_function"):
        score = normalize_01(model.decision_function(X))
    else:
        score = model.predict(X).astype(float)
    return np.asarray(score, dtype=float)


def evaluate_from_scores(y_true, scores, threshold=0.5):
    pred = (np.asarray(scores) >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    try:
        auc = roc_auc_score(y_true, scores)
    except Exception:
        auc = np.nan
    return {
        "accuracy": accuracy_score(y_true, pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "malicious_recall": recall_score(y_true, pred, pos_label=1, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "auc": auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "total_error": int(fp + fn),
        "threshold": float(threshold),
    }


def select_source_threshold(y_source, source_scores, objective="f1"):
    thresholds = np.round(np.arange(0.05, 0.96, 0.01), 2)
    best = None
    for t in thresholds:
        m = evaluate_from_scores(y_source, source_scores, threshold=t)
        value = m["f1"] if objective == "f1" else m["balanced_accuracy"]
        row = {"threshold": float(t), "objective_value": float(value), **m}
        if best is None or row["objective_value"] > best["objective_value"]:
            best = row
    return best


def summarize_results(df, group_cols):
    return (
        df.dropna(subset=["f1"])
        .groupby(group_cols)
        .agg(
            accuracy_mean=("accuracy", "mean"),
            accuracy_std=("accuracy", "std"),
            precision_mean=("precision", "mean"),
            malicious_recall_mean=("malicious_recall", "mean"),
            f1_mean=("f1", "mean"),
            f1_std=("f1", "std"),
            total_error_mean=("total_error", "mean"),
            fp_mean=("fp", "mean"),
            fn_mean=("fn", "mean"),
        )
        .reset_index()
        .sort_values(group_cols[:1] + ["f1_mean"], ascending=[True] * len(group_cols[:1]) + [False])
    )
