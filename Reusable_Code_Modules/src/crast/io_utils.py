from pathlib import Path
import numpy as np
import pandas as pd
from .config import LABEL_COL, REGISTRY_COL, FORBIDDEN_COLS


def read_dataset(path: str | Path, registry_name: str) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path)
    if LABEL_COL not in df.columns:
        raise ValueError(f"Missing required column: {LABEL_COL} in {path}")
    if REGISTRY_COL not in df.columns:
        df[REGISTRY_COL] = registry_name
    else:
        df[REGISTRY_COL] = df[REGISTRY_COL].fillna(registry_name)
    df[LABEL_COL] = df[LABEL_COL].astype(int)
    df = df.replace([np.inf, -np.inf], np.nan)
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(0)
    return df


def get_numeric_feature_cols(df: pd.DataFrame, forbidden_cols=FORBIDDEN_COLS) -> list[str]:
    return [c for c in df.columns if c not in forbidden_cols and pd.api.types.is_numeric_dtype(df[c])]


def align_feature_schema(npm_df: pd.DataFrame, pypi_df: pd.DataFrame) -> list[str]:
    npm_features = set(get_numeric_feature_cols(npm_df))
    pypi_features = set(get_numeric_feature_cols(pypi_df))
    return sorted(npm_features & pypi_features)


def drop_constant_features(npm_df: pd.DataFrame, pypi_df: pd.DataFrame, feature_cols: list[str]) -> tuple[list[str], list[str]]:
    constant = []
    for c in feature_cols:
        if npm_df[c].nunique(dropna=False) <= 1 or pypi_df[c].nunique(dropna=False) <= 1:
            constant.append(c)
    kept = [c for c in feature_cols if c not in constant]
    return kept, constant


def load_aligned_npm_pypi(npm_path: str | Path, pypi_path: str | Path):
    npm_df = read_dataset(npm_path, "NPM")
    pypi_df = read_dataset(pypi_path, "PyPI")
    feature_cols_raw = align_feature_schema(npm_df, pypi_df)
    feature_cols, constant_cols = drop_constant_features(npm_df, pypi_df, feature_cols_raw)
    X_npm = npm_df[feature_cols].copy()
    y_npm = npm_df[LABEL_COL].astype(int).copy()
    X_pypi = pypi_df[feature_cols].copy()
    y_pypi = pypi_df[LABEL_COL].astype(int).copy()
    return npm_df, pypi_df, X_npm, y_npm, X_pypi, y_pypi, feature_cols, constant_cols
