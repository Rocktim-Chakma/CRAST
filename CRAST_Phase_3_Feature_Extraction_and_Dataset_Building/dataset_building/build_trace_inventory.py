#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd


def main():
    p = argparse.ArgumentParser(description="Build inventory of per-sample trace files")
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--trace-glob", default="trace.*")
    p.add_argument("--registry", default="")
    p.add_argument("--label", type=int, default=-1)
    args = p.parse_args()
    root = Path(args.input)
    rows = []
    for d in sorted([p for p in root.iterdir() if p.is_dir()]):
        rows.append({
            "sample_id": d.name,
            "registry": args.registry,
            "label": args.label,
            "trace_file_count": len(list(d.glob(args.trace_glob))),
            "has_stdout": (d / "run.stdout.log").exists(),
            "has_stderr": (d / "run.stderr.log").exists(),
        })
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print("Wrote inventory:", out)

if __name__ == "__main__":
    main()
