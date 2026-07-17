import pandas as pd
from _common import common_parser, parse_config, ensure_out, load_data
from crast.feature_groups import build_feature_groups
from crast.transfer import run_crast_direction
from crast.metrics import summarize_results


def main():
    parser = common_parser("CRAST feature-group ablation")
    args = parser.parse_args()
    cfg = parse_config(args)
    out = ensure_out(args.out)
    _, _, X_npm, y_npm, X_pypi, y_pypi, feature_cols, _ = load_data(args)
    groups = build_feature_groups(feature_cols)
    rows = []
    directions = [("NPM", "PyPI", X_npm, y_npm, X_pypi, y_pypi), ("PyPI", "NPM", X_pypi, y_pypi, X_npm, y_npm)]
    for group_name, group_features in groups.items():
        configs = {
            f"{group_name}_only": group_features,
            f"without_{group_name}": [c for c in feature_cols if c not in group_features],
        }
        for config_name, selected_cols in configs.items():
            if len(selected_cols) < 2:
                continue
            for source_name, target_name, X_source, y_source, X_target, y_target in directions:
                for seed in cfg.seeds:
                    try:
                        row, _, _ = run_crast_direction(source_name, target_name, X_source, y_source, X_target, y_target, selected_cols, seed, gamma=cfg.gamma, filter_mode=cfg.filter_mode, top_k=min(cfg.top_k, len(selected_cols)), n_estimators=cfg.n_estimators, n_splits=cfg.n_splits)
                        row["feature_configuration"] = config_name
                        row["input_feature_count"] = len(selected_cols)
                        rows.append(row)
                    except Exception as e:
                        rows.append({"experiment": f"{source_name} -> {target_name}", "feature_configuration": config_name, "seed": seed, "error": str(e)})
    results = pd.DataFrame(rows)
    summary = summarize_results(results, ["experiment", "feature_configuration", "method", "alignment"])
    results.to_csv(out / "supplement_feature_group_ablation_by_seed.csv", index=False)
    summary.to_csv(out / "table_08_feature_group_ablation.csv", index=False)
    print(summary)


if __name__ == "__main__":
    main()
