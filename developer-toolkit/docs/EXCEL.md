# Using the files in Excel

## Quickest: one combined CSV
Run once (Python 3 with pandas):
```
python python/wt_nt8_eod.py export "C:\NT8 out" all_data.csv
```
Open `all_data.csv` in Excel – columns `symbol, date, open, high, low, close, volume`. Insert → PivotTable to summarise by symbol, month or year.

## Without Python: Power Query (Excel 2016 or later)
1. Data → Get Data → From File → **From Folder** → pick the converter's **NT-All** folder → **Combine & Transform**.
2. In the Power Query editor, if everything is in one column: Home → **Split Column → By Delimiter → Semicolon**.
3. Rename the columns to `Date, Open, High, Low, Close, Volume`. The file name column (`Source.Name`) is the symbol – remove `.Last.txt` with Transform → Replace Values.
4. Turn the `yyyyMMdd` text into a real date: Add Column → **Custom Column**, formula
   `Date.FromText(Text.Start([Date],4) & "-" & Text.Middle([Date],4,2) & "-" & Text.End([Date],2))`, then set its type to Date and remove the old Date column.
5. Close & Load. Refresh any time the converter writes new files.

For education and analysis only – not investment advice.
