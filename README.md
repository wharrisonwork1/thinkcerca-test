# 🧠 ThinkCERCA ELA Automation Toolkit

Automates the **ELA Standards Mapping & InDesign Publishing Workflow** for ThinkCERCA student guides.  
This toolkit extracts standards, aligns them with AI, and generates annotated InDesign layouts — all in one automated pipeline.

---

## 🚀 Overview

This tool performs a complete **data-to-design pipeline**:

| Step | Module | Description |
|------|---------|-------------|
| 1️⃣ | `standards_loader.py` | Reads the *Core National Scope and Sequence* Excel to extract module-specific standards for the target grade/unit/module. |
| 2️⃣ | `standards_descriptions.py` | Loads the full CCSS Grade 8 standards descriptions (code + text). |
| 3️⃣ | `join_standards.py` | Merges and normalizes standards with their descriptions. |
| 4️⃣ | `ai_matcher.py` | Uses OpenAI to semantically match Student Guide activities (from PDF) with standards. Produces an Excel summary file. |
| 5️⃣ | `indesign_bridge.py` | Converts Excel output → CSV → JSX script, then automates Adobe InDesign to label each page and export a finalized PDF. |

---

## ⚙️ Setup

### 1️⃣ Prerequisites
- macOS (required for AppleScript → InDesign bridge)
- **Adobe InDesign 2025+** installed (2026 has known scripting bugs — use 2025 for stability)
- **Python 3.11+**
- An OpenAI API key (for the AI matching step)
- Required fonts (e.g., “Minion Pro”) installed in InDesign

---

### 2️⃣ Install dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

- Duplicate .env.example → .env
- Add `AI-1-grade-8-student-guide-volume-1.indd` file in /data folder for indesign automation step
### Run
```bash
python main.py # Run full end-to-end pipeline
python main.py --ai #Include AI mapping before InDesign
python main.py --indesign-only # Skip standards extraction and AI — reuse latest Excel CSV to run InDesign automation only
```