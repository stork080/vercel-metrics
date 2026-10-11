import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# CORS: allow POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# TELEMETRY DATA — paste the downloaded bundle contents here
# as a Python list of dicts. Example shape:
# TELEMETRY = [
#     {"region": "emea", "latency_ms": 120, "uptime": 0.99},
#     {"region": "amer", "latency_ms": 200, "uptime": 0.98},
#     ...
# ]
# ------------------------------------------------------------------
TELEMETRY = [
    {"region": "emea", "latency_ms": 120, "uptime": 0.99},
    {"region": "amer", "latency_ms": 200, "uptime": 0.98},
    # ...
]


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float = 180


@app.post("/api/metrics")
def metrics(q: Query):
    result = {}
    for region in q.regions:
        rows = [r for r in TELEMETRY if r.get("region") == region]
        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0,
            }
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r.get("uptime", 0) for r in rows]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": int(sum(1 for l in latencies if l > q.threshold_ms)),
        }

    return result


# Optional root route so you can sanity-check the deploy in a browser
@app.get("/")
def root():
    return {"status": "ok"}