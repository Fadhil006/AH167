# LogSage

Log analysis tool combining Drain3 clustering with LLM-based semantic understanding.

## Features

- Fast log pattern extraction using Drain3
- LLM-enhanced pattern refinement and anomaly detection
- Support for generic logs and automotive DLT format
- JSON export for structured output

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set your Gemini API key in `src/config.py`:

```python
GEMINI_API_KEY = "your-api-key-here"
```

## Usage

**Generic logs:**
```bash
python -m src.enhanced_parser
```

**DLT automotive logs:**
```bash
python -m src.dlt_parser
```

## Project Structure

```
LogSage/
├── src/
│   ├── config.py          # Configuration
│   ├── llm_analyzer.py    # LLM integration
│   ├── enhanced_parser.py # Generic parser
│   └── dlt_parser.py      # DLT parser
├── data/                  # Sample logs
└── other/                 # Output directory
```

## How It Works

Drain3 extracts log templates from raw logs, then the LLM refines patterns and adds semantic understanding. Output is saved as structured JSON.

## Requirements

- Python 3.8+
- drain3
- google-generativeai
