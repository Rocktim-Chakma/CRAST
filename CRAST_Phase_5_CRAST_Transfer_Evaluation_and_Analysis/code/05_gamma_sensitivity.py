import pandas as pd
from _common import common_parser, parse_config, parse_model_names, ensure_out, load_data
from crast.transfer import run_crast_direction, run_rank_fusion_direction
from crast.metrics import summarize_results


def main():
    parser = common_parser("CRAST gamma sensitivity")
    parser.add_argument("--gammas", default="0.0,0.5,1.0,1.5,2.0")
    args = parser.parse_args()
    cfg = parse_config(args)
    gammas = [float(x.strip()) for x in args.gammas.split(",") if x.strip()]
    out = ensure_out(args.out)
    model_names = parse_model_names(args)
    _, _, X_npm, y_npm, X_pypi, y_pypi, feature_cols, _ = load_data(args)
    rows = []
    for gamma in gammas:
        for seed in cfg.seeds:
            rows.append(run_rank_fusion_direction("NPM", "PyPI", X_npm, y_npm, X_pypi, y_pypi, feature_cols, seed, gamma=gamma, filter_mode=cfg.filter_mode, top_k=cfg.top_k, n_estimators=cfg.n_estimators, n_splits=cfg.n_splits, top_model_count=5, model_names=model_names))
            row, _, _ = run_crast_direction("PyPI", "NPM", X_pypi, y_pypi, X_npm, y_npm, feature_cols, seed, gamma=gamma, filter_mode=cfg.filter_mode, top_k=cfg.top_k, n_estimators=cfg.n_estimators, n_splits=cfg.n_splits)
            rows.append(row)
    results = pd.DataFrame(rows)
    summary = summarize_results(results, ["experiment", "gamma", "method", "alignment"])
    results.to_csv(out / "supplement_gamma_sensitivity_by_seed.csv", index=False)
    summary.to_csv(out / "table_07_gamma_sensitivity.csv", index=False)
    print(summary)


if __name__ == "__main__":
    main()
