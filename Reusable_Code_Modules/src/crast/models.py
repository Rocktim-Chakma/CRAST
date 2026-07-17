import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from .metrics import get_model_score


def _optional_xgboost_factory(n_estimators):
    try:
        from xgboost import XGBClassifier
    except Exception:
        return None
    return lambda seed: XGBClassifier(
        n_estimators=min(300, n_estimators), max_depth=6, learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9,
        random_state=seed, eval_metric="logloss", n_jobs=1,
    )


def _optional_lightgbm_factory(n_estimators):
    try:
        from lightgbm import LGBMClassifier
    except Exception:
        return None
    return lambda seed: LGBMClassifier(
        n_estimators=min(300, n_estimators), learning_rate=0.05,
        subsample=0.9, colsample_bytree=0.9,
        random_state=seed, verbose=-1, n_jobs=1,
    )


def _optional_catboost_factory(n_estimators):
    try:
        from catboost import CatBoostClassifier
    except Exception:
        return None
    return lambda seed: CatBoostClassifier(
        iterations=min(300, n_estimators), learning_rate=0.05, depth=6,
        random_seed=seed, verbose=0, allow_writing_files=False,
    )


def model_factories(n_estimators=350, include_histgb=True, include_optional=True):
    """Return model factories used in CRAST comparisons.

    Optional backends are imported lazily so the core pipeline works even when
    xgboost/lightgbm/catboost are not installed.
    """
    models = {
        "LogisticRegression": lambda seed: Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=5000, random_state=seed)),
        ]),
        "LinearSVM": lambda seed: Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LinearSVC(random_state=seed, max_iter=10000)),
        ]),
        "RandomForest": lambda seed: RandomForestClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=1),
        "ExtraTrees": lambda seed: ExtraTreesClassifier(n_estimators=n_estimators, random_state=seed, n_jobs=1),
    }
    if include_histgb:
        models["HistGradientBoosting"] = lambda seed: HistGradientBoostingClassifier(
            random_state=seed, max_iter=300, learning_rate=0.05
        )
    if include_optional:
        for name, factory in [
            ("XGBoost", _optional_xgboost_factory(n_estimators)),
            ("LightGBM", _optional_lightgbm_factory(n_estimators)),
            ("CatBoost", _optional_catboost_factory(n_estimators)),
        ]:
            if factory is not None:
                models[name] = factory
    return models


def filter_model_factories(factories, requested_names=None):
    """Return selected model factories by name. Missing optional models are skipped."""
    if requested_names is None:
        return factories
    selected = {}
    missing = []
    for name in requested_names:
        if name in factories:
            selected[name] = factories[name]
        else:
            missing.append(name)
    if not selected:
        available = ", ".join(sorted(factories))
        raise ValueError(f"None of the requested models are available. Available models: {available}")
    if missing:
        print("Warning: requested models not available and skipped:", ", ".join(missing))
    return selected


def source_oof_scores(model_factory, X, y, seed, n_splits=5):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    scores = np.zeros(len(y), dtype=float)
    for train_idx, val_idx in skf.split(X, y):
        model = model_factory(seed)
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        scores[val_idx] = get_model_score(model, X.iloc[val_idx])
    return scores
