<div align="center">
  <h1 align="center">🛡️ IaC Compliance Scanner</h1>
  <p align="center"><strong>The Ultimate Automated Infrastructure-as-Code Security Auditing Tool</strong></p>
  <p align="center">Scan, Aggregate, and Visualize your cloud security posture in seconds.</p>

  <p align="center">
    <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build Status">
    <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python Version">
    <img src="https://img.shields.io/badge/terraform-compatible-lightgrey" alt="Terraform">
    <img src="https://img.shields.io/badge/security-hardened-orange" alt="Security">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </p>

  <p align="center">
    <a href="#🚀-quick-start-the-noob-guide">🚀 Quick Start</a> • 
    <a href="#💡-key-features">💡 Features</a> • 
    <a href="#⚙️-how-it-works">⚙️ Workflow</a> • 
    <a href="#🛠️-custom-policies">📖 Custom Rules</a>
  </p>
</div>

---

## 🌟 Overview

The **IaC Compliance Scanner** is a professional dual-engine security tool that combines the power of [Checkov](https://github.com/bridgecrewio/checkov) and [tfsec](https://github.com/aquasecurity/tfsec). It doesn't just find vulnerabilities; it tracks your compliance history in a local SQLite database and generates a high-fidelity dashboard to visualize your security trends.

| Component | Role | Benefit |
| :--- | :--- | :--- |
| 🧠 **Dual Engines** | Checkov + tfsec | 2x the detection coverage |
| 🗄️ **History DB** | SQLite Aggregation | Track security score over time |
| 📊 **Dashboard** | HTML5 + Chart.js | Stunning visual compliance reports |
| 🛡️ **Custom Rules** | Python-based Policies | Business-specific security logic |

---

## 💡 Key Features

*   ✅ **Multi-Engine Scanning** - Seamless integration of two industry-standard scanners.
*   ✅ **Trend Analytics** - Historical data tracking to monitor your security progress.
*   ✅ **Deep Customization** - Easily add your own Python-based security policies.
*   ✅ **Zero Config** - Get up and running in minutes with sane defaults.
*   ✅ **Local First** - All data stays on your machine in a lightweight SQLite database.

---

## ⚙️ How It Works

```text
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│ Terraform Code │ ───→ │  Scan Engines  │ ───→ │ JSON Findings  │
└────────────────┘      └──────┬─────────┘      └──────┬─────────┘
                               │                       │
                               ▼                       ▼
                        ┌──────────────┐        ┌──────────────┐
                        │ Custom Rules │        │ History DB   │
                        └──────────────┘        └──────┬───────┘
                                                       │
                                                       ▼
                                               ┌───────────────┐
                                               │ HTML Dashboard│
                                               └───────────────┘
```

---

## 🚀 Quick Start (The "Noob" Guide)

Follow these steps exactly to get the scanner running on your machine.

### 1. Prerequisites
*   **Python:** Install [Python 3.9+](https://www.python.org/downloads/). (Check with `python --version`)
*   **Git:** Install [Git](https://git-scm.com/downloads).

### 2. Installation
Open your terminal (Command Prompt or PowerShell on Windows) and run:

```bash
# Clone the repository
git clone https://github.com/momonigithub/iac-compliance-scanner.git
cd iac-compliance-scanner

# Install the required Python packages
pip install -r requirements.txt
```

### 3. Setup Scanning Tools
*   **Checkov:** Installed automatically via `pip`.
*   **tfsec:** 
    *   **Windows:** [Download tfsec.exe](https://github.com/aquasecurity/tfsec/releases/latest/download/tfsec-windows-amd64.exe) and place it in the project root folder.
    *   **Linux/Mac:** `brew install tfsec` or `curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash`

### 4. Running your first Scan
Perform the scan and generate the report with two simple commands:

```powershell
# 1. Run the scan (Scans terraform/secure and terraform/insecure)
python scanner/scan.py

# 2. Generate the visual dashboard
python scanner/report.py
```

### 5. View the Results
Go to the `reports/` folder and open the latest `.html` file in your favorite browser.

---

## 🛠️ Custom Policies

Extend the scanner with your own logic in `policies/custom_policies/`:
*   **Tag Enforcement:** Ensure every resource has mandatory Environment/Owner tags.
*   **Encryption Check:** Verify S3 buckets have mandatory SSE-S3 or SSE-KMS enabled.

---

## 📂 Project Structure

```text
.
├── db/                   # SQLite database (scan history)
├── policies/
│   └── custom_policies/  # Your custom Python security rules
├── reports/              # HTML dashboards and raw JSON results
├── scanner/
│   ├── scan.py           # Core scanner logic
│   ├── aggregate.py      # Database aggregator
│   └── report.py         # Dashboard generator
├── terraform/            # Sample scan targets (secure/insecure)
└── Makefile              # Task automation
```

---

## ❓ Troubleshooting

*   **"Command not found" for python?** Use `python3` instead.
*   **No passed checks?** Ensure `terraform/secure/` is populated correctly.
*   **Empty Dashboard?** Run `scan.py` before `report.py`.

---

<div align="center">
  <p>Distributed under the MIT License.</p>
  <p><i>Made with ❤️ for Cloud Security Engineers.</i></p>
</div>
