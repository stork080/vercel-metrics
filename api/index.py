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
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Manual CORS fallback ---
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# --- TELEMETRY DATA ---
TELEMETRY = [
    {"region": "apac", "service": "recommendations", "latency_ms": 208.67, "uptime_pct": 97.157, "timestamp": 20250301},
    {"region": "apac", "service": "support", "latency_ms": 194.03, "uptime_pct": 97.613, "timestamp": 20250302},
    {"region": "apac", "service": "catalog", "latency_ms": 210.27, "uptime_pct": 99.133, "timestamp": 20250303},
    {"region": "apac", "service": "analytics", "latency_ms": 155.9, "uptime_pct": 99.048, "timestamp": 20250304},
    {"region": "apac", "service": "support", "latency_ms": 135.52, "uptime_pct": 97.67, "timestamp": 20250305},
    {"region": "apac", "service": "recommendations", "latency_ms": 196.06, "uptime_pct": 99.179, "timestamp": 20250306},
    {"region": "apac", "service": "payments", "latency_ms": 209.56, "uptime_pct": 97.457, "timestamp": 20250307},
    {"region": "apac", "service": "recommendations", "latency_ms": 195.87, "uptime_pct": 99.26, "timestamp": 20250308},
    {"region": "apac", "service": "recommendations", "latency_ms": 212.9, "uptime_pct": 97.819, "timestamp": 20250309},
    {"region": "apac", "service": "support", "latency_ms": 201.71, "uptime_pct": 97.379, "timestamp": 20250310},
    {"region": "apac", "service": "payments", "latency_ms": 209.48, "uptime_pct": 98.711, "timestamp": 20250311},
    {"region": "apac", "service": "analytics", "latency_ms": 131.02, "uptime_pct": 99.167, "timestamp": 20250312},
    {"region": "emea", "service": "recommendations", "latency_ms": 179.91, "uptime_pct": 98.455, "timestamp": 20250301},
    {"region": "emea", "service": "checkout", "latency_ms": 210.52, "uptime_pct": 97.128, "timestamp": 20250302},
    {"region": "emea", "service": "support", "latency_ms": 190, "uptime_pct": 97.483, "timestamp": 20250303},
    {"region": "emea", "service": "payments", "latency_ms": 217.07, "uptime_pct": 97.226, "timestamp": 20250304},
    {"region": "emea", "service": "payments", "latency_ms": 137.68, "uptime_pct": 97.531, "timestamp": 20250305},
    {"region": "emea", "service": "support", "latency_ms": 148.45, "uptime_pct": 99.31, "timestamp": 20250306},
    {"region": "emea", "service": "catalog", "latency_ms": 149.78, "uptime_pct": 98.596, "timestamp": 20250307},
    {"region": "emea", "service": "catalog", "latency_ms": 151.49, "uptime_pct": 97.536, "timestamp": 20250308},
    {"region": "emea", "service": "checkout", "latency_ms": 196.2, "uptime_pct": 97.628, "timestamp": 20250309},
    {"region": "emea", "service": "catalog", "latency_ms": 162.37, "uptime_pct": 99.184, "timestamp": 20250310},
    {"region": "emea", "service": "recommendations", "latency_ms": 104.12, "uptime_pct": 99.293, "timestamp": 20250311},
    {"region": "emea", "service": "recommendations", "latency_ms": 209.97, "uptime_pct": 98.316, "timestamp": 20250312},
    {"region": "amer", "service": "analytics", "latency_ms": 148.51, "uptime_pct": 98.795, "timestamp": 20250301},
    {"region": "amer", "service": "catalog", "latency_ms": 224.94, "uptime_pct": 99.106, "timestamp": 20250302},
    {"region": "amer", "service": "analytics", "latency_ms": 148.99, "uptime_pct": 98.334, "timestamp": 20250303},
    {"region": "amer", "service": "checkout", "latency_ms": 139.15, "uptime_pct": 98.825, "timestamp": 20250304},
    {"region": "amer", "service": "support", "latency_ms": 204.96, "uptime_pct": 97.626, "timestamp": 20250305},
    {"region": "amer", "service": "catalog", "latency_ms": 176.69, "uptime_pct": 97.972, "timestamp": 20250306},
    {"region": "amer", "service": "catalog", "latency_ms": 139.28, "uptime_pct": 97.443, "timestamp": 20250307},
    {"region": "amer", "service": "catalog", "latency_ms": 140.66, "uptime_pct": 97.422, "timestamp": 20250308},
    {"region": "amer", "service": "support", "latency_ms": 208.44, "uptime_pct": 98.258, "timestamp": 20250309},
    {"region": "amer", "service": "support", "latency_ms": 223.3, "uptime_pct": 98.444, "timestamp": 20250310},
    {"region": "amer", "service": "support", "latency_ms": 113.2, "uptime_pct": 97.686, "timestamp": 20250311},
    {"region": "amer", "service": "checkout", "latency_ms": 127.65, "uptime_pct": 98.971, "timestamp": 20250312},
]


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float = 180


@app.options("/api/metrics")
async def preflight():
    return JSONResponse(content={}, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })


@app.post("/api/metrics")
def metrics(q: Query):
    result = {}
    for region in q.regions:
        rows = [r for r in TELEMETRY if r["region"] == region]
        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0,
            }
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 3),
            "breaches": int(sum(1 for l in latencies if l > q.threshold_ms)),
        }

    return result


@app.get("/")
def root():
    return {"status": "ok"}
