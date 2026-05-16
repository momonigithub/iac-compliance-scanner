#!/usr/bin/env python3
"""
scan.py  —  IaC Compliance Scanner
Runs Checkov and tfsec on one or more Terraform directories,
captures structured JSON output, and hands results to aggregate.py.
"""

import argparse
import json
import subprocess
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POLICIES_DIR = ROOT / "policies" / "custom_policies"
DB_DIR       = ROOT / "db"
REPORTS_DIR  = ROOT / "reports"


def _tool_available(name: str) -> bool:
    return shutil.which(name) is not None


def _run(cmd: list[str], label: str) -> dict:
    print(f"  ▶ {label} …", flush=True)
    try:
        # Windows compatibility: append .cmd or .exe if needed, but subprocess usually handles it if shell=False and executable is in PATH
        # checkov and tfsec might need shell=True on Windows if they are .cmd files
        is_windows = sys.platform == "win32"
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            shell=is_windows # Enable shell on Windows to find .cmd files like checkov
        )
        raw = result.stdout.strip()
        if not raw:
            print(f"    ✗ {label} produced no output (stderr: {result.stderr[:200]})")
            return {"error": result.stderr[:500], "raw": ""}
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    ✗ JSON parse error from {label}: {e}")
        return {"error": str(e), "raw": result.stdout[:500]}
    except subprocess.TimeoutExpired:
        print(f"    ✗ {label} timed out")
        return {"error": "timeout"}
    except Exception as e:
        print(f"    ✗ {label} failed: {e}")
        return {"error": str(e)}


def run_checkov(tf_dir: Path) -> dict:
    if not _tool_available("checkov"):
        print("  ⚠ checkov not found — skipping (run: pip install checkov)")
        return {"skipped": True}

    cmd = [
        "checkov",
        "--directory", str(tf_dir),
        "--output", "json",
        "--external-checks-dir", str(POLICIES_DIR),
    ]
    return _run(cmd, f"Checkov → {tf_dir.name}")


def run_tfsec(tf_dir: Path) -> dict:
    if not _tool_available("tfsec"):
        print("  ⚠ tfsec not found — skipping (run: scripts/install_tfsec.sh)")
        return {"skipped": True}

    cmd = [
        "tfsec",
        str(tf_dir),
        "--format", "json",
        "--no-color",
        "--include-ignored",
    ]
    return _run(cmd, f"tfsec    → {tf_dir.name}")


def normalize_checkov(raw: dict, tf_dir: Path) -> list[dict]:
    if raw.get("skipped") or raw.get("error"):
        return []

    findings = []
    summaries = raw if isinstance(raw, list) else [raw]

    for summary in summaries:
        results = summary.get("results", {})
        for status in ("failed_checks", "passed_checks"):
            passed = status == "passed_checks"
            for check in results.get(status, []):
                findings.append({
                    "tool":       "checkov",
                    "check_id":   check.get("check_id", ""),
                    "check_name": check.get("check_name", ""),
                    "severity":   _checkov_severity(check.get("check_id", "")),
                    "passed":     passed,
                    "resource":   check.get("resource", ""),
                    "file":       check.get("repo_file_path",
                                   check.get("file_path", "")),
                    "line_start": check.get("file_line_range", [0, 0])[0],
                    "line_end":   check.get("file_line_range", [0, 0])[-1],
                    "module":     tf_dir.name,
                    "guideline":  check.get("guideline", ""),
                })

    return findings


def normalize_tfsec(raw: dict, tf_dir: Path) -> list[dict]:
    if raw.get("skipped") or raw.get("error"):
        return []

    findings = []
    for result in raw.get("results", []):
        findings.append({
            "tool":       "tfsec",
            "check_id":   result.get("rule_id", ""),
            "check_name": result.get("description", ""),
            "severity":   result.get("severity", "MEDIUM").upper(),
            "passed":     False,
            "resource":   result.get("resource", ""),
            "file":       result.get("location", {}).get("filename", ""),
            "line_start": result.get("location", {}).get("start_line", 0),
            "line_end":   result.get("location", {}).get("end_line", 0),
            "module":     tf_dir.name,
            "guideline":  result.get("links", [""])[0] if result.get("links") else "",
        })

    return findings


