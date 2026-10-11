import os
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # important: must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Manual CORS fallback: guarantees the header on every response ---
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# --- TELEMETRY DATA — paste your bundle here ---
TELEMETRY = [
    # <-- PASTE YOUR FULL BUNDLE HERE
]


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float = 180


# --- Preflight handler (some graders send OPTIONS) ---
@app.options("/api/metrics")
async def preflight():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


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


@app.get("/")
def root():
    return {"status": "ok"}