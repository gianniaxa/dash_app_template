"""
Unit tests for utils/data_loader.py

These tests verify CSV loading and saving logic in isolation.
No database or external services required.
"""

import pytest
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_sample_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


SAMPLE_ROWS = [
    {"name": "Alice", "nationality": "German",  "email": "alice@example.com", "birthday": "1990-03-15"},
    {"name": "Bob",   "nationality": "Swiss",   "email": "bob@example.com",   "birthday": "1985-07-22"},
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLoadCsv:

    def test_returns_list_of_dicts_by_default(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        write_sample_csv(csv_file, SAMPLE_ROWS)

        # Patch DATA_DIR to point to tmp_path
        import utils.data_loader as loader
        original_dir = loader.DATA_DIR
        loader.DATA_DIR = tmp_path

        result = loader.load_csv("test.csv")

        loader.DATA_DIR = original_dir

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Alice"

    def test_returns_dataframe_when_requested(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        write_sample_csv(csv_file, SAMPLE_ROWS)

        import utils.data_loader as loader
        original_dir = loader.DATA_DIR
        loader.DATA_DIR = tmp_path

        result = loader.load_csv("test.csv", as_dataframe=True)

        loader.DATA_DIR = original_dir

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["name", "nationality", "email", "birthday"]

    def test_raises_when_file_missing(self, tmp_path):
        import utils.data_loader as loader
        original_dir = loader.DATA_DIR
        loader.DATA_DIR = tmp_path

        with pytest.raises(FileNotFoundError):
            loader.load_csv("nonexistent.csv")

        loader.DATA_DIR = original_dir


class TestSaveCsv:

    def test_appends_row_to_existing_file(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        write_sample_csv(csv_file, SAMPLE_ROWS)

        import utils.data_loader as loader
        original_dir = loader.DATA_DIR
        loader.DATA_DIR = tmp_path

        loader.save_csv("test.csv", {
            "name": "Clara",
            "nationality": "Austrian",
            "email": "clara@example.com",
            "birthday": "1992-11-08",
        })

        result = pd.read_csv(csv_file)
        loader.DATA_DIR = original_dir

        assert len(result) == 3
        assert result.iloc[-1]["name"] == "Clara"

    def test_creates_file_if_not_exists(self, tmp_path):
        import utils.data_loader as loader
        original_dir = loader.DATA_DIR
        loader.DATA_DIR = tmp_path

        loader.save_csv("new.csv", {"name": "Dave", "nationality": "French"})

        result = pd.read_csv(tmp_path / "new.csv")
        loader.DATA_DIR = original_dir

        assert len(result) == 1
        assert result.iloc[0]["name"] == "Dave"
