"""Combine every file into one CSV (Excel-friendly) and, if pyarrow is installed, one Parquet file.
Also writes a 'wide' CSV with one close column per symbol."""
import sys
from pathlib import Path
from _path import SAMPLE
import wt_nt8_eod as wt

DATA = sys.argv[1] if len(sys.argv) > 1 else SAMPLE
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "output"); OUT.mkdir(exist_ok=True)

df = wt.read_output(DATA)
print("saved", wt.export(df, OUT / "all_data.csv"))
wt.to_wide(df, "close").to_csv(OUT / "closes_wide.csv", date_format="%Y-%m-%d")
print("saved", OUT / "closes_wide.csv")
try:
    print("saved", wt.export(df, OUT / "all_data.parquet"))
except ImportError:
    print("(pip install pyarrow to also save Parquet)")
