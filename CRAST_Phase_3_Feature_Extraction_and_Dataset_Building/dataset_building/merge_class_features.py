#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def main():
    p = argparse.ArgumentParser(description="Merge benign and malicious feature CSVs for one registry")
    p.add_argument("--benign", required=True)
    p.add_argument("--malicious", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    benign = pd.read_csv(args.benign)
    malicious = pd.read_csv(args.malicious)
    if list(benign.columns) != list(malicious.columns):
        raise ValueError("Column mismatch between benign and malicious feature files")
    df = pd.concat([benign, malicious], ignore_index=True)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print("Rows:", len(df), "benign:", int((df.label == 0).sum()), "malicious:", int((df.label == 1).sum()))

if __name__ == "__main__":
    main()
