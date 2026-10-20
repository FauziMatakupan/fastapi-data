"""Data endpoints: upload, profile, stats - powered by Polars.

No auth in Lite: this starter is for learning and prototyping. Add auth by
copying the pattern from the Pro edition, or your own dependency.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.core.config import settings
from app.services.data_engine import load_frame, profile_frame, summary_stats

router = APIRouter()
_UPLOAD_DIR = Path(settings.data_dir) / "uploads"


@router.post("/upload")
async def upload(file: UploadFile) -> dict:
    """Upload a CSV/Parquet file; returns a dataset id for later calls."""
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "data.csv").suffix.lower()
    if suffix not in {".csv", ".parquet", ".pq"}:
        raise HTTPException(status_code=415, detail="Only CSV/Parquet accepted")
    dest = _UPLOAD_DIR / f"{abs(hash(file.filename)) & 0xFFFFFFFF}{suffix}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"dataset_id": dest.name, "size_bytes": dest.stat().st_size}


@router.get("/{dataset_id}/profile")
async def profile(dataset_id: str) -> dict:
    """Per-column dtype / null count / cardinality."""
    path = _UPLOAD_DIR / dataset_id
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    return profile_frame(load_frame(path))


@router.get("/{dataset_id}/stats")
async def stats(dataset_id: str) -> dict:
    """One-pass numeric descriptive statistics."""
    path = _UPLOAD_DIR / dataset_id
    if not path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    return summary_stats(load_frame(path))