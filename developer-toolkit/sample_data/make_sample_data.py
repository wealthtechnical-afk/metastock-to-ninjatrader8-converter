"""Creates the made-up sample data in this folder (NOT real market data), laid out
exactly like the WealthMetaStockToNT8 Converter's output root.
Run:  python make_sample_data.py"""
import shutil
import numpy as np, pandas as pd
from pathlib import Path
here = Path(__file__).parent
dates = pd.bdate_range("2022-01-03", "2024-12-31")
spec = {"DEMO A-M": {"ALPHA": 120, "BRAVO": 45, "CHARLIE": 860},
        "DEMO N-Z": {"NOVA": 310, "ORBIT": 22, "ZENITH": 1500},
        "DEMO INDEX": {"DEMOINDEX": 18000}}
rng = np.random.default_rng(42)
nt_all = here / "NT-All"; nt_all.mkdir(exist_ok=True)
all_syms, mapping = [], []
for folder, syms in spec.items():
    d = here / f"NT-{folder}"; d.mkdir(exist_ok=True)
    for sym, p0 in syms.items():
        r = rng.normal(0.0004, 0.016 if sym != "DEMOINDEX" else 0.009, len(dates))
        close = p0 * np.exp(np.cumsum(r))
        opn = np.r_[p0, close[:-1]] * (1 + rng.normal(0, 0.004, len(dates)))
        hi = np.maximum(opn, close) * (1 + np.abs(rng.normal(0, 0.006, len(dates))))
        lo = np.minimum(opn, close) * (1 - np.abs(rng.normal(0, 0.006, len(dates))))
        vol = rng.lognormal(12, 0.5, len(dates)).astype(int) if sym != "DEMOINDEX" else np.zeros(len(dates), int)
        f = d / f"{sym}.Last.txt"
        with open(f, "w", newline="\r\n") as fh:
            for i, dt in enumerate(dates):
                fh.write(f"{dt:%Y%m%d};{opn[i]:.2f};{hi[i]:.2f};{lo[i]:.2f};{close[i]:.2f};{vol[i]}\n")
        shutil.copy(f, nt_all / f.name)
        mapping.append(f"{sym}={sym}")
    (here / f"NT-{folder}-NT8-Symbol-Import-List.txt").write_text("\r\n".join(sorted(syms)) + "\r\n")
    all_syms += list(syms)
(here / "NT8-All Symbol-Import-List.txt").write_text("\r\n".join(sorted(all_syms)) + "\r\n")
(here / "Symbol-Mapping.txt").write_text("\r\n".join(sorted(mapping)) + "\r\n")
(here / "Duplicate-Symbols.txt").write_text("Duplicate mapped symbols report\r\n\r\nNo duplicate mapped symbols found.\r\n")
print("sample data written")
