# File: mv_refresh/refresh_materialized_views.py
"""
Refresh materialized views incrementally for SmartCity_IoT project.

Usage:
  python mv_refresh/refresh_materialized_views.py
"""
import os
import json
from datetime import datetime, timedelta
import time
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError

# ----------------------------
# Config
# ----------------------------
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017")
DB_NAME = os.environ.get("MONGO_DB", "smartcity")

# safety window (in days) to reprocess slightly earlier window for late arrivals
SAFETY_WINDOW_DAYS = int(os.environ.get("SAFETY_WINDOW_DAYS", "2"))

# meta state collection name (stores checkpoints per MV)
META_STATE_COLL = "mv_meta_state"

# log file
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "mv_refresh.log")

# MV collection names
MV_DEFINITIONS = {
    "mv_daily_readings_per_device": {
        "description": "daily counts per sensor_id",
        # aggregation pipeline generator function (will accept from_ts)
        "pipeline_fn": "pipeline_daily_readings_per_device"
    },
    "mv_monthly_pollution_alerts": {
        "description": "monthly pollution alerts count per sensor",
        "pipeline_fn": "pipeline_monthly_pollution_alerts"
    },
    "mv_top5_temp_devices_monthly": {
        "description": "top 5 devices by max temperature per month",
        "pipeline_fn": "pipeline_top5_temp_devices_monthly"
    }
}

# ----------------------------
# Utilities
# ----------------------------
def log(msg):
    ts = datetime.utcnow().isoformat()
    line = f"{ts} - {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def now_utc():
    return datetime.utcnow()

# ----------------------------
# Aggregation pipelines (factory functions)
# Each returns a pipeline list that operates on source collection "sensors"
# The function receives from_ts (datetime) to filter new/changed documents.
# ----------------------------
def pipeline_daily_readings_per_device(from_ts):
    # group per sensor per day, count
    return [
        {"$match": {"timestamp": {"$gte": from_ts}}},
        {"$project": {
            "sensor_id": 1,
            "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
        }},
        {"$group": {
            "_id": {"sensor": "$sensor_id", "day": "$day"},
            "totalReadings": {"$sum": 1}
        }},
        # shape to upsert-friendly doc
        {"$project": {
            "_id": 0,
            "sensor": "$_id.sensor",
            "day": "$_id.day",
            "totalReadings": 1
        }}
    ]

def pipeline_monthly_pollution_alerts(from_ts, threshold=100):
    return [
        {"$match": {"timestamp": {"$gte": from_ts}, "pollution_level": {"$gt": threshold}}},
        {"$project": {
            "sensor_id": 1,
            "month": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}}
        }},
        {"$group": {
            "_id": {"sensor": "$sensor_id", "month": "$month"},
            "alertsCount": {"$sum": 1}
        }},
        {"$project": {"_id": 0, "sensor": "$_id.sensor", "month": "$_id.month", "alertsCount": 1}}
    ]

def pipeline_top5_temp_devices_monthly(from_ts):
    # find max temp per sensor per month, then group months and pick top 5
    return [
        {"$match": {"timestamp": {"$gte": from_ts}}},
        {"$project": {
            "sensor_id": 1,
            "month": {"$dateToString": {"format": "%Y-%m", "date": "$timestamp"}},
            "temperature": 1
        }},
        {"$group": {
            "_id": {"sensor": "$sensor_id", "month": "$month"},
            "maxTemp": {"$max": "$temperature"}
        }},
        {"$sort": {"_id.month": 1, "maxTemp": -1}},
        {"$group": {
            "_id": "$_id.month",
            "top": {"$push": {"sensor": "$_id.sensor", "maxTemp": "$maxTemp"}}
        }},
        {"$project": {
            "_id": 0,
            "month": "$_id",
            "top5": {"$slice": ["$top", 5]}
        }}
    ]

# ----------------------------
# Main refresh logic
# ----------------------------
def refresh_mv(client, mv_name, pipeline_fn_name):
    db = client[DB_NAME]
    sensors = db["sensors"]
    meta = db[META_STATE_COLL]
    mv_coll = db[mv_name]

    # read last checkpoint
    state_doc = meta.find_one({"mv": mv_name})
    if state_doc and "last_processed_ts" in state_doc:
        last_ts = state_doc["last_processed_ts"]
    else:
        # if no checkpoint, start from epoch far past
        last_ts = datetime(1970, 1, 1)

    # safety window: subtract days
    from_ts = last_ts - timedelta(days=SAFETY_WINDOW_DAYS)
    # clamp to epoch if needed
    if from_ts.year < 1970:
        from_ts = datetime(1970, 1, 1)

    log(f"MV={mv_name} starting refresh. last_checkpoint={last_ts.isoformat()} from_ts={from_ts.isoformat()}")

    # build pipeline by calling factory
    pipeline_fn = globals()[pipeline_fn_name]
    pipeline = pipeline_fn(from_ts)

    # append $merge stage to write into mv collection (do upsert semantics)
    merge_stage = {
        "$merge": {
            "into": mv_name,
            "on": ["sensor", "day"] if mv_name == "mv_daily_readings_per_device" else ["sensor", "month"] if mv_name == "mv_monthly_pollution_alerts" else "month",
            "whenMatched": "merge",   # merge fields
            "whenNotMatched": "insert"
        }
    }
    # adjust key for mv_top5_temp_devices_monthly
    if mv_name == "mv_top5_temp_devices_monthly":
        # for top5 we merge by month (document per month)
        merge_stage["$merge"]["on"] = "month"
    pipeline_with_merge = pipeline + [merge_stage]

    start = time.time()
    try:
        # run aggregation with $merge - server-side will write results into mv collection
        log(f"Running aggregation pipeline for {mv_name} (server-side $merge)")
        sensors.aggregate(pipeline_with_merge, allowDiskUse=True)
        duration = time.time() - start

        # compute docs affected (approx): count documents with timestamp >= from_ts if feasible, 
        # or count items in mv collection (not precise for incremental)
        docs_affected = mv_coll.count_documents({})  # post-state
        # update meta state: new checkpoint = now
        new_checkpoint = now_utc()
        meta.update_one({"mv": mv_name}, {"$set": {"last_processed_ts": new_checkpoint, "last_run": now_utc(), "status": "ok"}}, upsert=True)

        log(f"MV={mv_name} refresh completed. duration_s={duration:.2f}, docs_after={docs_affected}")
        return {"mv": mv_name, "duration_s": duration, "docs_after": docs_affected, "error": None}
    except PyMongoError as e:
        duration = time.time() - start
        log(f"ERROR refreshing {mv_name}: {repr(e)}")
        meta.update_one({"mv": mv_name}, {"$set": {"last_error": str(e), "last_run": now_utc(), "status": "error"}}, upsert=True)
        return {"mv": mv_name, "duration_s": duration, "docs_after": None, "error": str(e)}

def main():
    client = MongoClient(MONGO_URI)
    results = []
    # iterate MVs
    for mv_name, spec in MV_DEFINITIONS.items():
        pipeline_fn_name = spec["pipeline_fn"]
        res = refresh_mv(client, mv_name, pipeline_fn_name)
        results.append(res)

    # write a run summary to logs
    run_summary = {"run_at": now_utc().isoformat(), "results": results}
    summary_path = os.path.join(LOG_DIR, f"mv_refresh_summary_{int(time.time())}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(run_summary, f, indent=2, default=str)
    log(f"MV refresh job finished. summary_file={summary_path}")

if __name__ == "__main__":
    main()
