import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence
from drain3.template_miner_config import TemplateMinerConfig
from llm_analyzer import LLMLogAnalyzer
from config import RARE_PATTERN_THRESHOLD, FREQUENCY_THRESHOLD
import json

# log file path
PROJECT_ROOT = Path(__file__).parent.parent.parent
LOG_FILE_PATH = PROJECT_ROOT / "data" / "logs.txt"

class EnhancedLogParser:
    """Log parser with Drain3 + LLM-guided adaptive pattern extraction"""
    
    def __init__(self, use_llm=True):
        # Configure Drain3
        config = TemplateMinerConfig()
        config.profiling_enabled = False
        config.drain_sim_th = 0.5
        config.drain_depth = 4
        config.drain_max_children = 100
        
        # Set path for drain3 state file
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        state_file = project_root / "other" / "drain3_state.bin"
        persistence = FilePersistence(str(state_file))
        self.template_miner = TemplateMiner(persistence, config)
        
        # Initialize LLM analyzer
        self.use_llm = use_llm
        if use_llm:
            self.llm_analyzer = LLMLogAnalyzer()
        
        # Track metrics
        self.total_lines = 0
        self.new_patterns = []
        self.changed_patterns = []
        self.log_lines_by_cluster = {}
    
    def parse_logs(self, log_file):
        """Parse logs and extract structured templates"""
        
        print("=== Starting Log Parsing with Drain3 ===\n")
        
        with open(log_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                result = self.template_miner.add_log_message(line)
                self.total_lines += 1
                
                cluster_id = result["cluster_id"]
                
                # Store log lines by cluster for later analysis
                if cluster_id not in self.log_lines_by_cluster:
                    self.log_lines_by_cluster[cluster_id] = []
                self.log_lines_by_cluster[cluster_id].append(line)
                
                # Track new patterns (LLM can analyze these)
                if result["change_type"] == "cluster_created":
                    self.new_patterns.append({
                        "line": line,
                        "cluster_id": cluster_id,
                        "template": result["template_mined"]
                    })
                    if self.use_llm and len(self.new_patterns) <= 5:  # Analyze first 5 new patterns
                        print(f"[NEW PATTERN] {result['template_mined']}")
                        analysis = self.llm_analyzer.classify_new_pattern(line, result["template_mined"])
                        print(f"LLM Analysis:\n{analysis}\n")
                
                # Track changed patterns
                elif result["change_type"] == "cluster_template_changed":
                    self.changed_patterns.append({
                        "line": line,
                        "cluster_id": cluster_id,
                        "template": result["template_mined"]
                    })
        
        print(f"[COMPLETE] Parsed {self.total_lines} log lines\n")
    
    def post_clustering_enhancement(self):
        """Post-clustering: Use LLM to refine Drain3 templates"""
        
        if not self.use_llm:
            return {}
        
        print("\n" + "=" * 80)
        print("POST-CLUSTERING ENHANCEMENT (LLM Refinement)")
        print("=" * 80 + "\n")
        
        clusters_sorted = sorted(
            self.template_miner.drain.clusters,
            key=lambda x: x.size,
            reverse=True
        )
        
        refined_clusters = {}
        
        # Refine top clusters
        for i, cluster in enumerate(clusters_sorted[:5], 1):  # Refine top 5
            cluster_id = cluster.cluster_id
            template = cluster.get_template()
            sample_logs = self.log_lines_by_cluster.get(cluster_id, [])[:5]
            
            print(f"Refining Cluster {cluster_id} (Count: {cluster.size})...")
            refinement = self.llm_analyzer.refine_cluster_template(
                template, sample_logs, cluster_id
            )
            print(f"{refinement}\n")
            
            refined_clusters[cluster_id] = {
                "original_template": template,
                "refinement": refinement,
                "count": cluster.size
            }
        
        # Suggest cluster merging
        print("=" * 80)
        print("SEMANTIC CLUSTER MERGING")
        print("=" * 80 + "\n")
        
        cluster_templates = [(c.cluster_id, c.get_template()) for c in clusters_sorted[:15]]
        merge_suggestions = self.llm_analyzer.merge_similar_clusters(cluster_templates)
        print(merge_suggestions)
        
        return refined_clusters
    
    def analyze_patterns(self):
        """Analyze extracted patterns and identify anomalies"""
        
        clusters_sorted = sorted(
            self.template_miner.drain.clusters,
            key=lambda x: x.size,
            reverse=True
        )
        total_count = sum(cluster.size for cluster in clusters_sorted)
        
        # Separate frequent vs rare patterns
        frequent_patterns = []
        rare_patterns = []
        
        for cluster in clusters_sorted:
            pattern_info = {
                "template": cluster.get_template(),
                "count": cluster.size,
                "percentage": (cluster.size / total_count * 100),
                "cluster_id": cluster.cluster_id
            }
            
            if cluster.size <= RARE_PATTERN_THRESHOLD or pattern_info["percentage"] < FREQUENCY_THRESHOLD * 100:
                rare_patterns.append(pattern_info)
            else:
                frequent_patterns.append(pattern_info)
        
        # Display results
        print("=" * 80)
        print("DRAIN3 CLUSTERING RESULTS")
        print("=" * 80)
        
        print(f"\nFrequent Patterns (Normal Behavior - {len(frequent_patterns)} patterns):\n")
        for pattern in frequent_patterns[:10]:  # Show top 10
            print(f"  [C{pattern['cluster_id']:>3}] Count: {pattern['count']:>4} ({pattern['percentage']:>5.1f}%) | {pattern['template']}")
        
        print(f"\nRare Patterns (Potential Anomalies - {len(rare_patterns)} patterns):\n")
        for pattern in rare_patterns[:10]:
            print(f"  [C{pattern['cluster_id']:>3}] Count: {pattern['count']:>4} ({pattern['percentage']:>5.1f}%) | {pattern['template']}")
        
        print(f"\nStatistics:")
        print(f"  Total log lines: {self.total_lines}")
        print(f"  Total patterns: {len(clusters_sorted)}")
        print(f"  New patterns detected: {len(self.new_patterns)}")
        print(f"  Changed patterns: {len(self.changed_patterns)}")
        
        # LLM analysis of rare patterns
        if self.use_llm and rare_patterns:
            print("\n" + "=" * 80)
            print("LLM-GUIDED ANOMALY ANALYSIS")
            print("=" * 80 + "\n")
            
            llm_analysis = self.llm_analyzer.analyze_rare_patterns(rare_patterns, self.total_lines)
            print(llm_analysis)
            
            # Explain top anomalies
            print("\n" + "=" * 80)
            print("ANOMALY EXPLANATIONS")
            print("=" * 80 + "\n")
            
            for pattern in rare_patterns[:3]:  # Explain top 3 anomalies
                cluster_id = pattern['cluster_id']
                sample_log = self.log_lines_by_cluster.get(cluster_id, [""])[0]
                if sample_log:
                    print(f"Anomaly: {pattern['template']}")
                    explanation = self.llm_analyzer.explain_anomaly(
                        sample_log, pattern['template']
                    )
                    print(f"{explanation}\n")
        
        return {
            "frequent_patterns": frequent_patterns,
            "rare_patterns": rare_patterns,
            "total_lines": self.total_lines,
            "new_patterns": len(self.new_patterns)
        }
    
    def export_structured_logs(self, output_file="structured_logs.json"):
        """Export structured log data for further analysis"""
        
        clusters_sorted = sorted(
            self.template_miner.drain.clusters,
            key=lambda x: x.size,
            reverse=True
        )
        
        structured_data = {
            "total_lines": self.total_lines,
            "total_patterns": len(clusters_sorted),
            "templates": [
                {
                    "template": cluster.get_template(),
                    "count": cluster.size,
                    "cluster_id": cluster.cluster_id,
                    "example_logs": self.log_lines_by_cluster.get(cluster.cluster_id, [])[:3]
                }
                for cluster in clusters_sorted
            ],
            "new_patterns": self.new_patterns,
            "changed_patterns": self.changed_patterns
        }
        
        with open(output_file, "w") as f:
            json.dump(structured_data, f, indent=2)
        
        print(f"\n[EXPORT] Structured logs exported to {output_file}")


if __name__ == "__main__":
    # Initialize parser
    parser = EnhancedLogParser(use_llm=True)
    
    # Optional: Pre-clustering analysis
    print("=" * 80)
    print("PRE-CLUSTERING ANALYSIS (Optional)")
    print("=" * 80 + "\n")
    
    # Read sample logs for preprocessing suggestions
    with open(LOG_FILE_PATH, "r") as f:
        sample_logs = [line.strip() for line in f if line.strip()][:20]
    
    if parser.use_llm:
        print("Analyzing log patterns to suggest preprocessing rules...\n")
        preprocessing_rules = parser.llm_analyzer.suggest_preprocessing_rules(sample_logs)
        print(preprocessing_rules)
        print()
    
    # Parse logs with Drain3
    parser.parse_logs(str(LOG_FILE_PATH))
    
    # Analyze patterns
    parser.analyze_patterns()
    
    # Post-clustering enhancement
    if parser.use_llm:
        refined_clusters = parser.post_clustering_enhancement()
    
    # Export structured data
    parser.export_structured_logs(str(PROJECT_ROOT / "other" / "structured_logs.json"))
