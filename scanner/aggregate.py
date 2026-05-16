#!/usr/bin/env python3
"""
aggregate.py  —  Scan History Manager
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "scan_history.db"

DDL = """
CREATE TABLE IF NOT EXISTS scans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    total_checks    INTEGER NOT NULL,
    passed          INTEGER NOT NULL,
    failed          INTEGER NOT NULL,
    compliance_score REAL   NOT NULL,
    scanned_dirs    TEXT,
    raw_json        TEXT
);

CREATE TABLE IF NOT EXISTS findings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id     INTEGER NOT NULL REFERENCES scans(id),
    tool        TEXT,
    check_id    TEXT,
    check_name  TEXT,
    severity    TEXT,
    passed      INTEGER,
    resource    TEXT,
    file        TEXT,
    line_start  INTEGER,
    line_end    INTEGER,
    module      TEXT,
    guideline   TEXT
);

CREATE INDEX IF NOT EXISTS idx_findings_scan_id  ON findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_scans_timestamp   ON scans(timestamp);
"""

def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(DDL)
    conn.commit()
    return conn

def update_history(scan_result: dict) -> int:
    conn = _get_conn()
    cur  = conn.cursor()

    cur.execute(
        """
        INSERT INTO scans
            (timestamp, total_checks, passed, failed, compliance_score,
             scanned_dirs, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            scan_result["timestamp"],
            scan_result["total_checks"],
            scan_result["passed"],
            scan_result["failed"],
            scan_result["compliance_score"],
            json.dumps(scan_result.get("scanned_dirs", [])),
            json.dumps(scan_result),
        ),
    )
    scan_id = cur.lastrowid

    for f in scan_result.get("findings", []):
        cur.execute(
            """
            INSERT INTO findings
                (scan_id, tool, check_id, check_name, severity,
                 passed, resource, file, line_start, line_end, module, guideline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scan_id,
                f.get("tool"),
                f.get("check_id"),
                f.get("check_name"),
                f.get("severity"),
                1 if f.get("passed") else 0,
                f.get("resource"),
                f.get("file"),
                f.get("line_start", 0),
                f.get("line_end", 0),
                f.get("module"),
                f.get("guideline"),
            ),
        )

    conn.commit()
    conn.close()

    print(f"  ✓ History updated  → db/scan_history.db  (scan_id={scan_id})")
    return scan_id

def get_history(limit: int = 30) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        """
        SELECT id, timestamp, total_checks, passed, failed, compliance_score, scanned_dirs
        FROM   scans
        ORDER  BY id DESC
        LIMIT  ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]

def get_latest_findings(limit_scans: int = 1) -> list[dict]:
    conn = _get_conn()
    scan_ids = conn.execute(
        "SELECT id FROM scans ORDER BY id DESC LIMIT ?", (limit_scans,)
    ).fetchall()

    if not scan_ids:
        conn.close()
        return []

    ids_placeholder = ",".join("?" * len(scan_ids))
    ids_values      = [r["id"] for r in scan_ids]

    rows = conn.execute(
        f"""
        SELECT f.*, s.timestamp, s.compliance_score
        FROM   findings f
        JOIN   scans    s ON f.scan_id = s.id
        WHERE  f.scan_id IN ({ids_placeholder})
        ORDER  BY f.severity, f.tool, f.check_id
        """,
        ids_values,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_summary() -> dict:
    conn = _get_conn()
    total_scans = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]

    if total_scans == 0:
        conn.close()
        return {"total_scans": 0}

    latest = conn.execute(
        """
        SELECT compliance_score, total_checks, passed, failed, timestamp
        FROM   scans
        ORDER  BY id DESC LIMIT 1
        """
    ).fetchone()

    worst_checks = conn.execute(
        """
        SELECT check_id, check_name, severity, COUNT(*) as fail_count
        FROM   findings
        WHERE  passed = 0
        GROUP  BY check_id
        ORDER  BY fail_count DESC
        LIMIT  5
        """
    ).fetchall()

    conn.close()
    return {
        "total_scans":   total_scans,
        "latest_score":  latest["compliance_score"],
        "latest_total":  latest["total_checks"],
        "latest_passed": latest["passed"],
        "latest_failed": latest["failed"],
        "latest_ts":     latest["timestamp"],
        "top_failures":  [dict(r) for r in worst_checks],
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query scan history database")
    parser.add_argument("--summary",  action="store_true", help="Print summary stats")
    parser.add_argument("--history",  action="store_true", help="List all scan runs")
    parser.add_argument("--findings", action="store_true", help="List latest findings")
    args = parser.parse_args()

    if args.summary:
        s = get_summary()
        print(json.dumps(s, indent=2))
    elif args.history:
        print(json.dumps(get_history(), indent=2))
    elif args.findings:
        print(json.dumps(get_latest_findings(), indent=2))
    else:
        parser.print_help()
