import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
from _common import common_parser, parse_config, parse_model_names, ensure_out, load_data
from crast.models import model_factories, filter_model_factories


def main():
    parser = common_parser("CRAST same-registry model comparison")
    args = parser.parse_args()
    cfg = parse_config(args)
    out = ensure_out(args.out)
    _, _, X_npm, y_npm, X_pypi, y_pypi, feature_cols, _ = load_data(args)
    models = filter_model_factories(model_factories(n_estimators=cfg.n_estimators), parse_model_names(args))
    scoring = {
        "accuracy": "accuracy",
        "precision": make_scorer(precision_score, zero_division=0),
        "malicious_recall": make_scorer(recall_score, pos_label=1, zero_division=0),
        "f1": make_scorer(f1_score, zero_division=0),
        "auc": "roc_auc",
    }
    rows = []
    for registry, X, y in [("NPM", X_npm, y_npm), ("PyPI", X_pypi, y_pypi)]:
        for seed in cfg.seeds:
            cv = StratifiedKFold(n_splits=cfg.n_splits, shuffle=True, random_state=seed)
            for model_name, factory in models.items():
                model = factory(seed)
                scores = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=1, error_score="raise")
                rows.append({
                    "registry": registry,
                    "model": model_name,
                    "seed": seed,
                    "accuracy": scores["test_accuracy"].mean(),
                    "precision": scores["test_precision"].mean(),
                    "malicious_recall": scores["test_malicious_recall"].mean(),
                    "f1": scores["test_f1"].mean(),
                    "auc": scores["test_auc"].mean(),
                })
    results = pd.DataFrame(rows)
    summary = results.groupby(["registry", "model"]).agg(
        accuracy_mean=("accuracy", "mean"), accuracy_std=("accuracy", "std"),
        precision_mean=("precision", "mean"), malicious_recall_mean=("malicious_recall", "mean"),
        f1_mean=("f1", "mean"), f1_std=("f1", "std"), auc_mean=("auc", "mean"),
    ).reset_index().sort_values(["registry", "f1_mean"], ascending=[True, False])
    results.to_csv(out / "supplement_same_registry_results_by_seed.csv", index=False)
    summary.to_csv(out / "table_01_same_registry_model_comparison.csv", index=False)
    print(summary)


if __name__ == "__main__":
    main()
