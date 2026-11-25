"""
wt_nt8_eod – free helper for NinjaTrader 8 end-of-day (EOD) text files.

Also reads and writes the WealthTechnical Data Tool format (Ticker,Date,Open,High,Low,Close,Volume).

Works with the plain-text files written by the free WealthMetaStockToNT8 Converter
(https://www.wealthtechnical.com/wealthmetastock-to-nt8-converter.html) and with any
other file in NinjaTrader 8's end-of-day format:

    yyyyMMdd;open;high;low;close;volume        e.g.  20240102;2580.0;2611.5;2571.2;2604.8;512340

One file per instrument; the file name is the symbol (the converter writes RELIANCE.Last.txt).
The converter's output root looks like:
    NT-<folder>/...          one tree per MetaStock folder converted
    NT-All/                  every symbol once  <- usually the folder to read
    NT8-All Symbol-Import-List.txt, <folder>-NT8-Symbol-Import-List.txt
    Symbol-Mapping.txt       original=mapped symbol
    Duplicate-Symbols.txt    report of symbols skipped as duplicates

Use it as a library:
    import wt_nt8_eod as wt
    df = wt.read_output("C:/NT8 out")           # reads NT-All: every symbol in one DataFrame
    wide = wt.to_wide(df, "close")              # one column per symbol
    report = wt.check_quality(df)               # data-quality report

or from the command line:
    python wt_nt8_eod.py info   "C:/NT8 data"
    python wt_nt8_eod.py check  "C:/NT8 data"
    python wt_nt8_eod.py export "C:/NT8 data" all_data.csv      (or .parquet, or .db for SQLite)
    python wt_nt8_eod.py export "C:/NT8 data" C:/out --format amibroker   (nt8, amibroker, metastock-csv, mt5, csv-per-symbol, wealthtool)

For education and analysis only – not investment advice. Provided "as is" under the MIT
licence (see LICENSE). This toolkit does not provide market data. Always compare
converted data with your original files.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Iterable

import pandas as pd

__version__ = "1.1.1"

COLUMNS = ["date", "open", "high", "low", "close", "volume"]
DEFAULT_EXTENSIONS = (".txt", ".csv")
_SUFFIXES = (".Last", ".Bid", ".Ask")  # NinjaTrader data-type suffixes in file names


def symbol_from_path(path: str | os.PathLike) -> str:
    """'RELIANCE.Last.txt' -> 'RELIANCE', 'NIFTY 50.txt' -> 'NIFTY 50'."""
    name = Path(path).stem
    for suf in _SUFFIXES:
        if name.endswith(suf):
            return name[: -len(suf)]
    return name


def _detect_sep(sample: str) -> str:
    for sep in (";", ",", "\t"):
        if sep in sample:
            return sep
    raise ValueError("no ';', ',' or tab separator found")


def read_file(path: str | os.PathLike, symbol: str | None = None) -> pd.DataFrame:
    """Read one NT8 EOD file into a DataFrame with columns
    symbol, date (datetime64), open, high, low, close, volume.

    Accepts ';' (NinjaTrader default), ',' or tab separators, an optional header line,
    and dates written as yyyyMMdd or 'yyyyMMdd HHmmss'.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines:
        return _empty()
    sep = _detect_sep(lines[0])
    if lines[0].lower().replace(" ", "").startswith("ticker" + sep + "date"):
        df = read_wealthtool(path, delimiter=sep)          # WealthTechnical Data Tool file
        if symbol:
            df["symbol"] = symbol
        return df
    has_header = not re.match(r"^\d{8}", lines[0])
    rows = lines[1:] if has_header else lines
    recs = [r.split(sep) for r in rows]
    bad = [i for i, r in enumerate(recs) if len(r) < 5]
    if bad:
        raise ValueError(f"{path.name}: {len(bad)} line(s) with fewer than 5 fields, first at data line {bad[0] + 1}")
    df = pd.DataFrame([r[:6] + [None] * (6 - len(r[:6])) for r in recs], columns=COLUMNS)
    df["date"] = pd.to_datetime(df["date"].str.strip().str[:8], format="%Y%m%d", errors="coerce")
    for c in COLUMNS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df.insert(0, "symbol", symbol or symbol_from_path(path))
    return df


