# Using the files with AI tools

The converted files are small plain-text tables, so most AI assistants that accept file uploads (or code-running assistants) can read them.

**Tips**
* Upload a few symbols at a time, or first combine them with `python python/wt_nt8_eod.py export <folder> all_data.csv`.
* Tell the assistant the format: *"Each line is yyyyMMdd;open;high;low;close;volume. The file name is the symbol."*
* Ask it to show its working (formulas or code) so you can check the numbers.

**Example questions**
* "Which symbols closed at a 52-week high on the last date?"
* "Make a table of each symbol's calendar-year % change."
* "Find days where the close moved more than 20 % – could these be unadjusted splits?"
* "Plot the close with 50- and 200-day moving averages for ALPHA."
* "Write pandas code that loads all these files into one DataFrame."

⚠ AI answers can be wrong. Check results against the data yourself. For education and analysis only – not investment advice.
