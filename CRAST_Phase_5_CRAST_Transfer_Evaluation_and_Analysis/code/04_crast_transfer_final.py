import pandas as pd
from _common import common_parser, parse_config, parse_model_names, ensure_out, load_data
from crast.transfer import run_crast_direction, run_rank_fusion_direction
from crast.metrics import summarize_results


def main():
    parser = common_parser("Final CRAST zero-shot cross-registry transfer")
    args = parser.parse_args()
    cfg = parse_config(args)
    out = ensure_out(args.out)
    model_names = parse_model_names(args)
    _, _, X_npm, y_npm, X_pypi, y_pypi, feature_cols, _ = load_data(args)
    rows, feature_frames, score_frames = [], [], []
    for seed in cfg.seeds:
        # Paper-aligned final NPM -> PyPI: source-selected top-5 rank fusion.
        rows.append(run_rank_fusion_direction(
            "NPM", "PyPI", X_npm, y_npm, X_pypi, y_pypi, feature_cols, seed,
            gamma=cfg.gamma, filter_mode=cfg.filter_mode, top_k=cfg.top_k,
            n_estimators=cfg.n_estimators, n_splits=cfg.n_splits, top_model_count=5, model_names=model_names,
        ))
        # Paper-aligned final PyPI -> NPM: Extra Trees + mean/std alignment.
        row, feat_df, score_df = run_crast_direction(
            "PyPI", "NPM", X_pypi, y_pypi, X_npm, y_npm, feature_cols, seed,
            gamma=cfg.gamma, filter_mode=cfg.filter_mode, top_k=cfg.top_k,
            n_estimators=cfg.n_estimators, n_splits=cfg.n_splits,
        )
        rows.append(row)
        feature_frames.append(feat_df)
        score_frames.append(score_df)
    results = pd.DataFrame(rows)
    summary = summarize_results(results, ["experiment", "method", "alignment"])
    results.to_csv(out / "supplement_crast_final_transfer_by_seed.csv", index=False)
    summary.to_csv(out / "table_04_crast_final_transfer_summary.csv", index=False)
    if feature_frames:
        pd.concat(feature_frames, ignore_index=True).to_csv(out / "supplement_selected_features_by_seed.csv", index=False)
    if score_frames:
        pd.concat(score_frames, ignore_index=True).to_csv(out / "supplement_feature_scores_by_seed.csv", index=False)
    print(summary)


if __name__ == "__main__":
    main()