def iter_files(folder: str | os.PathLike, recursive: bool = True,
               extensions: Iterable[str] = DEFAULT_EXTENSIONS) -> list[Path]:
    """List data files in a folder (and its subfolders), skipping the converter's
    report/list files (symbol import lists, duplicate-symbol and mapping reports)."""
    folder = Path(folder)
    exts = tuple(e.lower() for e in extensions)
    it = folder.rglob("*") if recursive else folder.glob("*")
    skip = re.compile(r"(import[-_ ]list|symbol[-_ ]mapping|duplicate[-_ ]symbol)", re.I)
    return sorted(p for p in it if p.is_file() and p.suffix.lower() in exts and not skip.search(p.name))


def read_folder(folder: str | os.PathLike, recursive: bool = True, add_folder: bool = True,
                on_error: str = "warn") -> pd.DataFrame:
    """Read every data file in a folder into one long DataFrame.

    on_error: 'warn' (skip bad files and print a message), 'raise' or 'ignore'.
    If add_folder is True a 'folder' column records the sub-folder each file came from.
    """
    folder = Path(folder)
    frames = []
    for p in iter_files(folder, recursive):
        try:
            df = read_file(p)
        except Exception as e:  # noqa: BLE001
            if on_error == "raise":
                raise
            if on_error == "warn":
                print(f"skipped {p}: {e}", file=sys.stderr)
            continue
        if add_folder:
            rel = p.parent.relative_to(folder)
            df["folder"] = "." if str(rel) == "." else str(rel)
        frames.append(df)
    if not frames:
        return _empty(add_folder)
    out = pd.concat(frames, ignore_index=True)
    return out.sort_values(["symbol", "date"], kind="stable").reset_index(drop=True)


def read_output(root: str | os.PathLike, **kw) -> pd.DataFrame:
    """Read a converter output root. Uses its NT-All folder (every symbol once) when present,
    otherwise reads the given folder and its subfolders. Extra keywords go to read_folder()."""
    root = Path(root)
    nt_all = root / "NT-All"
    return read_folder(nt_all if nt_all.is_dir() else root, **kw)


def read_symbol_mapping(path: str | os.PathLike) -> dict[str, str]:
    """Read Symbol-Mapping.txt (lines 'ORIGINAL=MAPPED') into {original: mapped}."""
    out = {}
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for ln in f:
            ln = ln.strip()
            if "=" in ln:
                k, v = ln.rsplit("=", 1)
                out[k.strip()] = v.strip()
    return out


def read_import_list(path: str | os.PathLike) -> list[str]:
    """Read an NT8 symbol import list (one symbol per line)."""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        return [ln.strip() for ln in f if ln.strip()]


def to_wide(df: pd.DataFrame, field: str = "close") -> pd.DataFrame:
    """Pivot a long DataFrame to one column per symbol (index = date)."""
    d = df.drop_duplicates(["symbol", "date"], keep="last")
    return d.pivot(index="date", columns="symbol", values=field).sort_index()


