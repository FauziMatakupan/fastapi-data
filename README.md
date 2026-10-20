# FastAPI-Data-Lite

Lightweight **FastAPI + Polars** data microservice starter. Free, MIT-licensed.

Upload a CSV/Parquet file, get per-column profiling and one-pass descriptive
statistics back over HTTP. Lazy Polars frames keep memory flat on large files.

```
POST /api/v1/data/upload        → dataset_id
GET  /api/v1/data/{id}/profile  → dtypes, nulls, cardinality
GET  /api/v1/data/{id}/stats    → mean, std, quartiles (linear interpolation)
```

## Quickstart

```bash
pip install -e .
uvicorn app.main:app --reload
# Swagger UI: http://localhost:8000/docs
```

```bash
curl -F "file=@data.csv" localhost:8000/api/v1/data/upload
# {"dataset_id": "...", "size_bytes": 12345}
curl localhost:8000/api/v1/data/<dataset_id>/stats
```

## What's inside

- **App factory** with CORS + `/health` (app/main.py)
- **12-factor settings** via pydantic-settings (app/core/config.py)
- **Polars engine** - lazy CSV/Parquet ingestion, one-pass stats, profiling
  (app/services/data_engine.py)
- **Upload → profile → stats** endpoints (app/api/v1/endpoints/data.py)
- **Tested** - pytest suite covering the full upload-to-stats flow

## Need more?

Lite is deliberately small. The [Pro edition](https://github.com/FauziMatakupan/fastapi-datapro)
adds what production deployments actually need:

| | Lite | Pro |
|---|:---:|:---:|
| FastAPI + Polars stats engine | ✅ | ✅ |
| JWT + API-key auth | — | ✅ |
| Pandera schema contracts | — | ✅ |
| Celery/Redis background jobs | — | ✅ |
| Hermetic Docker Compose | — | ✅ |
| Polar.sh license billing module | — | ✅ |

## License

MIT - free to use, modify, and ship. See [LICENSE](LICENSE).
