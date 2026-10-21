# FastAPI-Data

FastAPI Polars data microservice for profiling CSV and Parquet files over HTTP.

<!-- Banner slot: drop an image at docs/banner.png and uncomment the line below.
<p align="center"><img src="docs/banner.png" alt="FastAPI-Data, a FastAPI Polars data microservice" width="880"></p>
-->

<!-- Suggested GitHub about text: A FastAPI Polars data microservice for CSV and Parquet profiling and stats over HTTP. -->

This repository is a FastAPI data starter with 185 lines of application code in five modules. Upload a CSV or Parquet file, then call the profiling endpoint or the statistics endpoint to get per-column dtypes, null counts and quartiles back as JSON. Every module is self-contained, so the engine can be lifted into a project you already have.

## Quickstart

Python 3.11 or newer.

1. Clone and install the package in editable mode:

```bash
git clone https://github.com/FauziMatakupan/fastapi-data.git
cd fastapi-data
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Start the API:

```bash
uvicorn app.main:app --reload
```

It listens on `http://localhost:8000`, and the generated OpenAPI page is at `http://localhost:8000/docs`.

3. Upload a file:

```bash
printf "a,b\n0,0\n1,2\n2,4\n3,6\n4,8\n5,10\n6,12\n7,14\n8,16\n9,18\n" > sample.csv
curl -s -F "file=@sample.csv" http://localhost:8000/api/v1/data/upload
```

```json
{"dataset_id": "891903036.csv", "size_bytes": 49}
```

The id is a hash of the filename, so yours will look different.

4. Read the profile and the statistics:

```bash
DS=$(curl -s -F "file=@sample.csv" http://localhost:8000/api/v1/data/upload | python3 -c 'import json,sys; print(json.load(sys.stdin)["dataset_id"])')
curl -s "http://localhost:8000/api/v1/data/$DS/profile"
curl -s "http://localhost:8000/api/v1/data/$DS/stats"
```

Full response bodies are shown under [API surface](#api-surface).

## What it does

- **Upload endpoint.** `POST /api/v1/data/upload` takes a CSV or Parquet file and returns a dataset id that the two read endpoints use.
- **CSV Parquet HTTP profiling endpoint.** `GET /api/v1/data/{dataset_id}/profile` returns dtype, null count and distinct count for every column of an uploaded file.
- **Statistics endpoint.** `GET /api/v1/data/{dataset_id}/stats` returns count, mean, standard deviation, min, p25, median, p75 and max for every numeric column, computed in one pass.
- **Operational basics.** `GET /health` answers with a status for a probe, `/docs` serves the OpenAPI page, and uploaded files land in `data/uploads/`.

## API surface

| Method | Path | Returns |
|---|---|---|
| POST | `/api/v1/data/upload` | `dataset_id` and `size_bytes` |
| GET | `/api/v1/data/{dataset_id}/profile` | dtype, null count and distinct count per column |
| GET | `/api/v1/data/{dataset_id}/stats` | shape plus count, mean, std, min, quartiles and max per numeric column |
| GET | `/health` | `{"status": "ok", "environment": "development"}` |
| GET | `/docs` | Swagger UI generated from the OpenAPI schema |

Profile of a ten-row CSV with the columns `a` and `b`:

```bash
curl -s "http://localhost:8000/api/v1/data/$DS/profile"
```

```json
{
  "a": {"dtype": "Int64", "nulls": 0, "n_unique": 10},
  "b": {"dtype": "Int64", "nulls": 0, "n_unique": 10}
}
```

Statistics for the same file:

```bash
curl -s "http://localhost:8000/api/v1/data/$DS/stats"
```

```json
{
  "shape": [10, 2],
  "columns": {
    "a": {
      "count": 10,
      "nulls": 0,
      "mean": 4.5,
      "std": 3.0276503540974917,
      "min": 0,
      "p25": 2.25,
      "median": 4.5,
      "p75": 6.75,
      "max": 9
    },
    "b": {
      "count": 10,
      "nulls": 0,
      "mean": 9.0,
      "std": 6.0553007081949835,
      "min": 0,
      "p25": 4.5,
      "median": 9.0,
      "p75": 13.5,
      "max": 18
    }
  }
}
```

A few details worth knowing:

- `stats` only covers numeric columns. `profile` lists every column, so text columns still show up there.
- Quartiles use linear interpolation. Polars defaults to `nearest`, which snaps to a real value and returns a different median when the row count is even.
- `dataset_id` is `abs(hash(filename)) & 0xFFFFFFFF`. Python randomizes the hash seed per process, so a restart yields a different id for the same filename. Two uploads of the same filename in one process lifetime write the same path, so the second replaces the first.
- An unknown dataset returns 404, and a file type other than CSV or Parquet returns 415.

## Why Polars

The engine parses files through Polars and builds the query plan before any data is materialized. The endpoints collect the frame once at the API boundary, which keeps the memory story simple and predictable: an uploaded file fully materializes in RAM, so size the machine for the largest file you expect. Teams looking for a FastAPI pandas alternative can keep the same JSON shape and change the engine underneath.

## Testing

```bash
pytest -q
```

Four tests cover the health check, the 415 response for an unsupported file type, the upload to profile to stats flow, and the quantile interpolation of the stats engine.

```bash
ruff check .
```

`ruff` is configured in `pyproject.toml` with a line length of 100.

## Project layout

```
app/
  main.py                    FastAPI app factory, CORS middleware, /health
  core/config.py             settings loaded from the environment and .env
  api/v1/router.py           route registration
  api/v1/endpoints/data.py   upload, profile and stats endpoints
  services/data_engine.py    lazy ingestion, profiling, summary statistics
tests/test_data.py           upload to stats flow and engine unit tests
data/uploads/                uploaded datasets, ignored by git
```

Settings live in `app/core/config.py` and are read from environment variables or a `.env` file: `APP_NAME`, `ENVIRONMENT`, `API_V1_PREFIX`, `DATA_DIR` and `MAX_UPLOAD_MB`.

`MAX_UPLOAD_MB` is part of the settings object and the upload endpoint does not read it yet, so add the size check yourself when the service is reachable by other people.

## The complete edition

Everything in this repository is MIT licensed and usable as it is.

Growth tends to bring requirements this core does not cover, such as authentication, schema contracts and background jobs. Those live in the complete edition, which is documented on the [project site](https://matakupan-labs.vercel.app/docs.html) with update notes in the [changelog](https://matakupan-labs.vercel.app/changelog.html).

Take the engine, the endpoints and the tests from here.

## License

MIT, free to use, modify and ship. See [LICENSE](LICENSE).
