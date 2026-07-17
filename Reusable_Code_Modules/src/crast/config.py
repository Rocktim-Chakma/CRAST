from dataclasses import dataclass, field

LABEL_COL = "label"
REGISTRY_COL = "registry"
PACKAGE_COL = "package_name"

FORBIDDEN_COLS = {
    LABEL_COL,
    REGISTRY_COL,
    PACKAGE_COL,
    "runtime_family",
    "runtime_version",
    "source",
    "split",
    "is_malicious",
}

@dataclass(frozen=True)
class ExperimentConfig:
    seeds: tuple[int, ...] = (0, 1, 2, 3, 4, 5, 10, 42, 99, 123)
    n_splits: int = 5
    n_estimators: int = 350
    gamma: float = 1.0
    filter_mode: str = "q75"
    top_k: int = 100
    label_col: str = LABEL_COL
    registry_col: str = REGISTRY_COL
    package_col: str = PACKAGE_COL
    forbidden_cols: set[str] = field(default_factory=lambda: set(FORBIDDEN_COLS))
