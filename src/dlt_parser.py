from pathlib import Path
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence
from drain3.template_miner_config import TemplateMinerConfig
from src.llm_analyzer import LLMLogAnalyzer
from src.config import RARE_PATTERN_THRESHOLD, FREQUENCY_THRESHOLD
import json
import csv

PROJECT_ROOT = Path(__file__).parent.parent
DLT_LOG_FILE = PROJECT_ROOT / "data" / "dlt_logs.csv"

class DLTLogParser:
    
    def __init__(self, use_llm=True):
        config = TemplateMinerConfig()
        config.profiling_enabled = False
        config.drain_sim_th = 0.5
        config.drain_depth = 4
        config.drain_max_children = 100
        
        project_root = Path(__file__).parent.parent
        state_file = project_root / "other" / "dlt_drain3_state.bin"
        persistence = FilePersistence(str(state_file))
        self.template_miner = TemplateMiner(persistence, config)
        
        self.use_llm = use_llm
        if use_llm:
            self.llm_analyzer = LLMLogAnalyzer()
        
        # Track metrics
        self.total_lines = 0
        self.log_lines_by_cluster = {}
        self.dlt_metadata = {}  # Store DLT-specific metadata
        
    def parse_dlt_logs(self, csv_file):
        """Parse DLT format logs from CSV"""
        
        print("=== Starting DLT Log Parsing ===\n")
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Try to detect delimiter
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Extract DLT fields
                    timestamp = row.get('Timestamp', row.get('timestamp', ''))
                    index = row.get('Index', row.get('index', ''))
                    ecu = row.get('ECU', row.get('ecu', ''))
                    app_id = row.get('Application ID', row.get('application_id', ''))
                    message = row.get('Log Message', row.get('message', ''))
                    
                    if not message:
                        continue
                    
                    # Process only the log message with Drain3
                    result = self.template_miner.add_log_message(message)
                    self.total_lines += 1
                    
                    cluster_id = result["cluster_id"]
                    
                    # Store full log entry with metadata
                    if cluster_id not in self.log_lines_by_cluster:
                        self.log_lines_by_cluster[cluster_id] = []
                        self.dlt_metadata[cluster_id] = {
                            'ecus': set(),
                            'app_ids': set(),
                            'timestamps': []
                        }
                    
                    self.log_lines_by_cluster[cluster_id].append(message)
                    self.dlt_metadata[cluster_id]['ecus'].add(ecu)
                    self.dlt_metadata[cluster_id]['app_ids'].add(app_id)
                    self.dlt_metadata[cluster_id]['timestamps'].append(timestamp)
        
        except Exception as e:
            print(f"Error parsing DLT CSV: {e}")
            print("Trying alternative parsing...")
            # Fallback: try tab-separated
            self._parse_tsv(csv_file)
        
        print(f"[COMPLETE] Parsed {self.total_lines} DLT log lines\n")
    
    def _parse_tsv(self, file_path):
        """Fallback parser for tab/space separated DLT logs"""
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 5:
                    message = parts[4]  # Last column is message
                    result = self.template_miner.add_log_message(message)
                    self.total_lines += 1
                    cluster_id = result["cluster_id"]
                    
                    if cluster_id not in self.log_lines_by_cluster:
                        self.log_lines_by_cluster[cluster_id] = []
                    self.log_lines_by_cluster[cluster_id].append(message)
    
    def analyze_patterns(self):
        """Analyze patterns with DLT metadata"""
        
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
                "cluster_id": cluster.cluster_id,
                "ecus": list(self.dlt_metadata.get(cluster.cluster_id, {}).get('ecus', [])),
                "app_ids": list(self.dlt_metadata.get(cluster.cluster_id, {}).get('app_ids', []))
            }
            
            if cluster.size <= RARE_PATTERN_THRESHOLD or pattern_info["percentage"] < FREQUENCY_THRESHOLD * 100:
                rare_patterns.append(pattern_info)
            else:
                frequent_patterns.append(pattern_info)
        
        # Display results
        print("=" * 80)
        print("DLT LOG CLUSTERING RESULTS")
        print("=" * 80)
        
        print(f"\nFrequent Patterns ({len(frequent_patterns)} patterns):\n")
        for pattern in frequent_patterns[:10]:
            print(f"  [C{pattern['cluster_id']:>3}] Count: {pattern['count']:>4} ({pattern['percentage']:>5.1f}%)")
            print(f"       Template: {pattern['template']}")
            print(f"       ECUs: {', '.join(pattern['ecus'][:3])}")
            print(f"       Apps: {', '.join(pattern['app_ids'][:3])}\n")
        
        print(f"\nRare Patterns ({len(rare_patterns)} patterns):\n")
        for pattern in rare_patterns[:10]:
            print(f"  [C{pattern['cluster_id']:>3}] Count: {pattern['count']:>4} ({pattern['percentage']:>5.1f}%)")
            print(f"       Template: {pattern['template']}")
            print(f"       ECUs: {', '.join(pattern['ecus'][:3])}")
            print(f"       Apps: {', '.join(pattern['app_ids'][:3])}\n")
        
        print(f"Statistics:")
        print(f"  Total log lines: {self.total_lines}")
        print(f"  Total patterns: {len(clusters_sorted)}")
        print(f"  Unique ECUs: {len(set.union(*[self.dlt_metadata.get(c.cluster_id, {}).get('ecus', set()) for c in clusters_sorted]))}")
        print(f"  Unique Apps: {len(set.union(*[self.dlt_metadata.get(c.cluster_id, {}).get('app_ids', set()) for c in clusters_sorted]))}")
        
        # LLM analysis
        if self.use_llm and rare_patterns:
            print("\n" + "=" * 80)
            print("LLM ANALYSIS")
            print("=" * 80 + "\n")
            
            llm_analysis = self.llm_analyzer.analyze_rare_patterns(rare_patterns[:5], self.total_lines)
            print(llm_analysis)
        
        return {"frequent": frequent_patterns, "rare": rare_patterns}
    
    def refine_top_clusters(self):
        """LLM refinement of top clusters"""
        
        if not self.use_llm:
            return
        
        print("\n" + "=" * 80)
        print("LLM CLUSTER REFINEMENT")
        print("=" * 80 + "\n")
        
        clusters_sorted = sorted(
            self.template_miner.drain.clusters,
            key=lambda x: x.size,
            reverse=True
        )
        
        for cluster in clusters_sorted[:2]:  # Top 2
            cluster_id = cluster.cluster_id
            template = cluster.get_template()
            samples = self.log_lines_by_cluster.get(cluster_id, [])[:3]
            
            print(f"Refining Cluster {cluster_id} (Count: {cluster.size})...")
            refinement = self.llm_analyzer.refine_cluster_template(template, samples, cluster_id)
            print(f"{refinement}\n")
    
    def export_dlt_results(self, output_file="dlt_structured_logs.json"):
        """Export DLT analysis results"""
        
        clusters_sorted = sorted(
            self.template_miner.drain.clusters,
            key=lambda x: x.size,
            reverse=True
        )
        
        structured_data = {
            "total_lines": self.total_lines,
            "total_patterns": len(clusters_sorted),
            "dlt_format": True,
            "templates": []
        }
        
        for cluster in clusters_sorted:
            cid = cluster.cluster_id
            structured_data["templates"].append({
                "template": cluster.get_template(),
                "count": cluster.size,
                "cluster_id": cid,
                "ecus": list(self.dlt_metadata.get(cid, {}).get('ecus', [])),
                "app_ids": list(self.dlt_metadata.get(cid, {}).get('app_ids', [])),
                "example_logs": self.log_lines_by_cluster.get(cid, [])[:3]
            })
        
        output_path = Path(__file__).parent.parent / "other" / output_file
        with open(output_path, "w") as f:
            json.dump(structured_data, f, indent=2)
        
        print(f"\n[EXPORT] DLT results exported to {output_path}")


if __name__ == "__main__":
    # Initialize parser
    parser = DLTLogParser(use_llm=True)
    
    # Parse DLT logs
    parser.parse_dlt_logs(str(DLT_LOG_FILE))
    
    # Analyze patterns
    parser.analyze_patterns()
    
    # Refine with LLM
    parser.refine_top_clusters()
    
    # Export results
    parser.export_dlt_results()
