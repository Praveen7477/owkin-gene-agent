"""Reads the CSV and looks up genes / expression values."""

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "owkin_take_home_data.csv"


@lru_cache(maxsize=1)
def _load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    # lowercase copy of the cancer column so lookups aren't case-sensitive
    df["_cancer_norm"] = df["cancer_indication"].str.strip().str.lower()
    return df


def list_cancers() -> List[str]:
    """All cancer types in the dataset."""
    return sorted(_load()["cancer_indication"].unique().tolist())


def get_targets(cancer_name: str) -> List[str]:
    """Genes for a cancer (empty list if we don't have that cancer)."""
    df = _load()
    key = str(cancer_name).strip().lower()
    return df[df["_cancer_norm"] == key]["gene"].tolist()


def get_expressions(cancer_name: str, genes: List[str]) -> Dict[str, float]:
    """Median values for the given genes within one cancer."""
    # I filter by cancer too, not just gene name. A gene like TP53 shows up in
    # several cancers with different values, so filtering on the gene alone would
    # mix them up.
    df = _load()
    key = str(cancer_name).strip().lower()
    subset = df[(df["_cancer_norm"] == key) & (df["gene"].isin(genes))]
    return dict(zip(subset["gene"], subset["median_value"]))
