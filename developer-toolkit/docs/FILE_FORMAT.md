# File format – what the converter writes

The free **WealthMetaStockToNT8 Converter** reads MetaStock® binary folders or MetaStock-compatible ASCII TXT/CSV folders and writes plain-text files that NinjaTrader 8 can import. Because they are plain text, the same files can be read by Excel, Python, R, databases and AI tools.

## Output root – layout

```
<output root>/
├─ NT-<folder>/                         one tree per MetaStock® folder converted (sub-folders keep their structure, each prefixed NT-)
│   └─ SYMBOL.Last.txt                  price file, one per instrument
├─ NT-All/                              every symbol once (duplicates skipped) – usually the folder to use
│   └─ SYMBOL.Last.txt
├─ NT-<folder>-NT8-Symbol-Import-List.txt   symbols of that folder, one per line
├─ NT8-All Symbol-Import-List.txt           every symbol, one per line
├─ Symbol-Mapping.txt                       ORIGINAL=MAPPED, one per line
└─ Duplicate-Symbols.txt                    readable report of symbols skipped as duplicates
```

`sample_data/` in this toolkit has exactly this layout (with made-up data).

## Price files – `SYMBOL.Last.txt`

NinjaTrader 8 end-of-day text format – one bar per line, no header, `;` separated, UTF-8:

```
yyyyMMdd;open;high;low;close;volume
20240102;2580;2611.5;2571.2;2604.8;512340
20240103;2604.8;2630;2598.1;2622.4;468210
```

| Field | Meaning |
|---|---|
| `yyyyMMdd` | trading date (e.g. `20240102`) |
| `open`, `high`, `low`, `close` | prices, `.` as the decimal point, no thousands separator |
| `volume` | traded volume (often `0` for indices) |

* **File name = symbol** plus NinjaTrader's data-type suffix `.Last` (the toolkit removes `.Last`, `.Bid`, `.Ask` to get the symbol).
* **Importing into NinjaTrader 8:** first Control Center → Tools → Import → **Stock Symbol List** with an import-list file; then Tools → Import → **Historical Data** → *NinjaTrader (end of day)*, Data Type **Last**, your time zone, *Generate day bars* on.

## Lists and reports

| File | Format | Toolkit function |
|---|---|---|
| `NT8-All Symbol-Import-List.txt`, `NT-<folder>-NT8-Symbol-Import-List.txt` | one symbol per line | `read_import_list()` |
| `Symbol-Mapping.txt` | `ORIGINAL=MAPPED` per line – how each MetaStock® symbol was turned into a safe NT8 symbol | `read_symbol_mapping()` |
| `Duplicate-Symbols.txt` | text report: mapped symbol, original symbol, what it conflicts with, source folders, reason | read it as text |

`read_output(root)` reads the `NT-All` folder; `read_folder()` reads any folder and skips list/report files automatically.

## Tips

* Compare a few converted symbols with your original charts before relying on the data.
* A one-day move of 40 % or more is often a split or bonus that was not adjusted in the source data – `check_quality()` flags these.
* `write_nt8()` writes this same format, so you can build weekly bars, synthetic series or cleaned data in Python and import it back into NinjaTrader 8.