def _checkov_severity(check_id: str) -> str:
    critical = {"CKV_AWS_18", "CKV_AWS_19", "CKV_AWS_53", "CKV_AWS_54",
                "CKV_AWS_55", "CKV_AWS_56", "CKV_AWS_57", "CKV_AWS_70"}
    high     = {"CKV_AWS_8",  "CKV_AWS_23", "CKV_AWS_25", "CKV_AWS_26",
                "CKV_AWS_27", "CKV_AWS_28", "CKV_AWS_116"}
    if check_id in critical:
        return "CRITICAL"
    if check_id in high:
        return "HIGH"
    return "MEDIUM"


def scan(tf_dirs: list[Path]) -> dict:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    all_findings: list[dict] = []

    for tf_dir in tf_dirs:
        if not tf_dir.is_dir():
            print(f"  ✗ Directory not found: {tf_dir}")
            continue

        print(f"\n{'─'*50}")
        try:
            print(f"  Scanning: {tf_dir.relative_to(ROOT)}")
        except ValueError:
            print(f"  Scanning: {tf_dir}")
        print(f"{'─'*50}")

        ck_raw  = run_checkov(tf_dir)
        tf_raw  = run_tfsec(tf_dir)

        all_findings.extend(normalize_checkov(ck_raw, tf_dir))
        all_findings.extend(normalize_tfsec(tf_raw, tf_dir))

    passed  = [f for f in all_findings if f["passed"]]
    failed  = [f for f in all_findings if not f["passed"]]
    total   = len(all_findings)
    score   = round((len(passed) / total * 100), 1) if total else 100.0

    scan_result = {
        "timestamp":       timestamp,
        "total_checks":    total,
        "passed":          len(passed),
        "failed":          len(failed),
        "compliance_score": score,
        "findings":        all_findings,
        "scanned_dirs":    [str(d) for d in tf_dirs],
    }

    raw_path = REPORTS_DIR / f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    raw_path.write_text(json.dumps(scan_result, indent=2))

    print(f"\n{'═'*50}")
    print(f"  SCAN COMPLETE")
    print(f"{'═'*50}")
    print(f"  Total checks : {total}")
    print(f"  Passed       : {len(passed)}  ✓")
    print(f"  Failed       : {len(failed)}  ✗")
    print(f"  Score        : {score}%")
    sev_counts = {}
    for f in failed:
        sev_counts[f["severity"]] = sev_counts.get(f["severity"], 0) + 1
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if sev_counts.get(sev):
            print(f"  {sev:<10}: {sev_counts[sev]} failures")
    try:
        print(f"\n  Raw results  → {raw_path.relative_to(ROOT)}")
    except ValueError:
        print(f"\n  Raw results  → {raw_path}")

    return scan_result


def main():
    parser = argparse.ArgumentParser(
        description="IaC Compliance Scanner — runs Checkov + tfsec locally"
    )
    parser.add_argument(
        "dirs",
        nargs="*",
        help="Terraform directories to scan (default: terraform/insecure terraform/secure)",
    )
    parser.add_argument(
        "--insecure-only", action="store_true",
        help="Scan only the intentionally misconfigured module"
    )
    args = parser.parse_args()

    if args.dirs:
        tf_dirs = [Path(d) for d in args.dirs]
    elif args.insecure_only:
        tf_dirs = [ROOT / "terraform" / "insecure"]
    else:
        tf_dirs = [
            ROOT / "terraform" / "insecure",
            ROOT / "terraform" / "secure",
        ]

    result = scan(tf_dirs)

    # Pass result path to aggregate.py automatically
    import sys
    sys.path.insert(0, str(ROOT / "scanner"))
    from aggregate import update_history
    update_history(result)

if __name__ == "__main__":
    main()
