"""
Dataset Builder — IRS Phase 4.

Orchestrates the full Phase 4 pipeline:

    SyntheticDatasetGenerator  →  raw DataFrame
            ↓
    DataFrameFeatureEngineer   →  validated + cleaned DataFrame
            ↓
    CSV saved to  data/synthetic_progression_dataset.csv

The builder is the single entry point for Phase 4.  Phase 5 will call
``DatasetBuilder.load()`` to retrieve the ready-to-train dataset.

Usage
-----
    # Generate and save
    python -m ml.dataset_builder

    # Or from code
    builder = DatasetBuilder()
    df      = builder.build_and_save()
    X, y    = builder.load()
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from ml.synthetic_data_generator import (
    SyntheticDatasetGenerator,
    SyntheticDatasetConfig,
    SYNTHETIC_DATA_DISCLAIMER,
)
from ml.feature_engineering import DataFrameFeatureEngineer, FEATURE_NAMES, TARGET_COLUMN

logger = logging.getLogger(__name__)

# Default output path — relative to the project root.
DEFAULT_DATASET_PATH: Path = Path(__file__).resolve().parent.parent / "data" / "synthetic_progression_dataset.csv"


class DatasetBuilder:
    """
    Builds, validates, saves, and loads the Phase 4 ML dataset.

    Parameters
    ----------
    output_path : Path | str | None
        Where to write the CSV.  Defaults to
        ``data/synthetic_progression_dataset.csv`` in the project root.
    config : SyntheticDatasetConfig | None
        Generator configuration.  Defaults to 1 000 samples, seed 42.
    """

    def __init__(
        self,
        output_path: Path | str | None = None,
        config: SyntheticDatasetConfig | None = None,
    ) -> None:
        self._path = Path(output_path) if output_path else DEFAULT_DATASET_PATH
        self._generator = SyntheticDatasetGenerator(config)
        self._engineer = DataFrameFeatureEngineer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_and_save(self) -> pd.DataFrame:
        """
        Generate the synthetic dataset, validate it, and persist it to CSV.

        Returns:
            The validated DataFrame (features + target).
        """
        logger.info("Phase 4 — building synthetic dataset.")

        raw_df = self._generator.generate()
        clean_df = self._engineer.validate_and_clean(raw_df)

        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._save_csv(clean_df)

        logger.info("Dataset saved to %s (%d rows).", self._path, len(clean_df))
        return clean_df

    def load(self) -> tuple[pd.DataFrame, pd.Series]:
        """
        Load the saved dataset and return (X, y).

        Returns:
            (X, y) — feature matrix and target vector.

        Raises:
            FileNotFoundError: If the dataset CSV has not been generated yet.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self._path}. "
                "Run DatasetBuilder.build_and_save() first."
            )
        df = pd.read_csv(self._path, comment="#")
        X, y = self._engineer.get_X_y(df)
        logger.info("Dataset loaded from %s: X=%s y=%s.", self._path, X.shape, y.shape)
        return X, y

    def load_raw(self) -> pd.DataFrame:
        """
        Load the saved dataset as a raw DataFrame (features + target column).

        Returns:
            Full DataFrame including the target column.

        Raises:
            FileNotFoundError: If the dataset CSV has not been generated yet.
        """
        if not self._path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self._path}. "
                "Run DatasetBuilder.build_and_save() first."
            )
        return pd.read_csv(self._path, comment="#")

    @property
    def dataset_path(self) -> Path:
        """Absolute path to the dataset CSV file."""
        return self._path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _save_csv(self, df: pd.DataFrame) -> None:
        """Write the DataFrame to CSV with a disclaimer comment header."""
        disclaimer_line = f"# {SYNTHETIC_DATA_DISCLAIMER}\n"
        with self._path.open("w", newline="", encoding="utf-8") as fh:
            fh.write(disclaimer_line)
            df.to_csv(fh, index=False)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _print_summary(df: pd.DataFrame) -> None:
    """Print a human-readable dataset summary to stdout."""
    n = len(df)
    promoted = int(df[TARGET_COLUMN].sum())
    not_promoted = n - promoted

    print("\n" + "=" * 60)
    print("  IRS Phase 4 — Synthetic Dataset Summary")
    print("=" * 60)
    print(f"  DISCLAIMER : {SYNTHETIC_DATA_DISCLAIMER}")
    print(f"  Rows       : {n:,}")
    print(f"  Features   : {len(FEATURE_NAMES)}")
    print(f"  Target     : {TARGET_COLUMN}")
    print(f"  Promoted   : {promoted:,}  ({promoted / n * 100:.1f}%)")
    print(f"  Not Promoted: {not_promoted:,}  ({not_promoted / n * 100:.1f}%)")
    print()
    print("  Feature statistics:")
    print(df[FEATURE_NAMES].describe().round(3).to_string())
    print()
    print("  Readiness score distribution by promotion outcome:")
    print(
        df.groupby(TARGET_COLUMN)["readiness_score"]
        .describe()[["mean", "std", "min", "max"]]
        .round(2)
        .to_string()
    )
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    )

    n_samples = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000
    config = SyntheticDatasetConfig(n_samples=n_samples)
    builder = DatasetBuilder(config=config)
    df = builder.build_and_save()
    _print_summary(df)
    print(f"Dataset written to: {builder.dataset_path}")
