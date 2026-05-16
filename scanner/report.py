#!/usr/bin/env python3
"""
report.py  —  HTML Dashboard Generator
"""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"

try:
    sys.path.insert(0, str(ROOT / "scanner"))
    from aggregate import get_history, get_latest_findings, get_summary
except ImportError:
    print("Error: Could not import aggregate.py. Ensure it is in the scanner/ directory.")
    sys.exit(1)

SEV_ORDER  = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
SEV_COLORS = {
    "CRITICAL": "#ff4d4d",
    "HIGH":     "#ff8c42",
    "MEDIUM":   "#f5c518",
    "LOW":      "#4db8ff",
    "UNKNOWN":  "#8888aa",
}

def sev_badge(sev: str) -> str:
    col = SEV_COLORS.get(sev.upper(), "#8888aa")
    return (
        f'<span class="badge" style="background:{col}22;color:{col};'
        f'border:1px solid {col}44">{sev}</span>'
    )

def build_findings_rows(findings: list[dict]) -> str:
    if not findings:
        return '<tr><td colspan="7" class="empty">No findings yet — run <code>python scanner/scan.py</code></td></tr>'

    failures = sorted(
        [f for f in findings if not f["passed"]],
        key=lambda x: (SEV_ORDER.get(x.get("severity", "").upper(), 99), x.get("module", "")),
    )

    rows = []
    for f in failures:
        sev   = (f.get("severity") or "UNKNOWN").upper()
        fname = Path(f.get("file", "")).name or "—"
        rows.append(
            f"<tr>"
            f"<td>{sev_badge(sev)}</td>"
            f"<td><span class='tool-tag tool-{f.get('tool','')}'>{f.get('tool','—')}</span></td>"
            f"<td class='mono'>{f.get('check_id','—')}</td>"
            f"<td>{f.get('check_name','—')[:80]}</td>"
            f"<td class='mono'>{f.get('module','—')}</td>"
            f"<td class='mono'>{fname}</td>"
            f"<td class='mono'>{f.get('resource','—')[:40]}</td>"
            f"</tr>"
        )
    return "\n".join(rows)

def score_color(score: float) -> str:
    if score >= 80:
        return "#39d98a"
    if score >= 50:
        return "#f5c518"
    return "#ff4d4d"

