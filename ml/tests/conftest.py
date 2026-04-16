from __future__ import annotations

import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ML_ROOT.parents[1]

for path in (str(ML_ROOT), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

