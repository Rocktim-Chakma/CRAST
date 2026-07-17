import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Run paper-aligned CRAST experiments in sequence")
    parser.add_argument("--npm", required=True)
    parser.add_argument("--pypi", required=True)
    parser.add_argument("--out", default="results/tables")
    args, extra = parser.parse_known_args()
    scripts = [
        "01_data_quality_audit.py",
        "02_same_registry_validation.py",
        "03_direct_transfer_baseline.py",
        "04_crast_transfer_final.py",
        "05_gamma_sensitivity.py",
        "06_feature_group_ablation.py",
    ]
    base = Path(__file__).resolve().parent
    for script in scripts:
        cmd = [sys.executable, str(base / script), "--npm", args.npm, "--pypi", args.pypi, "--out", args.out, *extra]
        print("\nRunning:", " ".join(cmd))
        subprocess.check_call(cmd)


if __name__ == "__main__":
    main()
