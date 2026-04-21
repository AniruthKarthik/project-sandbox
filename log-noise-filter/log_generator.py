"""
Log Generator — produces realistic application log files for testing.
Usage:
    python log_generator.py                        # 1000 lines -> app.log
    python log_generator.py --lines=5000           # custom line count
    python log_generator.py --lines=500 --out=test.log
"""

import random
import sys
import os
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Message pools
# ---------------------------------------------------------------------------
ERRORS = [
    "Database connection failed",
    "Timeout while contacting API",
    "Authentication token expired",
    "File permission denied on /var/log/app.log",
    "Cache synchronization failed for node 192.168.1.42",
    "SSL certificate validation error for host 'api.example.com'",
    "Queue processing delay exceeded 500ms threshold",
    "Unexpected null value in field 'user_id' at row 13",
    "Microservice heartbeat missed for service 'order-processor'",
    "Out of memory: failed to allocate 512MB",
    "Deadlock detected on table 'transactions'",
    "Max retry attempts reached for job 8821",
    "Unhandled exception in worker thread 4",
    "Config file missing: /etc/app/config.yaml",
    "Failed to write to disk: no space left on device",
]

WARNINGS = [
    "Disk space low",
    "Memory usage high: 87%",
    "Response time degraded: 1200ms",
    "Retry attempt 2 of 3 for request 9921",
    "Deprecated API endpoint called: /v1/users",
    "Connection pool nearing limit: 95/100",
    "Rate limit approaching for client 10.0.0.5",
]

INFOS = [
    "User logged in",
    "User logged out",
    "Health check passed",
    "Backup completed successfully",
    "Scheduled job started",
    "Metrics flushed",
    "Cache warmed up",
    "Service restarted",
    "New deployment detected: v2.4.1",
    "Config reloaded",
]

DEBUGS = [
    "Entering function process_request",
    "Query executed in 4ms",
    "Cache hit for key session:abc123",
    "Payload size: 2048 bytes",
    "Thread pool size: 8",
]

# Level → (pool, weight)
LEVELS = [
    ("ERROR",   ERRORS,   20),
    ("WARNING", WARNINGS, 15),
    ("INFO",    INFOS,    50),
    ("DEBUG",   DEBUGS,   15),
]

# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------
def generate_lines(n: int, start: datetime):
    level_names  = [l[0] for l in LEVELS]
    level_pools  = [l[1] for l in LEVELS]
    level_weights= [l[2] for l in LEVELS]
    ts = start
    for _ in range(n):
        ts += timedelta(seconds=random.randint(0, 5))
        level = random.choices(level_names, weights=level_weights, k=1)[0]
        pool  = level_pools[level_names.index(level)]
        msg   = random.choice(pool)
        yield f"{ts.strftime('%Y-%m-%d %H:%M:%S')} {level} {msg}\n"


def parse_args(argv):
    cfg = {"lines": 1000, "out": "app.log"}
    for a in argv[1:]:
        if a.startswith("--lines="):
            cfg["lines"] = int(a.split("=", 1)[1])
        elif a.startswith("--out="):
            cfg["out"] = a.split("=", 1)[1]
    return cfg


def main():
    cfg   = parse_args(sys.argv)
    n     = cfg["lines"]
    out   = cfg["out"]
    start = datetime(2025, 3, 5, 10, 0, 0)

    with open(out, "w", encoding="utf-8") as fh:
        for line in generate_lines(n, start):
            fh.write(line)

    size = os.path.getsize(out)
    print(f"Generated {n} lines → {out}  ({size:,} bytes)")
    print(f"Run: python log_analyzer.py {out}")


if __name__ == "__main__":
    main()
