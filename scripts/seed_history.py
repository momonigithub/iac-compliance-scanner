#!/usr/bin/env python3
"""
seed_history.py  —  Demo History Seeder
"""

import sys
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scanner"))
from aggregate import update_history

CHECKS = [
    ("CKV_AWS_18",  "Ensure the S3 bucket has access logging enabled",           "HIGH",     "aws_s3_bucket",     "s3.tf"),
    ("CKV_AWS_19",  "Ensure all data stored in S3 is securely encrypted",        "CRITICAL",  "aws_s3_bucket",     "s3.tf"),
    ("CKV_AWS_53",  "Ensure S3 bucket has block public ACLs enabled",            "HIGH",     "aws_s3_bucket",     "s3.tf"),
    ("CKV_AWS_57",  "Ensure S3 bucket is not publicly readable via ACL",         "CRITICAL",  "aws_s3_bucket",     "s3.tf"),
    ("CKV_AWS_23",  "Ensure security group has description",                     "MEDIUM",   "aws_security_group","security_groups.tf"),
    ("CKV_AWS_25",  "Ensure no security group allows ingress from 0.0.0.0/0 on 22", "CRITICAL","aws_security_group","security_groups.tf"),
    ("CKV_AWS_26",  "Ensure no security group allows ingress from 0.0.0.0/0 on 3389","HIGH",  "aws_security_group","security_groups.tf"),
    ("CKV_AWS_8",   "Ensure IMDSv2 is required for EC2 instances",              "HIGH",     "aws_instance",      "iam_rds_ec2.tf"),
    ("CKV_AWS_116", "Ensure RDS database has deletion protection enabled",       "MEDIUM",   "aws_db_instance",   "iam_rds_ec2.tf"),
    ("CKV_AWS_17",  "Ensure RDS is not publicly accessible",                     "HIGH",     "aws_db_instance",   "iam_rds_ec2.tf"),
    ("CKV_AWS_16",  "Ensure RDS database is encrypted at rest",                  "HIGH",     "aws_db_instance",   "iam_rds_ec2.tf"),
    ("CKV_CUSTOM_1","Ensure all AWS resources have required tags",               "MEDIUM",   "aws_instance",      "iam_rds_ec2.tf"),
    ("CKV_CUSTOM_2","Ensure S3 bucket enforces HTTPS-only access",              "MEDIUM",   "aws_s3_bucket",     "s3.tf"),
    ("aws-iam-no-policy-wildcards", "IAM policy should not have wildcards",     "CRITICAL",  "aws_iam_role_policy","iam_rds_ec2.tf"),
    ("aws-rds-no-public-db-access", "RDS should not be publicly accessible",    "HIGH",     "aws_db_instance",   "iam_rds_ec2.tf"),
]

TOTAL_PASSING = 12

def make_scan(offset_days: float, fail_subset_size: int) -> dict:
    ts = (datetime.now(timezone.utc) - timedelta(days=offset_days)).isoformat()
    failing = random.sample(CHECKS, min(fail_subset_size, len(CHECKS)))
    findings = []
    for check_id, name, sev, resource, fname in CHECKS:
        failed = any(c[0] == check_id for c in failing)
        findings.append({
            "tool":       "checkov" if check_id.startswith("CKV") else "tfsec",
            "check_id":   check_id,
            "check_name": name,
            "severity":   sev,
            "passed":     not failed,
            "resource":   resource,
            "file":       f"terraform/insecure/{fname}",
            "line_start": random.randint(10, 60),
            "line_end":   random.randint(61, 90),
            "module":     "insecure",
            "guideline":  "",
        })
    for i in range(TOTAL_PASSING):
        findings.append({
            "tool": "checkov", "check_id": f"CKV_AWS_{100+i}",
            "check_name": f"Secure check #{i+1}", "severity": "MEDIUM",
            "passed": True, "resource": "aws_s3_bucket",
            "file": "terraform/secure/main.tf",
            "line_start": 10, "line_end": 20, "module": "secure", "guideline": "",
        })
    total   = len(findings)
    passed  = sum(1 for f in findings if f["passed"])
    failed  = total - passed
    score   = round(passed / total * 100, 1) if total else 100.0
    return {
        "timestamp":        ts,
        "total_checks":     total,
        "passed":           passed,
        "failed":           failed,
        "compliance_score": score,
        "findings":         findings,
        "scanned_dirs":     ["terraform/insecure", "terraform/secure"],
    }

def seed():
    schedule = [
        (14.0, 13),  (12.8, 12),  (11.5, 11),  (10.3, 11),
        (9.0,  10),  (7.7,  10),  (6.5,   9),  (5.4,   9),
        (4.2,   8),  (3.1,   7),  (2.3,   7),  (1.5,   6),
        (0.9,   5),  (0.4,   4),  (0.1,   3),
    ]
    print(f"  Seeding {len(schedule)} historical scan runs …")
    for i, (days_ago, fail_count) in enumerate(schedule, 1):
        result = make_scan(days_ago, fail_count)
        scan_id = update_history(result)
        print(f"    [{i:2d}/{len(schedule)}] score={result['compliance_score']:5.1f}%  "
              f"failed={result['failed']:2d}  scan_id={scan_id}")
    print("\n  ✓ Seed complete.")

if __name__ == "__main__":
    seed()
