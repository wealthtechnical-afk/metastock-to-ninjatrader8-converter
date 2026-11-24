# lets the examples import wt_nt8_eod from ../python without installing anything
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
SAMPLE = ROOT / "sample_data"
