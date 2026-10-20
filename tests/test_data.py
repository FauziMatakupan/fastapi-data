"""Tests for the Lite starter: health, upload, profile, stats flow."""

from __future__ import annotations

import csv

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_upload_rejects_bad_type(client):
    r = client.post("/api/v1/data/upload", files={"file": ("x.txt", b"nope", "text/plain")})
    assert r.status_code == 415


def test_upload_profile_stats_flow(client, tmp_path):
    csv_path = tmp_path / "sample.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["a", "b"])
        for i in range(10):
            w.writerow([i, i * 2])

    with csv_path.open("rb") as f:
        r = client.post("/api/v1/data/upload", files={"file": ("sample.csv", f, "text/csv")})
    assert r.status_code == 200, r.text
    ds_id = r.json()["dataset_id"]

    prof = client.get(f"/api/v1/data/{ds_id}/profile")
    assert prof.status_code == 200
    assert prof.json()["a"]["dtype"] == "Int64"

    stats = client.get(f"/api/v1/data/{ds_id}/stats")
    assert stats.status_code == 200
    col = stats.json()["columns"]["a"]
    assert col["count"] == 10
    assert col["mean"] == 4.5
    assert col["median"] == 4.5  # linear interpolation

    missing = client.get("/api/v1/data/nonexistent/stats")
    assert missing.status_code == 404


def test_engine_summary_unit():
    import polars as pl

    from app.services.data_engine import summary_stats

    df = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0]})
    s = summary_stats(df.lazy())
    assert s["columns"]["x"]["mean"] == 2.5
    assert s["columns"]["x"]["median"] == 2.5