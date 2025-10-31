# LogSage 🔍

**Hybrid Log Analysis with Drain3 + LLM Enhancement**

LogSage combines fast symbolic clustering (Drain3) with semantic understanding (Gemini 2.5 Pro) to provide intelligent log analysis for generic logs and automotive DLT (Diagnostic Log and Trace) format.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

### Core Capabilities
- 🚀 **Fast Pattern Mining**: Drain3 for efficient log template extraction
- 🤖 **LLM Enhancement**: Gemini 2.5 Pro for semantic analysis
- 🚗 **DLT Support**: Full automotive diagnostic log format (Timestamp, Index, ECU, App ID, Message)
- 📊 **Structured Output**: JSON export with metadata
- ⚡ **Optimized Performance**: ~2 API calls per run, 15-30s execution

### LLM-Powered Analysis
1. Rare pattern detection with severity analysis
2. New pattern classification
3. Pattern refinement suggestions
4. Cluster template refinement with semantic labels
5. Preprocessing rule generation
6. Anomaly explanation
7. Similar cluster merging

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/LogSage.git
cd LogSage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Edit `src/custom/config.py` and set your Gemini API key:

```python
GEMINI_API_KEY = "your-api-key-here"
```

### Usage

#### Generic Log Analysis
```bash
# Edit log file path in src/custom/enhanced_parser.py (line 17)
python -m src.custom.enhanced_parser
```

#### DLT Automotive Log Analysis
```bash
# Place your DLT CSV file in data/dlt_logs.csv
python -m src.custom.dlt_parser
```

---

## 📁 Project Structure

```
LogSage/
├── src/
│   ├── custom/                 # Core implementation
│   │   ├── config.py          # Configuration & API keys
│   │   ├── llm_analyzer.py    # LLM integration (7 features)
│   │   ├── enhanced_parser.py # Generic log parser
│   │   └── dlt_parser.py      # DLT format parser
│   └── external/              # External libraries (Drain3)
├── data/
│   ├── logs.txt               # Sample generic logs
│   └── dlt_logs.csv          # Sample DLT automotive logs
├── other/                     # Output directory
│   ├── structured_logs.json  # Generic log results
│   └── dlt_structured_logs.json  # DLT results
└── requirements.txt           # Python dependencies
```

---

## 🚗 DLT Format Support

LogSage provides specialized support for automotive DLT logs with these columns:
- **Timestamp**: Date and time
- **Index**: Log ID
- **ECU**: Electronic Control Unit name
- **Application ID**: Application identifier
- **Log Message**: The actual log content

### DLT Features
- ✅ ECU-level pattern grouping
- ✅ Application ID tracking
- ✅ Automotive-aware LLM analysis
- ✅ Critical issue detection (engine overheat, brake failures)
- ✅ JSON export with ECU/App metadata

See [DLT_GUIDE.md](DLT_GUIDE.md) for detailed usage.

---

## 📊 Output Format

### Generic Logs
```json
{
  "total_lines": 43,
  "total_patterns": 15,
  "templates": [
    {
      "template": "User <*> logged in from <*>",
      "count": 8,
      "cluster_id": 2,
      "example_logs": ["User admin logged in from 192.168.1.1"]
    }
  ]
}
```

### DLT Logs
```json
{
  "total_lines": 30,
  "total_patterns": 21,
  "dlt_format": true,
  "templates": [
    {
      "template": "Engine RPM: <*>",
      "count": 4,
      "cluster_id": 2,
      "ecus": ["ECU1"],
      "app_ids": ["APP_ENGINE"],
      "example_logs": ["Engine RPM: 800"]
    }
  ]
}
```

---

## ⚙️ Configuration

Key settings in `src/custom/config.py`:

```python
# LLM Settings
LLM_MODEL = "gemini-2.5-pro"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 500

# Feature Toggles (optimize for speed)
ENABLE_PRE_CLUSTERING = False
ENABLE_POST_CLUSTERING = True
ENABLE_SEMANTIC_MERGING = False
ENABLE_ANOMALY_EXPLANATION = False

# Performance
MAX_CLUSTERS_TO_REFINE = 2
```

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)**: Step-by-step setup guide
- **[DLT_GUIDE.md](DLT_GUIDE.md)**: DLT format usage and examples
- **[EVALUATION_READY.md](EVALUATION_READY.md)**: Hackathon evaluation guide

---

## 🔬 How It Works

### Hybrid Architecture

```
Raw Logs → Drain3 Clustering → LLM Refinement → Structured Output
           (Fast, Symbolic)     (Semantic)        (JSON/CSV)
```

1. **Drain3 Clustering**: Efficiently extracts log templates (e.g., "User <*> logged in")
2. **LLM Enhancement**: Adds semantic labels, detects anomalies, refines patterns
3. **JSON Export**: Structured output ready for downstream analysis

### Why Hybrid?

- **Fast**: Drain3 processes thousands of logs in seconds
- **Intelligent**: LLM provides human-readable insights
- **Efficient**: Only 2 API calls per run (saves quota)
- **Accurate**: Best of symbolic + semantic approaches

---

## 🛠️ Requirements

- Python 3.8 or higher
- drain3 >= 0.9.0
- google-generativeai >= 0.4.0
- See [requirements.txt](requirements.txt) for full list

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## 🎯 Use Cases

- **DevOps**: Monitor application logs, detect anomalies
- **Security**: Identify suspicious patterns, track intrusions
- **Automotive**: Analyze ECU diagnostics, predict failures
- **Research**: LogHub-2.0 dataset analysis (BGL, HDFS, Thunderbird)

---

## 🏆 Hackathon Ready

This project is optimized for demonstrations:
- ⚡ Fast execution (15-30 seconds)
- 📊 Concise output (perfect for slides)
- 🚗 DLT format support (automotive evaluation)
- 🤖 LLM-powered insights (wow factor)

See [EVALUATION_READY.md](EVALUATION_READY.md) for demo tips!

---

**Built with ❤️ for intelligent log analysis**
