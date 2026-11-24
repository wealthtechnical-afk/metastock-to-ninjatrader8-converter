"""A simple screener: 52-week high/low, distance from the 200-day average, 1-month change.
For education and analysis only – not investment advice."""
import sys
import pandas as pd
from _path import SAMPLE
import wt_nt8_eod as wt

DATA = sys.argv[1] if len(sys.argv) > 1 else SAMPLE
df = wt.read_output(DATA)
close, high, low = (wt.to_wide(df, f) for f in ("close", "high", "low"))

last = close.iloc[-1]
hi52 = high.tail(252).max()
lo52 = low.tail(252).min()
sma200 = close.rolling(200).mean().iloc[-1]
table = pd.DataFrame({
    "last_close": last,
    "52w_high": hi52,
    "52w_low": lo52,
    "pct_below_52w_high": (1 - last / hi52) * 100,
    "pct_vs_sma200": (last / sma200 - 1) * 100,
    "1m_change_pct": (last / close.iloc[-22] - 1) * 100,
}).round(2)
table["at_52w_high"] = table["pct_below_52w_high"] <= 1
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)
print(table.sort_values("pct_vs_sma200", ascending=False))
