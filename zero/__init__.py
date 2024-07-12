from pathlib import Path

THIS = Path(__file__).resolve()
ROOT = THIS.parent
SERVICES = ROOT / "services"

NYUNTAM = SERVICES / "nyuntam"
NYUNTAM_ADAPT = SERVICES / "nyuntam-adapt"

__all__ = ["NYUNTAM", "NYUNTAM_ADAPT"]