def check_quality(df: pd.DataFrame, max_gap_days: int = 10, jump_pct: float = 40.0) -> pd.DataFrame:
    """Return one row per problem found. Checks:
    unreadable dates/prices, duplicate dates, high < low, open/close outside high-low,
    zero or negative prices, negative volume, calendar gaps longer than max_gap_days,
    and day-to-day close moves bigger than jump_pct % (often an unadjusted split/bonus).
    An empty result means no issues were found by these checks.
    """
    issues = []

    def add(sym, date, kind, detail):
        issues.append({"symbol": sym, "date": date, "issue": kind, "detail": detail})

    for sym, g in df.groupby("symbol", sort=True):
        g = g.sort_values("date")
        for _, r in g[g["date"].isna()].iterrows():
            add(sym, None, "bad date", "date could not be read")
        num = g[["open", "high", "low", "close"]]
        for idx in g.index[num.isna().any(axis=1)]:
            add(sym, g.at[idx, "date"], "bad price", "missing or non-numeric price")
        g = g.dropna(subset=["date"])
        for d in g.loc[g["date"].duplicated(keep=False), "date"].unique():
            add(sym, d, "duplicate date", "same date appears more than once")
        v = g.dropna(subset=["open", "high", "low", "close"])
        for _, r in v[v["high"] < v["low"]].iterrows():
            add(sym, r["date"], "high < low", f"high {r['high']} < low {r['low']}")
        out = v[(v["open"] > v["high"]) | (v["open"] < v["low"]) | (v["close"] > v["high"]) | (v["close"] < v["low"])]
        for _, r in out.iterrows():
            add(sym, r["date"], "outside range", "open or close outside the high-low range")
        for _, r in v[(v[["open", "high", "low", "close"]] <= 0).any(axis=1)].iterrows():
            add(sym, r["date"], "non-positive price", "price is zero or negative")
        for _, r in g[g["volume"] < 0].iterrows():
            add(sym, r["date"], "negative volume", f"volume {r['volume']}")
        u = v.drop_duplicates("date")
        gaps = u["date"].diff().dt.days
        for i in u.index[gaps > max_gap_days]:
            add(sym, u.at[i, "date"], "gap", f"{int(gaps[i])} calendar days since previous bar")
        chg = u["close"].pct_change() * 100
        for i in u.index[chg.abs() > jump_pct]:
            add(sym, u.at[i, "date"], "big move", f"close changed {chg[i]:+.1f}% – check for split/bonus adjustment")
    return pd.DataFrame(issues, columns=["symbol", "date", "issue", "detail"])


def summary(df: pd.DataFrame) -> pd.DataFrame:
    """One row per symbol: first/last date, number of bars, last close."""
    g = df.dropna(subset=["date"]).sort_values("date").groupby("symbol")
    return pd.DataFrame({
        "first_date": g["date"].first(), "last_date": g["date"].last(),
        "bars": g.size(), "last_close": g["close"].last(),
    })


def export(df: pd.DataFrame, path: str | os.PathLike) -> Path:
    """Save to .csv or .parquet (parquet needs 'pyarrow')."""
    path = Path(path)
    if path.suffix.lower() == ".parquet":
        df.to_parquet(path, index=False)
    elif path.suffix.lower() == ".csv":
        df.to_csv(path, index=False, date_format="%Y-%m-%d")
    else:
        raise ValueError("use a .csv or .parquet file name")
    return path


def write_nt8(df: pd.DataFrame, folder: str | os.PathLike, suffix: str = ".Last") -> list[Path]:
    """Write a long DataFrame back to NinjaTrader 8 EOD files, one per symbol
    (yyyyMMdd;open;high;low;close;volume), named SYMBOL.Last.txt like the converter's output.
    Use suffix='' for SYMBOL.txt."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    written = []
    for sym, g in df.dropna(subset=["date"]).sort_values("date").groupby("symbol"):
        p = folder / f"{sym}{suffix}.txt"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            for r in g.itertuples(index=False):
                vol = 0 if pd.isna(r.volume) else int(r.volume)
                f.write(f"{r.date:%Y%m%d};{_n(r.open)};{_n(r.high)};{_n(r.low)};{_n(r.close)};{vol}\n")
        written.append(p)
    return written


# ----------------------------------------------------------------------------- more writers
def _iter_symbols(df):
    for sym, g in df.dropna(subset=["date"]).sort_values("date").groupby("symbol"):
        yield sym, g


def _f4(x) -> str:
    return f"{x:.4f}"


def _vol(v) -> int:
    return 0 if pd.isna(v) else int(v)


def write_amibroker(df: pd.DataFrame, folder: str | os.PathLike) -> list[Path]:
    """AmiBroker ASCII import files: SYMBOL.txt with Ticker,Date(yyyymmdd),Open,High,Low,Close,Volume."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True); out = []
    for sym, g in _iter_symbols(df):
        p = folder / f"{sym}.txt"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("Ticker,Date,Open,High,Low,Close,Volume\n")
            for r in g.itertuples(index=False):
                f.write(f"{sym},{r.date:%Y%m%d},{_f4(r.open)},{_f4(r.high)},{_f4(r.low)},{_f4(r.close)},{_vol(r.volume)}\n")
        out.append(p)
    return out


