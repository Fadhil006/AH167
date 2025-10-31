# DLT Log Analysis Guide

## What is DLT?

**DLT (Diagnostic Log and Trace)** is an automotive logging protocol used in ECUs (Electronic Control Units) for vehicle diagnostics.

## DLT Log Format

Your system now supports DLT logs with these columns:

1. **Timestamp** - Date and time of log entry
2. **Index** - Sequential log ID
3. **ECU** - Electronic Control Unit name (e.g., ECU1, ECU2)
4. **Application ID** - Application identifier (e.g., APP_ENGINE, APP_BRAKE)
5. **Log Message** - The actual log message text

## How to Use

### 1. Prepare Your DLT Log File

Format your DLT logs as a CSV file:

```csv
Timestamp,Index,ECU,Application ID,Log Message
2025-10-31 10:00:01.234,1,ECU1,APP_ENGINE,Engine started successfully
2025-10-31 10:00:02.456,2,ECU1,APP_ENGINE,Engine RPM: 800
...
```

Save it as `data/dlt_logs.csv`

### 2. Run DLT Parser

```bash
# With LLM analysis (recommended for evaluation)
python -m src.custom.dlt_parser

# Or specify custom file in src/custom/dlt_parser.py:
# DLT_LOG_FILE = PROJECT_ROOT / "data" / "your_file.csv"
```

### 3. Check Output

Results will be saved to:
- **JSON:** `other/dlt_structured_logs.json`
- **State:** `other/dlt_drain3_state.bin`

## What You Get

### DLT-Specific Analysis

1. **Pattern Templates** - Drain3 clusters similar messages
2. **ECU Mapping** - Which ECUs produce which patterns
3. **App ID Mapping** - Which applications generate which logs
4. **Frequency Analysis** - Common vs rare patterns
5. **LLM Refinement** - Semantic labels and explanations

### Example Output

```
Frequent Patterns (5 patterns):

  [C  1] Count:    8 (26.7%)
       Template: Engine RPM: <*>
       ECUs: ECU1
       Apps: APP_ENGINE

Rare Patterns (12 patterns):

  [C 13] Count:    1 (3.3%)
       Template: CRITICAL: Engine overheat protection activated
       ECUs: ECU1
       Apps: APP_ENGINE
```

## For LogHub Datasets

To support BGL, HDFS, or Thunderbird datasets from [LogHub-2.0](https://github.com/logpai/loghub-2.0):

### Option 1: Use Enhanced Parser (Generic)

```bash
# For any text-based log format
python -m src.custom.enhanced_parser

# Edit LOG_FILE_PATH in enhanced_parser.py (line 17)
LOG_FILE_PATH = PROJECT_ROOT / "data" / "BGL.log"
```

### Option 2: Create Custom Parser

Similar to `dlt_parser.py`, create parsers for:
- **BGL**: Blue Gene/L supercomputer logs
- **HDFS**: Hadoop Distributed File System logs  
- **Thunderbird**: Thunderbird supercomputer logs

## Adapting for Different Formats

### BGL Format
```python
# BGL has: Label, Timestamp, Date, Node, Content
# Extract 'Content' column for analysis
```

### HDFS Format
```python
# HDFS has: Date, Time, Pid, Level, Component, Content
# Extract 'Content' for clustering
```

### Thunderbird Format
```python
# Thunderbird has: Label, Timestamp, Date, User, Month, Day, Time, Location, Content
# Extract 'Content' for analysis
```

## Current Configuration

Your system is optimized for evaluation:
- **Model:** gemini-2.5-pro (highest accuracy)
- **API calls:** ~2 per run (top 2 clusters)
- **Output:** Concise explanations
- **Speed:** 15-30 seconds per run

## Quick Commands

```bash
# DLT logs (automotive)
python -m src.custom.dlt_parser

# Generic logs (LogHub datasets)
python -m src.custom.enhanced_parser

# Fast Drain3 only (no LLM)
python -m src.custom.parser
```

## For Evaluation

### What to Demonstrate

1. **DLT Support** ✅
   - Show ECU-specific pattern analysis
   - Demonstrate application ID grouping
   - Highlight automotive-specific insights

2. **Pattern Discovery** ✅
   - Drain3 clustering (fast, accurate)
   - LLM semantic labeling
   - Anomaly detection (CRITICAL/ERROR patterns)

3. **Real-World Value** ✅
   - ECU fault diagnosis
   - Application behavior analysis
   - Proactive maintenance alerts

### Sample Questions to Answer

1. Which ECU generates the most errors?
2. What are the critical patterns across all applications?
3. Which patterns indicate system degradation?

## Files Structure

```
LogSage/
├── src/custom/
│   ├── dlt_parser.py        # NEW: DLT format parser
│   ├── enhanced_parser.py   # Generic log parser
│   ├── parser.py            # Basic Drain3 (fast)
│   ├── llm_analyzer.py      # LLM integration
│   └── config.py            # Configuration
├── data/
│   ├── dlt_logs.csv         # NEW: Sample DLT logs
│   └── logs.txt             # Generic logs
└── other/
    ├── dlt_structured_logs.json  # NEW: DLT output
    └── structured_logs.json      # Generic output
```

## Tips for Hackathon

1. **Use DLT parser for evaluation** - Shows you understand automotive standards
2. **Highlight ECU analysis** - Unique to DLT format
3. **Show LLM value** - Semantic labels make patterns understandable
4. **Demo both modes** - Fast (Drain3 only) vs Accurate (with LLM)

## Need Help?

- Check `CURRENT_CONFIG.md` for settings
- See `HACKATHON_MODE.md` for optimization tips
- Read `QUICK_START.md` for basic usage

Good luck with your evaluation! 🚀
