import pandas as pd
from _common import common_parser, parse_config, parse_model_names, ensure_out, load_data
from crast.models import model_factories, filter_model_factories
from crast.transfer import run_source_only_transfer
from crast.metrics import summarize_results


def main():
    parser = common_parser("CRAST direct source-only cross-registry baseline")
    args = parser.parse_args()
    cfg = parse_config(args)
    out = ensure_out(args.out)
    _, _, X_npm, y_npm, X_pypi, y_pypi, feature_cols, _ = load_data(args)
    models = filter_model_factories(model_factories(n_estimators=cfg.n_estimators), parse_model_names(args))
    rows = []
    directions = [("NPM", "PyPI", X_npm, y_npm, X_pypi, y_pypi), ("PyPI", "NPM", X_pypi, y_pypi, X_npm, y_npm)]
    for source_name, target_name, X_source, y_source, X_target, y_target in directions:
        for seed in cfg.seeds:
            for model_name, factory in models.items():
                try:
                    rows.append(run_source_only_transfer(source_name, target_name, X_source, y_source, X_target, y_target, model_name, factory, seed, n_splits=cfg.n_splits))
                except Exception as e:
                    rows.append({"experiment": f"{source_name} -> {target_name}", "model": model_name, "seed": seed, "error": str(e)})
    results = pd.DataFrame(rows)
    summary = summarize_results(results, ["experiment", "model", "alignment"])
    results.to_csv(out / "supplement_direct_cross_registry_by_seed.csv", index=False)
    summary.to_csv(out / "table_03_direct_cross_registry_baseline.csv", index=False)
    print(summary)


if __name__ == "__main__":
    main()
