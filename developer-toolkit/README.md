# Developer toolkit – NinjaTrader 8 EOD data in Python, Excel & AI tools (free)

Free, open-source (MIT) helpers for the plain-text files written by the free **[WealthMetaStockToNT8 Converter](https://www.wealthtechnical.com/wealthmetastock-to-nt8-converter.html)** (`NT-All/SYMBOL.Last.txt`, symbol import lists, `Symbol-Mapping.txt`) – and for any NinjaTrader 8 end-of-day file (`yyyyMMdd;open;high;low;close;volume`).

▶ [Watch the 1-minute video](https://www.youtube.com/shorts/nlhzCcbAfJw) · ⬇ [Download the converter (free)](https://www.wealthtechnical.com/wealthmetastock-to-nt8-converter.html) · 📘 [Import guide](https://www.wealthtechnical.com/guides/import-metastock-data-into-ninjatrader-8/)

> The converter itself is free to use but its source code is not published. This folder contains only the open toolkit around its output.

## What's inside

| Path | What it does |
|---|---|
| `python/wt_nt8_eod.py` | one-file library + command line: read the converter output into pandas, read its symbol lists and mapping, data-quality checks, export to CSV / Parquet / SQLite, and one file per symbol for **NinjaTrader 8, AmiBroker, MetaStock ASCII, MetaTrader 5, WealthTechnical Data Tool** or plain CSV – and reads WealthTechnical Data Tool files too |
| `examples/quick_start.ipynb` | Jupyter notebook: load, check, chart, moving averages, export |
| `examples/01…05_*.py` | explore · 52-week-high screener · export · quality check · weekly bars back to NT8 |
| `docs/FILE_FORMAT.md` | exactly what the converter writes |
| `docs/EXCEL.md` | open the files in Excel (CSV or Power Query, no Python needed) |
| `docs/BACKTESTING.md` | use the data in Python backtesting tools (backtrader example) |
| `docs/AI_TOOLS.md` | using the files with AI assistants, with example questions |
| `sample_data/` | a **made-up** converter output (7 fictional symbols, same folders and lists as the real thing – not real market data) so everything runs out of the box |

## Install

```bash
pip install "https://github.com/wealthtechnical-afk/metastock-to-ninjatrader8-converter/archive/refs/heads/main.zip#subdirectory=developer-toolkit"
```
This adds the `wt-nt8-eod` command and the `wt_nt8_eod` Python module. (Or just download the folder and use the files directly, as below.)

## Quick start

```bash
pip install pandas            # optional: pyarrow matplotlib jupyter
cd developer-toolkit
python python/wt_nt8_eod.py info   sample_data          # symbols, first/last date, bars
python python/wt_nt8_eod.py check  sample_data          # data-quality report
python python/wt_nt8_eod.py export sample_data all.csv  # one combined file (.parquet, .db = SQLite)
python python/wt_nt8_eod.py export sample_data out_ab --format amibroker   # nt8, amibroker, metastock-csv, mt5, csv-per-symbol, wealthtool
```

Use your own data by pointing at the converter's output folder (its `NT-All` folder is used), e.g. `python python/wt_nt8_eod.py check "C:\NT8 out"`.

In Python:

```python
import sys; sys.path.insert(0, "python")
import wt_nt8_eod as wt

df    = wt.read_output(r"C:\NT8 out")            # NT-All -> symbol, date, open, high, low, close, volume
close = wt.to_wide(df, "close")                  # one column per symbol
issues = wt.check_quality(df)                    # duplicates, high<low, gaps, unadjusted splits…
wt.export(df, "all_data.parquet")
mapping = wt.read_symbol_mapping(r"C:\NT8 out\Symbol-Mapping.txt")   # {original: mapped}
```

## Quality checks

`check_quality()` flags: unreadable dates or prices · duplicate dates · high < low · open/close outside the high-low range · zero or negative prices · negative volume · gaps longer than 10 calendar days · one-day close moves over 40 % (often an unadjusted split or bonus). Both limits can be changed.

## Contributing

Issues and pull requests for the toolkit are welcome – new examples, readers for other tools, bug fixes.

---

## ⚠ Important
**This free toolkit is for education and analysis only** – not investment advice or a recommendation to buy or sell any security. Provided "as is"; always compare data with your original files. It provides no market data, places no orders and connects to no broker. Trading futures & options, crypto and other speculative instruments involves a high risk of loss and suits only those who understand and can bear that risk. MetaStock® and NinjaTrader® are registered trademarks of their respective owners; WealthTechnical LLP is not affiliated with or endorsed by MetaStock. WealthTechnical LLP is an Ecosystem Vendor of NinjaTrader Group LLC; NinjaTrader does not endorse WealthTechnical products. See [DISCLAIMER.md](DISCLAIMER.md) and the [full disclaimer](https://www.wealthtechnical.com/disclaimer.html).
