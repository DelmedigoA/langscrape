import json

log_path = "log.json"

with open(log_path, "r", encoding="utf-8") as f:
    data = json.load(f)

total_time = 0
success_count = 0
failure_count = 0
timeout_count = 0
failed_ids = []
timeout_ids = []

for id, entry in data.items():
    result = entry.get("result", "")
    t = entry.get("time")
    if result == "success":
        success_count += 1
        if isinstance(t, (int, float)):
            total_time += t
    elif result == "failure":
        failure_count += 1
        failed_ids.append(id)
    elif result == "timeout":
        timeout_count += 1
        timeout_ids.append(id)

summary = {
    "total_items": len(data),
    "success_count": success_count,
    "failure_count": failure_count,
    "timeout_count": timeout_count,
    "total_time_seconds": total_time,
    "avg_time_per_success": round(total_time / success_count, 2) if success_count else 0,
    "failed_ids": failed_ids,
    "timeout_ids": timeout_ids,
}

print(json.dumps(summary, indent=2, ensure_ascii=False))
