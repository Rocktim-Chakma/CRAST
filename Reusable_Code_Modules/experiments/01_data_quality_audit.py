import pandas as pd
import numpy as np
from _common import common_parser, ensure_out, load_data
from crast.config import LABEL_COL
from crast.data_audit import duplicate_conflict_audit


def main():
    parser = common_parser("CRAST data quality and leakage-style audit")
    args = parser.parse_args()
    out = ensure_out(args.out)
    npm_df, pypi_df, X_npm, y_npm, X_pypi, y_pypi, feature_cols, constant_cols = load_data(args)

    audit_rows = []
    for name, df, X, y in [("NPM", npm_df, X_npm, y_npm), ("PyPI", pypi_df, X_pypi, y_pypi)]:
        audit_rows.append({
            "registry": name,
            "rows": len(df),
            "features": X.shape[1],
            "benign": int((y == 0).sum()),
            "malicious": int((y == 1).sum()),
            "missing_numeric_values": int(X.isna().sum().sum()),
            "infinite_numeric_values": int(np.isinf(X.to_numpy()).sum()),
            "duplicate_rows": int(X.duplicated().sum()),
        })
        dup, cross = duplicate_conflict_audit(df, feature_cols, name)
        dup.to_csv(out / f"{name.lower()}_duplicate_feature_audit.csv", index=False)
        cross.to_csv(out / f"{name.lower()}_cross_label_duplicate_audit.csv", index=False)

    pd.DataFrame(audit_rows).to_csv(out / "dataset_quality_audit.csv", index=False)
    pd.DataFrame({"removed_constant_feature": constant_cols}).to_csv(out / "removed_constant_features.csv", index=False)
    pd.DataFrame({"feature": feature_cols}).to_csv(out / "final_feature_schema.csv", index=False)
    print("Saved data-quality audit to", out)


if __name__ == "__main__":
    main()
