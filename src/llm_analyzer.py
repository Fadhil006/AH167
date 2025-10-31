import google.generativeai as genai
from src.config import GEMINI_API_KEY, LLM_MODEL, LLM_TEMPERATURE

class LLMLogAnalyzer:
    
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(LLM_MODEL)
    
    def analyze_rare_patterns(self, rare_patterns, total_lines):
        """Analyze rare log patterns to identify potential anomalies"""
        
        prompt = f"""Analyze these rare log patterns. Be CONCISE (2-3 sentences per pattern max).

Total lines: {total_lines}

Patterns:
"""
        for pattern in rare_patterns[:5]:  # Only top 5
            prompt += f"\n- Count: {pattern['count']}, Template: {pattern['template']}"
        
        prompt += """

For each critical pattern only, provide:
- Severity (INFO/WARNING/ERROR/CRITICAL)
- Issue (1 sentence)
- Action (1 sentence)

Skip INFO patterns. Be brief."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error analyzing patterns: {str(e)}"
    
    def classify_new_pattern(self, log_line, template):
        """Classify a new pattern detected by Drain3"""
        
        prompt = f"""Classify in 1 line each:

Log: {log_line}
Template: {template}

Category: <Auth/DB/Network/System/App>
Severity: <INFO/WARN/ERROR/CRITICAL>
Status: <Normal/Anomaly>
Why: <1 sentence>"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error classifying pattern: {str(e)}"
    
    def suggest_pattern_refinement(self, template, examples):
        """Suggest improvements to pattern extraction"""
        
        prompt = f"""Template: {template}

Examples:
"""
        for ex in examples[:3]:  # Only 3 examples
            prompt += f"\n- {ex}"
        
        prompt += """

Correct? Suggest improvements (1-2 sentences max)."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error suggesting refinement: {str(e)}"
    
    def refine_cluster_template(self, template, sample_logs, cluster_id):
        """Post-clustering: Refine and generalize Drain3 templates using LLM"""
        
        prompt = f"""Refine this log pattern. Be CONCISE.

Cluster: {cluster_id}
Template: {template}

Samples:
"""
        for log in sample_logs[:3]:  # Only 3 samples
            prompt += f"\n- {log}"
        
        prompt += """

Provide (keep each to 1 line max):
Refined Template: <better template>
Label: <short descriptive name>
Severity: <INFO/WARNING/ERROR/CRITICAL>
Merge With: <cluster IDs or None>
Explanation: <1 sentence only>"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error refining template: {str(e)}"
    
    def suggest_preprocessing_rules(self, sample_logs):
        """Pre-clustering: Analyze logs to suggest tokenization/masking rules"""
        
        prompt = f"""Suggest preprocessing rules. Be CONCISE (max 10 lines total).

Sample Logs:
"""
        for log in sample_logs[:10]:  # Only 10 samples
            prompt += f"\n- {log}"
        
        prompt += """

List only:
1. Top 5 regex masks (format: pattern -> replacement)
2. Key normalization rules (1 sentence each max)

Be brief."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error suggesting preprocessing: {str(e)}"
    
    def explain_anomaly(self, log_line, template, context=None):
        """Real-time: Explain anomalous logs in natural language"""
        
        prompt = f"""Explain this anomalous log entry in natural language for a developer.

Log Entry: {log_line}
Template: {template}
"""
        if context:
            prompt += f"Context: {context}\n"
        
        prompt += """

Provide (1 sentence each max):
1. What: <what happened>
2. Cause: <likely root cause>
3. Action: <immediate fix>
4. Check: <related systems>

Be concise."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error explaining anomaly: {str(e)}"
    
    def merge_similar_clusters(self, cluster_templates):
        """Identify clusters that should be merged based on semantic similarity"""
        
        prompt = f"""Find templates that mean the same thing. Be CONCISE.

Templates:
"""
        for i, (cid, template) in enumerate(cluster_templates[:10], 1):  # Only top 10
            prompt += f"\n{i}. [{cid}] {template}"
        
        prompt += """

List merge groups (1 line each):
Group 1: [IDs] - <1 word reason>
Group 2: [IDs] - <1 word reason>

Only list if truly equivalent."""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                )
            )
            return response.text
        except Exception as e:
            return f"Error merging clusters: {str(e)}"
