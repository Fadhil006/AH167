# Configuration file template
# INSTRUCTIONS: Copy this to config.py and add your actual Gemini API key

# ============================================================================
# Gemini API Configuration
# ============================================================================
GEMINI_API_KEY = "YOUR_API_KEY_HERE"  # Get from: https://makersuite.google.com/app/apikey

# ============================================================================
# LLM Settings
# ============================================================================
LLM_MODEL = "gemini-2.5-pro"  # Pro model for highest accuracy
LLM_TEMPERATURE = 0.1  # Lower (0.0-0.3) for more consistent analysis, higher for creativity
LLM_MAX_TOKENS = 500  # Reduced for faster responses

# ============================================================================
# Anomaly Detection Thresholds
# ============================================================================
RARE_PATTERN_THRESHOLD = 2  # Patterns appearing <= this many times are considered rare
FREQUENCY_THRESHOLD = 0.05  # Patterns below 5% frequency are flagged as potential anomalies

# ============================================================================
# Pipeline Control (Enable/Disable LLM Features)
# ============================================================================
# SPEED MODE: Minimal API calls for fast results
ENABLE_PRE_CLUSTERING = False  # Disabled - saves time
ENABLE_POST_CLUSTERING = True  # Only most important feature enabled
ENABLE_REAL_TIME_CLASSIFICATION = False  # Disabled - saves time
ENABLE_SEMANTIC_MERGING = False  # Disabled - saves time
ENABLE_ANOMALY_EXPLANATION = False  # Disabled - saves time

# ============================================================================
# Performance Tuning (SPEED MODE - Fast results)
# ============================================================================
MAX_CLUSTERS_TO_REFINE = 2  # Only top 2 most important clusters (FAST)
MAX_CLUSTERS_FOR_MERGING = 5  # Minimal (not used if disabled)
MAX_ANOMALIES_TO_EXPLAIN = 1  # Minimal (not used if disabled)
SAMPLE_LOGS_FOR_PREPROCESSING = 10  # Reduced sample size
