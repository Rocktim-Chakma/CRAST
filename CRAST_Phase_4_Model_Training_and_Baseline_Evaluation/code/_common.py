from pathlib import Path
import argparse
import sys

HERE = Path(__file__).resolve()
ROOT = None
for parent in [HERE.parent, *HERE.parents]:
    if (parent / "Reusable_Code_Modules" / "src").exists():
        ROOT = parent / "Reusable_Code_Modules"
        break
    if (parent / "src").exists() and (parent / "src" / "crast").exists():
        ROOT = parent
        break
if ROOT is None:
    raise RuntimeError("Could not locate Reusable_Code_Modules/src or src/crast")
sys.path.insert(0, str(ROOT / "src"))

from crast.config import ExperimentConfig
from crast.io_utils import load_aligned_npm_pypi


def common_parser(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--npm", required=True, help="Path to final NPM feature matrix CSV")
    parser.add_argument("--pypi", required=True, help="Path to final PyPI feature matrix CSV")
    parser.add_argument("--out", default="results/tables", help="Output directory")
    parser.add_argument("--seeds", default="0,1,2,3,4,5,10,42,99,123", help="Comma-separated random seeds")
    parser.add_argument("--gamma", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--filter-mode", default="q75", choices=["q75", "q50", "none"])
    parser.add_argument("--n-estimators", type=int, default=350)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--models", default="all", help="Comma-separated model names or all")
    return parser


def parse_model_names(args):
    value = getattr(args, "models", "all")
    if value is None or value.strip().lower() == "all":
        return None
    return [x.strip() for x in value.split(",") if x.strip()]


def parse_config(args):
    seeds = tuple(int(x.strip()) for x in args.seeds.split(",") if x.strip())
    return ExperimentConfig(
        seeds=seeds,
        gamma=args.gamma,
        top_k=args.top_k,
        filter_mode=args.filter_mode,
        n_estimators=args.n_estimators,
        n_splits=args.n_splits,
    )


def load_data(args):
    return load_aligned_npm_pypi(args.npm, args.pypi)


def ensure_out(path):
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out
