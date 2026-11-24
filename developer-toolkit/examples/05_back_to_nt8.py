"""Round trip: read, change in pandas (here: build weekly bars), write NinjaTrader 8 files again.
Each weekly bar is dated on the last trading day of that week."""
import sys
from _path import SAMPLE
import wt_nt8_eod as wt

DATA = sys.argv[1] if len(sys.argv) > 1 else SAMPLE
df = wt.read_output(DATA).dropna(subset=["date"])
df["week"] = df["date"].dt.to_period("W-FRI")
weekly = (df.sort_values("date").groupby(["symbol", "week"])
            .agg(date=("date", "last"), open=("open", "first"), high=("high", "max"),
                 low=("low", "min"), close=("close", "last"), volume=("volume", "sum"))
            .reset_index().drop(columns="week"))
files = wt.write_nt8(weekly, "output/weekly_nt8")
print(f"wrote {len(files)} weekly files to output/weekly_nt8 – import them in NT8 like any EOD file")
