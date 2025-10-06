# Ensure the project root and `src/` are on sys.path for imports like `from src.budgetbuddy...`
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

# Insert at the front so it takes precedence over site-packages
for p in (PROJECT_ROOT, SRC_DIR):
    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
