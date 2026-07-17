#!/usr/bin/env python3
import argparse
import pandas as pd


def main():
    p = argparse.ArgumentParser(description="Validate required CRAST feature-matrix columns")
    p.add_argument("--input", required=True)
    p.add_argument("--required", default="sample_id,label,total_syscalls,unique_syscalls,trace_file_count")
    args = p.parse_args()
    df = pd.read_csv(args.input)
    required = [x.strip() for x in args.required.split(",") if x.strip()]
    missing = [c for c in required if c not in df.columns]
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Missing required columns:", missing)
    if "label" in df.columns:
        print("Label counts:")
        print(df["label"].value_counts().sort_index())
    if missing:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
