import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run the paper-aligned CRAST reproduction scripts")
    parser.add_argument("--npm", default="data/processed/npm_final_feature_matrix.csv")
    parser.add_argument("--pypi", default="data/processed/pypi_final_feature_matrix.csv")
    parser.add_argument("--out", default="reproduced_results")
    args, extra = parser.parse_known_args()

    root = Path(__file__).resolve().parent
    scripts = [
        root / "Reusable_Code_Modules" / "experiments" / "01_data_quality_audit.py",
        root / "Reusable_Code_Modules" / "experiments" / "02_same_registry_validation.py",
        root / "Reusable_Code_Modules" / "experiments" / "03_direct_transfer_baseline.py",
        root / "Reusable_Code_Modules" / "experiments" / "04_crast_transfer_final.py",
        root / "Reusable_Code_Modules" / "experiments" / "05_gamma_sensitivity.py",
        root / "Reusable_Code_Modules" / "experiments" / "06_feature_group_ablation.py",
    ]
    for script in scripts:
        cmd = [sys.executable, str(script), "--npm", args.npm, "--pypi", args.pypi, "--out", args.out, *extra]
        print("\nRunning:", " ".join(cmd))
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