def write_metastock_csv(df: pd.DataFrame, folder: str | os.PathLike) -> list[Path]:
    """MetaStock ASCII files (<TICKER>,<PER>,<DTYYYYMMDD>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>), one per symbol –
    import them with MetaStock's downloader."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True); out = []
    for sym, g in _iter_symbols(df):
        p = folder / f"{sym}.csv"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("<TICKER>,<PER>,<DTYYYYMMDD>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>\n")
            for r in g.itertuples(index=False):
                f.write(f"{sym},D,{r.date:%Y%m%d},{_f4(r.open)},{_f4(r.high)},{_f4(r.low)},{_f4(r.close)},{_vol(r.volume)}\n")
        out.append(p)
    return out


def write_mt5(df: pd.DataFrame, folder: str | os.PathLike) -> list[Path]:
    """MetaTrader 5 bar files for custom symbols (Symbols → Bars → Import Bars): tab-separated
    <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>, dates as yyyy.MM.dd, one file per symbol."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True); out = []
    for sym, g in _iter_symbols(df):
        p = folder / f"{sym}.csv"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write("<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>\n")
            for r in g.itertuples(index=False):
                v = _vol(r.volume)
                f.write(f"{r.date:%Y.%m.%d}\t00:00:00\t{_f4(r.open)}\t{_f4(r.high)}\t{_f4(r.low)}\t{_f4(r.close)}\t{v}\t{v}\t0\n")
        out.append(p)
    return out


def write_csv_per_symbol(df: pd.DataFrame, folder: str | os.PathLike) -> list[Path]:
    """Plain CSV per symbol (Date,Open,High,Low,Close,Volume) – the layout most backtesting tools,
    spreadsheets and charting apps read directly."""
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True); out = []
    for sym, g in _iter_symbols(df):
        p = folder / f"{sym}.csv"
        g[["date", "open", "high", "low", "close", "volume"]].rename(columns=str.capitalize).to_csv(
            p, index=False, date_format="%Y-%m-%d", float_format="%.4f")
        out.append(p)
    return out


def to_sqlite(df: pd.DataFrame, path: str | os.PathLike, table: str = "bars") -> Path:
    """Save to a SQLite database file (one table, indexed on symbol+date) – query it with SQL from
    Python, Excel (ODBC), DB Browser for SQLite or any reporting tool. Replaces the table if it exists."""
    import sqlite3
    path = Path(path)
    d = df.dropna(subset=["date"]).copy()
    d["date"] = d["date"].dt.strftime("%Y-%m-%d")
    cols = [c for c in ["symbol", "date", "open", "high", "low", "close", "volume"] if c in d.columns]
    with sqlite3.connect(path) as con:
        d[cols].to_sql(table, con, if_exists="replace", index=False)
        con.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_symbol_date ON {table}(symbol, date)")
    return path


# ----------------------------------------------------------------------------- WealthTechnical Data Tool format
WEALTHTOOL_COLUMNS = ["Ticker", "Date", "Open", "High", "Low", "Close", "Volume"]


def write_wealthtool(df: pd.DataFrame, folder: str | os.PathLike, delimiter: str = ",",
                     date_format: str = "%Y%m%d", header: bool = True,
                     columns: list | None = None, extension: str = ".txt") -> list[Path]:
    """WealthTechnical Data Tool files – the same layout as the Downloader's "WealthTool" export:
    SYMBOL.txt with Ticker,Date(yyyymmdd),Open,High,Low,Close,Volume (prices to 4 decimals).
    delimiter, date_format, header, columns and extension follow the Downloader's WealthTool settings."""
    cols = columns or WEALTHTOOL_COLUMNS
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True); out = []
    for sym, g in df.dropna(subset=["date"]).sort_values("date").groupby("symbol"):
        p = folder / f"{sym}{extension}"
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            if header:
                f.write(delimiter.join(cols) + "\n")
            for r in g.itertuples(index=False):
                vals = {"Ticker": str(sym), "Date": r.date.strftime(date_format), "Open": f"{r.open:.4f}",
                        "High": f"{r.high:.4f}", "Low": f"{r.low:.4f}", "Close": f"{r.close:.4f}",
                        "Volume": str(0 if pd.isna(r.volume) else int(r.volume))}
                f.write(delimiter.join(vals[c] for c in cols if c in vals) + "\n")
        out.append(p)
    return out


