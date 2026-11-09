import sys
from pathlib import Path

# The eval package (wrapper library, cases) lives at the repo root.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
