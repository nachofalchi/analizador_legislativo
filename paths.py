from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
VOTATIONS_DIR = DATA_DIR / "votations"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
SRC_DIR = BASE_DIR / "src"