def build_sev_breakdown(findings: list[dict]) -> dict:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings:
        if not f["passed"]:
            sev = (f.get("severity") or "").upper()
            if sev in counts:
                counts[sev] += 1
    return counts

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>IaC Compliance Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg0:   #0b0d12;
    --bg1:   #111420;
    --bg2:   #171b28;
    --bg3:   #1e2435;
    --line:  #252d42;
    --text0: #e2e6f0;
    --text1: #8b95b0;
    --text2: #525c78;
    --green: #39d98a;
    --red:   #ff4d4d;
    --amber: #f5c518;
    --blue:  #4db8ff;
    --purple:#a78bfa;
    --accent:#39d98a;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg0);
    color: var(--text0);
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background-image:
      linear-gradient(var(--line) 1px, transparent 1px),
      linear-gradient(90deg, var(--line) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.3;
    pointer-events: none;
    z-index: 0;
  }
  .page { position: relative; z-index: 1; max-width: 1280px; margin: 0 auto; padding: 32px 24px 64px; }
  .header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 40px; gap: 16px; flex-wrap: wrap; }
  .eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--accent); letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 6px; }
  .header h1 { font-size: 28px; font-weight: 600; line-height: 1.1; letter-spacing: -0.5px; }
  .header h1 span { color: var(--accent); }
  .header-meta { font-size: 12px; color: var(--text1); margin-top: 6px; font-family: 'JetBrains Mono', monospace; }
  .generated-at { font-size: 11px; color: var(--text2); font-family: 'JetBrains Mono', monospace; text-align: right; }
  .score-ring-wrap { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; }
  .score-ring-container { position: relative; width: 88px; height: 88px; flex-shrink: 0; }
  .score-ring-container svg { transform: rotate(-90deg); }
  .score-ring-label {
    position: absolute; inset: 0;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
  }
  .score-ring-label .score-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 18px; font-weight: 600;
    line-height: 1;
  }
  .score-ring-label .score-pct {
    font-size: 10px; color: var(--text1);
    font-family: 'JetBrains Mono', monospace;
  }
  .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 28px; }
  .card {
    background: var(--bg2);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .card:hover { border-color: var(--bg3); }
  .card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent-line, var(--line));
    border-radius: 10px 10px 0 0;
  }
  .card-label { font-size: 11px; color: var(--text1); letter-spacing: 0.05em; text-transform: uppercase; font-weight: 500; margin-bottom: 8px; }
  .card-value { font-size: 32px; font-weight: 600; font-family: 'JetBrains Mono', monospace; line-height: 1; }
  .card-sub { font-size: 11px; color: var(--text2); margin-top: 5px; font-family: 'JetBrains Mono', monospace; }
  .sev-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px; }
  .sev-pill {
    display: flex; align-items: center; gap: 8px;
    background: var(--bg2); border: 1px solid var(--line);
    border-radius: 8px; padding: 8px 14px;
    font-size: 12px; font-family: 'JetBrains Mono', monospace;
  }
  .sev-dot { width: 8px; height: 8px; border-radius: 50%; }
  .sev-count { font-weight: 600; margin-left: 2px; }
  .charts { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 28px; }
  @media(max-width:720px){ .charts { grid-template-columns: 1fr; } }
  .chart-card {
    background: var(--bg2);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 20px;
  }
  .chart-title {
    font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text1); font-weight: 500; margin-bottom: 16px;
    font-family: 'JetBrains Mono', monospace;
  }
  .section-title {
    font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text1); font-weight: 500; margin-bottom: 12px;
    font-family: 'JetBrains Mono', monospace;
    display: flex; align-items: center; gap: 10px;
  }
  .section-title::after { content: ''; flex: 1; height: 1px; background: var(--line); }
  .table-wrap { background: var(--bg2); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; margin-bottom: 28px; }
  table { width: 100%; border-collapse: collapse; }
  thead { background: var(--bg3); }
  th {
    text-align: left; padding: 10px 14px;
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--text1); font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    border-bottom: 1px solid var(--line);
  }
  td { padding: 9px 14px; border-bottom: 1px solid var(--line); vertical-align: middle; font-size: 12px; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: var(--bg3); }
  .mono { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text1); }
  .empty { text-align: center; color: var(--text2); padding: 32px; font-family: 'JetBrains Mono', monospace; font-size: 12px; }
  code { font-family: 'JetBrains Mono', monospace; background: var(--bg3); padding: 1px 6px; border-radius: 4px; font-size: 11px; }
  .badge {
    display: inline-block; padding: 2px 8px;
    border-radius: 4px; font-size: 10px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.05em; text-transform: uppercase;
  }
  .tool-tag {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: 10px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace; text-transform: uppercase;
  }
  .tool-checkov { background: #a78bfa22; color: #a78bfa; border: 1px solid #a78bfa44; }
  .tool-tfsec   { background: #4db8ff22; color: #4db8ff; border: 1px solid #4db8ff44; }
  .footer { text-align: center; font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text2); margin-top: 40px; }
  .footer a { color: var(--text1); text-decoration: none; }
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div class="header-left">
      <div class="eyebrow">IaC Security · Compliance Report</div>
      <h1>Infrastructure <span>Compliance</span> Dashboard</h1>
      <div class="header-meta">Tools: Checkov · tfsec · Custom Policies</div>
    </div>
    <div class="generated-at">Generated<br>__GENERATED_AT__</div>
  </div>
  <div class="score-ring-wrap" style="margin-bottom:20px">
    <div class="score-ring-container">
      <svg width="88" height="88" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r="36" fill="none" stroke="#252d42" stroke-width="7"/>
        <circle cx="44" cy="44" r="36" fill="none"
          stroke="__SCORE_COLOR__" stroke-width="7"
          stroke-linecap="round"
          stroke-dasharray="__DASH_ARRAY__"
          stroke-dashoffset="0"/>
      </svg>
      <div class="score-ring-label">
        <span class="score-num" style="color:__SCORE_COLOR__">__SCORE__</span>
        <span class="score-pct">score</span>
      </div>
    </div>
    <div>
      <div style="font-size:13px;color:var(--text1);margin-bottom:4px">Overall compliance score</div>
      <div style="font-size:12px;color:var(--text2);font-family:'JetBrains Mono',monospace">Latest scan: __LATEST_TS__</div>
      <div style="font-size:12px;color:var(--text2);font-family:'JetBrains Mono',monospace">Total scans in history: __TOTAL_SCANS__</div>
    </div>
  </div>
  <div class="cards">
    <div class="card" style="--accent-line:#39d98a">
      <div class="card-label">Passed</div>
      <div class="card-value" style="color:#39d98a">__PASSED__</div>
      <div class="card-sub">checks</div>
    </div>
    <div class="card" style="--accent-line:#ff4d4d">
      <div class="card-label">Failed</div>
      <div class="card-value" style="color:#ff4d4d">__FAILED__</div>
      <div class="card-sub">checks</div>
    </div>
    <div class="card" style="--accent-line:#4db8ff">
      <div class="card-label">Total checks</div>
      <div class="card-value" style="color:#4db8ff">__TOTAL__</div>
      <div class="card-sub">this scan</div>
    </div>
    <div class="card" style="--accent-line:#a78bfa">
      <div class="card-label">Scan runs</div>
      <div class="card-value" style="color:#a78bfa">__TOTAL_SCANS__</div>
      <div class="card-sub">in history</div>
    </div>
  </div>
  <div class="sev-row">
    <div class="sev-pill">
      <span class="sev-dot" style="background:#ff4d4d"></span>
      <span>Critical</span><span class="sev-count" style="color:#ff4d4d">__CNT_CRITICAL__</span>
    </div>
    <div class="sev-pill">
      <span class="sev-dot" style="background:#ff8c42"></span>
      <span>High</span><span class="sev-count" style="color:#ff8c42">__CNT_HIGH__</span>
    </div>
    <div class="sev-pill">
      <span class="sev-dot" style="background:#f5c518"></span>
      <span>Medium</span><span class="sev-count" style="color:#f5c518">__CNT_MEDIUM__</span>
    </div>
    <div class="sev-pill">
      <span class="sev-dot" style="background:#4db8ff"></span>
      <span>Low</span><span class="sev-count" style="color:#4db8ff">__CNT_LOW__</span>
    </div>
  </div>
  <div class="charts">
    <div class="chart-card">
      <div class="chart-title">Compliance score trend</div>
      <div class="chart-wrap"><canvas id="trendChart" height="180"></canvas></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Failure severity distribution</div>
      <div class="chart-wrap"><canvas id="sevChart" height="180"></canvas></div>
    </div>
  </div>
  <div class="section-title">Failed checks (__FAILED__ findings)</div>
  <div class="table-wrap">
    <table id="findingsTable">
      <thead>
        <tr>
          <th>Severity</th>
          <th>Tool</th>
          <th>Check ID</th>
          <th>Finding</th>
          <th>Module</th>
          <th>File</th>
          <th>Resource</th>
        </tr>
      </thead>
      <tbody id="tbody">
__TABLE_ROWS__
      </tbody>
    </table>
  </div>
  <div class="footer">
    IaC Compliance Scanner · <a href="https://github.com/bridgecrewio/checkov">Checkov</a> ·
    <a href="https://github.com/aquasecurity/tfsec">tfsec</a>
  </div>
</div>
<script>
const historyData = __HISTORY_JSON__;
const sevData     = __SEV_JSON__;
const trendCtx = document.getElementById('trendChart').getContext('2d');
const labels   = historyData.map(d => {
  const dt = new Date(d.timestamp);
  return dt.toLocaleDateString('en-GB', { day:'2-digit', month:'short' }) + ' ' + dt.toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit' });
});
const scores = historyData.map(d => d.compliance_score);
new Chart(trendCtx, {
  type: 'line',
  data: {
    labels,
    datasets: [{
      label: 'Compliance %',
      data: scores,
      borderColor: '#39d98a',
      backgroundColor: 'rgba(57,217,138,0.08)',
      borderWidth: 2,
      pointBackgroundColor: '#39d98a',
      pointRadius: 4,
      fill: true,
      tension: 0.35,
    }]
  },
  options: {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { ticks: { color:'#525c78', font:{size:10, family:"'JetBrains Mono', monospace"} }, grid:{color:'#252d42'} },
      y: { min:0, max:100, ticks:{ color:'#525c78', font:{size:10}, callback: v => v+'%' }, grid:{color:'#252d42'} }
    }
  }
});
const sevCtx = document.getElementById('sevChart').getContext('2d');
new Chart(sevCtx, {
  type: 'doughnut',
  data: {
    labels: ['Critical','High','Medium','Low'],
    datasets: [{
      data: [sevData.CRITICAL||0, sevData.HIGH||0, sevData.MEDIUM||0, sevData.LOW||0],
      backgroundColor: ['#ff4d4d','#ff8c42','#f5c518','#4db8ff'],
      borderColor: '#111420',
      borderWidth: 3,
      hoverOffset: 8,
    }]
  },
  options: {
    responsive: true,
    cutout: '70%',
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color:'#8b95b0', font:{size:11, family:"'JetBrains Mono', monospace"}, padding:12 }
      }
    }
  }
});
</script>
</body>
</html>
"""

def build_report(output_path: Path | None = None) -> Path:
    history  = get_history(limit=30)
    findings = get_latest_findings(limit_scans=1)
    summary  = get_summary()

    if not history:
        print("  ⚠ No scan history found. Run `python scanner/scan.py` first.")
        history = [{
            "timestamp": datetime.utcnow().isoformat(),
            "total_checks": 0, "passed": 0, "failed": 0, "compliance_score": 0,
        }]

    latest       = history[-1]
    score        = latest["compliance_score"]
    sev_counts   = build_sev_breakdown(findings)
    circumference = 2 * 3.14159 * 36
    dash_array   = f"{circumference * score / 100:.1f} {circumference:.1f}"

    now_str      = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    latest_ts    = latest["timestamp"][:16].replace("T", " ")
    s_col        = score_color(score)

    html = HTML_TEMPLATE
    replacements = {
        "__GENERATED_AT__":  now_str,
        "__SCORE__":         f"{score:.0f}%",
        "__SCORE_COLOR__":   s_col,
        "__DASH_ARRAY__":    dash_array,
        "__LATEST_TS__":     latest_ts,
        "__TOTAL_SCANS__":   str(summary.get("total_scans", len(history))),
        "__PASSED__":        str(latest.get("passed", 0)),
        "__FAILED__":        str(latest.get("failed", 0)),
        "__TOTAL__":         str(latest.get("total_checks", 0)),
        "__CNT_CRITICAL__":  str(sev_counts.get("CRITICAL", 0)),
        "__CNT_HIGH__":      str(sev_counts.get("HIGH", 0)),
        "__CNT_MEDIUM__":    str(sev_counts.get("MEDIUM", 0)),
        "__CNT_LOW__":       str(sev_counts.get("LOW", 0)),
        "__TABLE_ROWS__":    build_findings_rows(findings),
        "__HISTORY_JSON__":  json.dumps(history),
        "__SEV_JSON__":      json.dumps(sev_counts),
    }

    for k, v in replacements.items():
        html = html.replace(k, v)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if output_path is None:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = REPORTS_DIR / f"dashboard_{ts}.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"  ✓ Dashboard → {output_path}")
    return output_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate HTML compliance dashboard")
    parser.add_argument("--output", type=str, default=None, help="Custom output path")
    args = parser.parse_args()
    build_report(Path(args.output) if args.output else None)
