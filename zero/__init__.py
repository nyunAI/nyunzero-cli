from pathlib import Path

THIS = Path(__file__).resolve()
ROOT = THIS.parent
SERVICES = ROOT / "services"

NYUNTAM = "nyuntam"
NYUNTAM_ADAPT = "nyuntam_adapt"

__all__ = ["NYUNTAM", "NYUNTAM_ADAPT"]
