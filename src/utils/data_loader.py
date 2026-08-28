"""
Data loader utilities.

Provides a single entry point for loading and saving data in the data/ directory.
Pages should use these functions instead of reading files directly,
keeping file handling and path logic out of the app code.

Usage:
------
from utils.data_loader import load_csv, save_csv

data = load_csv("users.csv")  # returns list[dict], ready for Dash components
df   = load_csv("users.csv", as_dataframe=True)  # returns pd.DataFrame

# Append a new row:
save_csv("users.csv", {"name": "Anna", "department": "HR", ...})
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"


def load_csv(filename: str, as_dataframe: bool = False) -> list[dict] | pd.DataFrame:
    """
    Load a CSV file from the data/ directory.

    Parameters
    ----------
    filename : str
        Filename relative to the data/ directory, e.g. "users.csv".
    as_dataframe : bool
        If True, return a pd.DataFrame. If False (default), return list[dict]
        which can be passed directly to Dash table components.
    """
    path = DATA_DIR / filename
    df = pd.read_csv(path)
    return df if as_dataframe else df.to_dict("records")


def save_csv(filename: str, row: dict) -> None:
    """
    Append a single row to a CSV file in the data/ directory.
    Creates the file if it does not exist.

    Parameters
    ----------
    filename : str
        Filename relative to the data/ directory, e.g. "users.csv".
    row : dict
        A single record to append, e.g. {"name": "Anna", "department": "HR"}.
    """
    path = DATA_DIR / filename
    df_new = pd.DataFrame([row])
    if path.exists():
        df_existing = pd.read_csv(path)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.to_csv(path, index=False)
