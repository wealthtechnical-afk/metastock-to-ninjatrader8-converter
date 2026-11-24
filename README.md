# WealthMetaStockToNT8 Converter – free MetaStock® data to NinjaTrader 8

**▶ [Get NinjaTrader 8 FREE](https://ninjatraderdomesticvendor.sjv.io/wealthtechnical)** – free for charting and analysis.

Free **NinjaTrader® 8 indicator** that converts **MetaStock®-compatible end-of-day data** – folders and subfolders – into NinjaTrader 8 historical data format. Use NT8 alongside MetaStock: no switching, the power of both.

**[⬇ Download & guide](https://www.wealthtechnical.com/wealthmetastock-to-nt8-converter.html)** · [Get NinjaTrader 8 free](https://ninjatraderdomesticvendor.sjv.io/wealthtechnical) · [How to download NT8 (video)](https://www.youtube.com/watch?v=mFkVCLbghkY) · [Watch the converter (video)](https://www.youtube.com/watch?v=xxFZp-X9r-g) · [The Power of 2 (video)](https://www.youtube.com/watch?v=s01S0OjIKeo) · [NT8, Excel, Python & AI in 1 minute (Short)](https://www.youtube.com/shorts/nlhzCcbAfJw)

## What it creates
- NT8-format data, folder-wise and one combined file
- NT8 symbol import lists (per folder and master list)
- Duplicate symbol report and symbol mapping file

## How it works
0. [Download NinjaTrader 8 free](https://ninjatraderdomesticvendor.sjv.io/wealthtechnical) and install it ([video guide](https://www.youtube.com/watch?v=mFkVCLbghkY))
1. NT8 → Control Center → Tools → Import → NinjaScript Add-On → select the converter .zip
2. Open any chart and apply **WealthMetaStockToNT8 Converter**
3. Select the MetaStock input folder and NT8 output folder
4. Import symbols (Tools → Import → Stock Symbol List) and data (Tools → Import → Historical Data → NinjaTrader End-of-Day)

Works with MetaStock-compatible data from any data vendor or market – and from our free [NSE/BSE EOD Downloader](https://www.wealthtechnical.com/eod-downloader/). Converted data can also be used in Python, Excel, AI tools or a platform of your choice.

## For developers – free toolkit (open source, MIT)

The converter writes plain-text files (`NT-All/SYMBOL.Last.txt`, `yyyyMMdd;open;high;low;close;volume`) plus symbol import lists and a symbol-mapping file. The free **[developer-toolkit](developer-toolkit/)** helps you build on them:

- **Python library + command line** – read the whole output into pandas in one line, read the symbol lists and mapping, export to CSV/Parquet, write NT8 files back
- **Data-quality checks** – duplicate dates, high < low, bad prices, long gaps, unadjusted splits/bonuses
- **Examples** – Jupyter notebook, 52-week-high screener, export, quality report, weekly bars back to NT8
- **Guides** – [file format](developer-toolkit/docs/FILE_FORMAT.md) · [Excel](developer-toolkit/docs/EXCEL.md) · [AI tools](developer-toolkit/docs/AI_TOOLS.md)
- **Made-up sample data** in the converter's exact layout, so everything runs out of the box

```bash
cd developer-toolkit
python python/wt_nt8_eod.py check  sample_data          # or your converter output folder
python python/wt_nt8_eod.py export sample_data all.csv
```

The toolkit is open source; the converter itself is free to use but its source code is not published. Issues and pull requests for the toolkit are welcome.

## Important
**This free tool is for education and analysis only.** It is provided as is and is not investment advice or a recommendation to buy or sell any security – compare converted data with your original files. It converts only data you own and provides no market data. Trading futures & options, crypto and other speculative instruments involves a high risk of loss and suits only those who understand and can bear that risk. WealthTechnical LLP is an Ecosystem Vendor of NinjaTrader Group LLC. The NinjaTrader link on this page is our referral link. MetaStock® and NinjaTrader® are trademarks of their respective owners.

© WealthTechnical LLP · [wealthtechnical.com](https://www.wealthtechnical.com)
