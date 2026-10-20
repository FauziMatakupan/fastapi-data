"""Polars-powered data engine: lazy ingestion + summary statistics.

The heart of the starter. Everything is written against lazy Frames so
operations optimize before touching memory. For production needs - schema
validation, background jobs, auth, billing - see the Pro edition:
https://github.com/FauziMatakupan/fastapi-datapro
"""

from __future__ import annotations

from pathlib import Path

import polars as pl


def load_frame(path: str | Path) -> pl.LazyFrame:
    """Load CSV or Parquet into a lazy frame (extension-detected).

    Lazy by design: filters and projections are pushed down before any data
    is read into memory. Collect at the last responsible moment.
    """
    p = Path(path)
    if p.suffix.lower() in {".parquet", ".pq"}:
        return pl.scan_parquet(p)
    return pl.scan_csv(p)


def summary_stats(lf: pl.LazyFrame) -> dict:
    """Column-wise descriptive statistics - collected once, in one pass.

    Quartiles use linear interpolation (Polars' default "nearest" snaps to
    real values, which surprises statistics users).
    """
    df = lf.collect()
    numeric = [c for c, dt in df.schema.items() if dt.is_numeric()]
    out: dict = {"shape": df.shape, "columns": {}}
    for col in numeric:
        s = df.get_column(col)
        out["columns"][col] = {
            "count": s.len(),
            "nulls": s.null_count(),
            "mean": s.mean(),
            "std": s.std(),
            "min": s.min(),
            "p25": s.quantile(0.25, interpolation="linear"),
            "median": s.quantile(0.50, interpolation="linear"),
            "p75": s.quantile(0.75, interpolation="linear"),
            "max": s.max(),
        }
    return out


def profile_frame(lf: pl.LazyFrame) -> dict:
    """Lightweight profile: dtypes, null counts, cardinality per column."""
    df = lf.collect()
    return {
        c: {
            "dtype": str(dt),
            "nulls": df.get_column(c).null_count(),
            "n_unique": df.get_column(c).n_unique(),
        }
        for c, dt in df.schema.items()
    }