def read_wealthtool(path: str | os.PathLike, delimiter: str = ",", date_format: str = "%Y%m%d") -> pd.DataFrame:
    """Read one WealthTechnical Data Tool file (with a header line, as the Downloader writes by default)."""
    d = pd.read_csv(path, sep=delimiter, dtype={"Date": str})
    d.columns = [c.strip().lower() for c in d.columns]
    d["date"] = pd.to_datetime(d["date"].astype(str).str.strip(), format=date_format, errors="coerce")
    sym = d.pop("ticker") if "ticker" in d.columns else Path(path).stem
    d.insert(0, "symbol", sym if isinstance(sym, str) else sym.astype(str))
    for c in ["open", "high", "low", "close", "volume"]:
        if c not in d.columns:
            d[c] = pd.NA
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d[["symbol", "date", "open", "high", "low", "close", "volume"]]


WRITERS = {"nt8": lambda df, folder: write_nt8(df, folder), "amibroker": write_amibroker, "metastock-csv": write_metastock_csv,
           "mt5": write_mt5, "csv-per-symbol": write_csv_per_symbol, "wealthtool": write_wealthtool}


def _n(x) -> str:
    return f"{x:.6f}".rstrip("0").rstrip(".")


def _empty(add_folder: bool = False) -> pd.DataFrame:
    cols = ["symbol"] + COLUMNS + (["folder"] if add_folder else [])
    return pd.DataFrame(columns=cols)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wt_nt8_eod", description="Read, check and export NinjaTrader 8 EOD text files.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, hlp in (("info", "list symbols with first/last date and bar count"),
                      ("check", "run data-quality checks"),
                      ("export", "combine all files into one CSV or Parquet file")):
        s = sub.add_parser(name, help=hlp)
        s.add_argument("folder", help="converter output root (its NT-All folder is used) or any folder of NT8 files")
        if name == "export":
            s.add_argument("output", help="all_data.csv / .parquet / .db (SQLite), or a folder when --format is given")
            s.add_argument("--format", choices=sorted(WRITERS), help="write one file per symbol for this platform")
        if name == "check":
            s.add_argument("--max-gap-days", type=int, default=10)
            s.add_argument("--jump-pct", type=float, default=40.0)
            s.add_argument("--save", help="save the report to this CSV file")
    a = ap.parse_args(argv)
    df = read_output(a.folder)
    if df.empty:
        print("No data files found.")
        return 1
    if a.cmd == "info":
        with pd.option_context("display.max_rows", 500, "display.width", 120):
            print(summary(df))
        print(f"\n{df['symbol'].nunique()} symbols, {len(df)} bars")
    elif a.cmd == "check":
        rep = check_quality(df, a.max_gap_days, a.jump_pct)
        if rep.empty:
            print(f"No issues found in {df['symbol'].nunique()} symbols ({len(df)} bars).")
        else:
            with pd.option_context("display.max_rows", 200, "display.width", 200, "display.max_columns", 10, "display.max_colwidth", 80):
                print(rep)
            print(f"\n{len(rep)} issue(s) in {rep['symbol'].nunique()} symbol(s).")
        if a.save:
            rep.to_csv(a.save, index=False)
    elif a.cmd == "export":
        if a.format:
            files = WRITERS[a.format](df, a.output)
            print(f"Wrote {len(files)} {a.format} files to {a.output}")
        elif str(a.output).lower().endswith((".db", ".sqlite")):
            print(f"Saved {len(df)} rows for {df['symbol'].nunique()} symbols to {to_sqlite(df, a.output)}")
        else:
            p = export(df, a.output)
            print(f"Saved {len(df)} rows for {df['symbol'].nunique()} symbols to {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
