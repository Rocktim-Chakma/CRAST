#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def main():
    p = argparse.ArgumentParser(description="Merge NPM and PyPI feature matrices")
    p.add_argument("--npm", required=True)
    p.add_argument("--pypi", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    npm = pd.read_csv(args.npm)
    pypi = pd.read_csv(args.pypi)
    common = sorted(set(npm.columns) & set(pypi.columns))
    df = pd.concat([npm[common], pypi[common]], ignore_index=True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print("Rows:", len(df), "Columns:", len(df.columns))

if __name__ == "__main__":
    main()
