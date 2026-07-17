import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from .metrics import normalize_01


def select_transferable_features(
    X_source,
    y_source,
    X_target,
    feature_cols,
    seed,
    gamma=1.0,
    filter_mode="q75",
    top_k=100,
    n_estimators=350,
):
    """Registry-aware transferable feature filter: T(f)=U(f)-gamma*B(f)."""
    malware_model = ExtraTreesClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1)
    malware_model.fit(X_source[feature_cols], y_source)
    utility = pd.Series(malware_model.feature_importances_, index=feature_cols)

    X_reg = pd.concat([X_source[feature_cols], X_target[feature_cols]], axis=0, ignore_index=True)
    y_reg = np.array([0] * len(X_source) + [1] * len(X_target))
    registry_model = ExtraTreesClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=-1)
    registry_model.fit(X_reg, y_reg)
    bias = pd.Series(registry_model.feature_importances_, index=feature_cols)

    score_df = pd.DataFrame({
        "feature": feature_cols,
        "malware_utility_raw": utility.reindex(feature_cols).values,
        "registry_bias_raw": bias.reindex(feature_cols).values,
    })
    score_df["malware_utility"] = normalize_01(score_df["malware_utility_raw"])
    score_df["registry_bias"] = normalize_01(score_df["registry_bias_raw"])
    score_df["transferability_score"] = score_df["malware_utility"] - gamma * score_df["registry_bias"]

    if filter_mode == "q75":
        cutoff = score_df["registry_bias"].quantile(0.75)
        candidates = score_df[score_df["registry_bias"] <= cutoff].copy()
    elif filter_mode == "q50":
        cutoff = score_df["registry_bias"].quantile(0.50)
        candidates = score_df[score_df["registry_bias"] <= cutoff].copy()
    else:
        candidates = score_df.copy()

    selected = candidates.sort_values("transferability_score", ascending=False).head(min(top_k, len(candidates)))["feature"].tolist()
    score_df["selected"] = score_df["feature"].isin(selected).astype(int)
    return selected, score_df.sort_values("transferability_score", ascending=False)
