import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from .metrics import get_model_score, evaluate_from_scores, select_source_threshold, rank01
from .models import source_oof_scores, model_factories, filter_model_factories
from .feature_selection import select_transferable_features


def rank_threshold_transfer(source_scores, source_threshold, target_scores):
    source_pred_rate = float(np.mean(np.asarray(source_scores) >= source_threshold))
    source_pred_rate = min(max(source_pred_rate, 1e-6), 1 - 1e-6)
    target_threshold = float(np.quantile(target_scores, 1 - source_pred_rate))
    return target_threshold, source_pred_rate


def mean_std_align(target_scores, source_scores):
    target_scores = np.asarray(target_scores, dtype=float)
    source_scores = np.asarray(source_scores, dtype=float)
    mu_s, sd_s = np.mean(source_scores), np.std(source_scores)
    mu_t, sd_t = np.mean(target_scores), np.std(target_scores)
    if sd_t == 0:
        return target_scores
    if sd_s == 0:
        sd_s = 1.0
    return np.clip(((target_scores - mu_t) / sd_t) * sd_s + mu_s, 0, 1)


def run_source_only_transfer(source_name, target_name, X_source, y_source, X_target, y_target, model_name, factory, seed, n_splits=5):
    source_scores = source_oof_scores(factory, X_source, y_source, seed, n_splits=n_splits)
    threshold_info = select_source_threshold(y_source, source_scores, objective="f1")
    source_threshold = threshold_info["threshold"]
    model = factory(seed)
    model.fit(X_source, y_source)
    target_scores = get_model_score(model, X_target)
    metrics = evaluate_from_scores(y_target, target_scores, source_threshold)
    return {
        "experiment": f"{source_name} -> {target_name}",
        "model": model_name,
        "seed": seed,
        "alignment": "source_threshold_no_alignment",
        "source_threshold": source_threshold,
        "source_oof_f1": threshold_info["f1"],
        **metrics,
    }


def run_crast_direction(source_name, target_name, X_source, y_source, X_target, y_target, feature_cols, seed, gamma=1.0, filter_mode="q75", top_k=100, n_estimators=350, n_splits=5):
    selected_features, score_df = select_transferable_features(
        X_source, y_source, X_target, feature_cols, seed=seed,
        gamma=gamma, filter_mode=filter_mode, top_k=top_k, n_estimators=n_estimators,
    )
    factory = lambda s: ExtraTreesClassifier(n_estimators=n_estimators, random_state=s, n_jobs=-1)
    source_oof = source_oof_scores(factory, X_source[selected_features], y_source, seed, n_splits=n_splits)
    threshold_info = select_source_threshold(y_source, source_oof, objective="f1")
    source_threshold = threshold_info["threshold"]
    model = factory(seed)
    model.fit(X_source[selected_features], y_source)
    target_scores = get_model_score(model, X_target[selected_features])

    if source_name == "NPM" and target_name == "PyPI":
        threshold, pred_rate = rank_threshold_transfer(source_oof, source_threshold, target_scores)
        final_scores = target_scores
        alignment = "rank_threshold_transfer"
        method = "CRAST_ExtraTrees_RankThreshold"
    else:
        final_scores = mean_std_align(target_scores, source_oof)
        threshold = source_threshold
        pred_rate = float(np.mean(source_oof >= source_threshold))
        alignment = "mean_std_score_alignment"
        method = "CRAST_ExtraTrees_MeanStdAlignment"

    metrics = evaluate_from_scores(y_target, final_scores, threshold)
    row = {
        "experiment": f"{source_name} -> {target_name}",
        "seed": seed,
        "method": method,
        "model": "ExtraTrees",
        "n_features": len(selected_features),
        "gamma": gamma,
        "filter_mode": filter_mode,
        "top_k": top_k,
        "alignment": alignment,
        "source_threshold": source_threshold,
        "target_threshold": threshold,
        "source_pred_rate": pred_rate,
        "source_oof_f1": threshold_info["f1"],
        **metrics,
    }
    feature_rows = pd.DataFrame({"experiment": f"{source_name} -> {target_name}", "seed": seed, "selected_feature": selected_features})
    score_df.insert(0, "experiment", f"{source_name} -> {target_name}")
    score_df.insert(1, "seed", seed)
    return row, feature_rows, score_df


def run_rank_fusion_direction(source_name, target_name, X_source, y_source, X_target, y_target, feature_cols, seed, gamma=1.0, filter_mode="q75", top_k=100, n_estimators=350, n_splits=5, top_model_count=5, model_names=None):
    selected_features, _ = select_transferable_features(
        X_source, y_source, X_target, feature_cols, seed=seed,
        gamma=gamma, filter_mode=filter_mode, top_k=top_k, n_estimators=n_estimators,
    )
    models = filter_model_factories(model_factories(n_estimators=n_estimators), model_names)
    source_score_map, target_score_map, source_f1_map, rows = {}, {}, {}, []
    for model_name, factory in models.items():
        try:
            source_oof = source_oof_scores(factory, X_source[selected_features], y_source, seed, n_splits=n_splits)
            threshold_info = select_source_threshold(y_source, source_oof, objective="f1")
            model = factory(seed)
            model.fit(X_source[selected_features], y_source)
            target_scores = get_model_score(model, X_target[selected_features])
            source_score_map[model_name] = source_oof
            target_score_map[model_name] = target_scores
            source_f1_map[model_name] = threshold_info["f1"]
        except Exception:
            continue
    ranked = sorted(source_score_map.keys(), key=lambda m: source_f1_map[m], reverse=True)
    selected_models = ranked[:top_model_count]
    if not selected_models:
        raise RuntimeError("No models produced valid scores for rank fusion")
    source_fused = np.mean([rank01(source_score_map[m]) for m in selected_models], axis=0)
    target_fused = np.mean([rank01(target_score_map[m]) for m in selected_models], axis=0)
    threshold_info = select_source_threshold(y_source, source_fused, objective="f1")
    source_threshold = threshold_info["threshold"]
    if source_name == "NPM" and target_name == "PyPI":
        threshold, pred_rate = rank_threshold_transfer(source_fused, source_threshold, target_fused)
        final_scores = target_fused
        alignment = "rank_threshold_transfer"
    else:
        final_scores = mean_std_align(target_fused, source_fused)
        threshold = source_threshold
        pred_rate = float(np.mean(source_fused >= source_threshold))
        alignment = "mean_std_score_alignment"
    metrics = evaluate_from_scores(y_target, final_scores, threshold)
    return {
        "experiment": f"{source_name} -> {target_name}",
        "seed": seed,
        "method": f"Fusion_Top{top_model_count}_SourceSelected_RankMean",
        "model": "rank_fusion",
        "models_used": ",".join(selected_models),
        "n_features": len(selected_features),
        "gamma": gamma,
        "filter_mode": filter_mode,
        "top_k": top_k,
        "alignment": alignment,
        "source_threshold": source_threshold,
        "target_threshold": threshold,
        "source_pred_rate": pred_rate,
        "source_oof_f1": threshold_info["f1"],
        **metrics,
    }
