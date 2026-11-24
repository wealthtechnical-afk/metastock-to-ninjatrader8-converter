"""Run the data-quality checks: duplicate dates, high < low, bad prices, long gaps,
and big one-day moves that often mean a split or bonus was not adjusted."""
import sys
from _path import SAMPLE
import wt_nt8_eod as wt

DATA = sys.argv[1] if len(sys.argv) > 1 else SAMPLE
df = wt.read_output(DATA)
report = wt.check_quality(df, max_gap_days=10, jump_pct=40)
if report.empty:
    print(f"No issues found in {df['symbol'].nunique()} symbols.")
else:
    print(report.to_string(index=False))
    report.to_csv("quality_report.csv", index=False)
    print("\nsaved quality_report.csv")
