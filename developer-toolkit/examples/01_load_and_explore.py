"""Load a whole folder of NinjaTrader 8 EOD files into pandas and look around.
Point DATA at your own converted folder, or keep the made-up sample data."""
import sys
from _path import SAMPLE
import pandas as pd
import wt_nt8_eod as wt

pd.set_option("display.width", 160)

DATA = sys.argv[1] if len(sys.argv) > 1 else SAMPLE

df = wt.read_output(DATA)
print(wt.summary(df))
print()
closes = wt.to_wide(df, "close")
print("Last 5 closes:")
print(closes.tail().round(2))
print()
ye = closes.resample("YE").last()
start = closes.iloc[[0]]
yearly = (pd.concat([start, ye]).pct_change().iloc[1:] * 100)
yearly.index = yearly.index.year
print("Calendar-year % change:")
print(yearly.round(1))
