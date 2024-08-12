from pathlib import Path

THIS = Path(__file__).resolve()
ROOT = THIS.parent
SERVICES = ROOT / "services"

NYUNTAM = "nyuntam"

__all__ = ["NYUNTAM"]
