"""
Integrates ARC testing with graph database analysis
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class GraphAnalyzer:
    """Analyzes relationships between graph knowledge and ARC performance"""
    
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.graph_file = Path('/users/bard/mcp/memory_files/graph.json')
        self.correlations_file = self.base_dir / 'graph_correlations.json'
        
    def load_graph_data(self) -> Dict[str, Any]:
        """Load current state of knowledge graph"""
        with open(self.graph_file, 'r') as f:
            return json.load(f)
            
    def analyze_graph_metrics(self) -> Dict[str, Any]:
        """Calculate current graph metrics"""
        graph_data = self.load_graph_data()
        
        # Node type analysis
        node_types = {}
        pattern_nodes = []
        reasoning_nodes = []
        
        for node in graph_data.get('nodes', []):
            node_type = node.get('type', 'unknown')
            if node_type not in node_types:
                node_types[node_type] = 0
            node_types[node_type] += 1
            
            # Track specific node types
            if 'pattern' in node_type.lower():
                pattern_nodes.append(node)
            if 'reason' in node_type.lower():
                reasoning_nodes.append(node)
                
        # Relationship analysis
        relationships = {}
        for edge in graph_data.get('edges', []):
            rel_type = edge.get('type', 'unknown')
            if rel_type not in relationships:
                relationships[rel_type] = 0
            relationships[rel_type] += 1
            
        # Calculate cluster metrics
        clusters = self.identify_clusters(graph_data)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_nodes': len(graph_data.get('nodes', [])),
            'total_edges': len(graph_data.get('edges', [])),
            'node_types': node_types,
            'pattern_nodes': len(pattern_nodes),
            'reasoning_nodes': len(reasoning_nodes),
            'relationships': relationships,
            'clusters': len(clusters),
            'cluster_sizes': [len(c) for c in clusters],
            'density': self.calculate_density(graph_data)
        }
        
    def identify_clusters(self, graph_data: Dict) -> List[Set[str]]:
        """Find connected components in the graph"""
        nodes = set(n['id'] for n in graph_data.get('nodes', []))
        edges = [(e['source'], e['target']) for e in graph_data.get('edges', [])]
        
        # Build adjacency list
        adjacency = {n: set() for n in nodes}
        for source, target in edges:
            adjacency[source].add(target)
            adjacency[target].add(source)
            
        # Find clusters using DFS
        clusters = []
        unvisited = nodes.copy()
        
        def dfs(node: str, cluster: Set[str]):
            cluster.add(node)
            unvisited.remove(node)
            for neighbor in adjacency[node]:
                if neighbor in unvisited:
                    dfs(neighbor, cluster)
                    
        while unvisited:
            node = next(iter(unvisited))
            cluster = set()
            dfs(node, cluster)
            clusters.append(cluster)
            
        return clusters
        
    def calculate_density(self, graph_data: Dict) -> float:
        """Calculate graph density"""
        nodes = len(graph_data.get('nodes', []))
        edges = len(graph_data.get('edges', []))
        if nodes <= 1:
            return 0
        max_edges = (nodes * (nodes - 1)) / 2
        return edges / max_edges if max_edges > 0 else 0
        
    def analyze_arc_correlations(self, arc_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlations between graph metrics and ARC performance"""
        graph_metrics = self.analyze_graph_metrics()
        
        # Load historical correlations
        correlations = self.load_correlations()
        
        # Calculate new correlations
        new_correlation = {
            'timestamp': datetime.now().isoformat(),
            'graph_metrics': graph_metrics,
            'arc_results': arc_results,
            'correlations': {
                'pattern_impact': self.calculate_pattern_correlation(
                    graph_metrics['pattern_nodes'],
                    arc_results
                ),
                'reasoning_impact': self.calculate_reasoning_correlation(
                    graph_metrics['reasoning_nodes'],
                    arc_results
                ),
                'cluster_impact': self.calculate_cluster_correlation(
                    graph_metrics['clusters'],
                    arc_results
                )
            }
        }
        
        # Add to history
        correlations['history'].append(new_correlation)
        self.save_correlations(correlations)
        
        return new_correlation
        
    def calculate_pattern_correlation(self, pattern_nodes: int, arc_results: Dict) -> Dict[str, float]:
        """Calculate correlation between pattern nodes and pattern-related task performance"""
        pattern_tasks = {}
        for task_id, task in arc_results['tasks'].items():
            if 'pattern' in task.get('category', '').lower():
                pattern_tasks[task_id] = task
                
        success_rate = (
            len([t for t in pattern_tasks.values() if t['success']]) /
            len(pattern_tasks)
            if pattern_tasks else 0
        )
        
        return {
            'pattern_nodes': pattern_nodes,
            'pattern_task_success': success_rate
        }
        
    def calculate_reasoning_correlation(self, reasoning_nodes: int, arc_results: Dict) -> Dict[str, float]:
        """Calculate correlation between reasoning nodes and multi-step task performance"""
        reasoning_tasks = {}
        for task_id, task in arc_results['tasks'].items():
            if any(s in task.get('category', '').lower() for s in ['reason', 'multi', 'abstract']):
                reasoning_tasks[task_id] = task
                
        success_rate = (
            len([t for t in reasoning_tasks.values() if t['success']]) /
            len(reasoning_tasks)
            if reasoning_tasks else 0
        )
        
        return {
            'reasoning_nodes': reasoning_nodes,
            'reasoning_task_success': success_rate
        }
        
    def calculate_cluster_correlation(self, num_clusters: int, arc_results: Dict) -> Dict[str, float]:
        """Calculate correlation between knowledge clusters and overall performance"""
        success_rate = (
            arc_results['summary']['solved'] /
            arc_results['summary']['attempted']
            if arc_results['summary']['attempted'] > 0 else 0
        )
        
        return {
            'clusters': num_clusters,
            'overall_success': success_rate
        }
        
    def load_correlations(self) -> Dict[str, Any]:
        """Load historical correlation data"""
        if self.correlations_file.exists():
            with open(self.correlations_file, 'r') as f:
                return json.load(f)
        return {'history': []}
        
    def save_correlations(self, correlations: Dict[str, Any]) -> None:
        """Save correlation data"""
        with open(self.correlations_file, 'w') as f:
            json.dump(correlations, f, indent=2)
            
    def generate_correlation_report(self) -> str:
        """Generate a readable report of current correlations"""
        correlations = self.load_correlations()
        if not correlations['history']:
            return "No correlation data available yet."
            
        latest = correlations['history'][-1]
        report = ["Knowledge Graph Impact Analysis\n"]
        
        # Pattern recognition impact
        pattern_corr = latest['correlations']['pattern_impact']
        report.append("Pattern Recognition:")
        report.append(f"- Pattern Nodes: {pattern_corr['pattern_nodes']}")
        report.append(f"- Pattern Task Success: {pattern_corr['pattern_task_success']:.2%}\n")
        
        # Reasoning impact
        reason_corr = latest['correlations']['reasoning_impact']
        report.append("Abstract Reasoning:")
        report.append(f"- Reasoning Nodes: {reason_corr['reasoning_nodes']}")
        report.append(f"- Complex Task Success: {reason_corr['reasoning_task_success']:.2%}\n")
        
        # Overall impact
        cluster_corr = latest['correlations']['cluster_impact']
        report.append("Knowledge Organization:")
        report.append(f"- Knowledge Clusters: {cluster_corr['clusters']}")
        report.append(f"- Overall Success Rate: {cluster_corr['overall_success']:.2%}\n")
        
        # Growth metrics
        if len(correlations['history']) > 1:
            prev = correlations['history'][-2]
            node_growth = (
                latest['graph_metrics']['total_nodes'] -
                prev['graph_metrics']['total_nodes']
            )
            success_change = (
                cluster_corr['overall_success'] -
                prev['correlations']['cluster_impact']['overall_success']
            )
            report.append("Growth Metrics:")
            report.append(f"- New Knowledge Nodes: {node_growth}")
            report.append(f"- Performance Change: {success_change:+.2%}")
            
        return '\n'.join(report)

async def main():
    """Run graph analysis and correlation"""
    analyzer = GraphAnalyzer()
    
    print("Analyzing graph metrics...")
    metrics = analyzer.analyze_graph_metrics()
    
    print("\nCurrent Graph State:")
    print(f"Total Nodes: {metrics['total_nodes']}")
    print(f"Total Edges: {metrics['total_edges']}")
    print(f"Knowledge Clusters: {metrics['clusters']}")
    print(f"Graph Density: {metrics['density']:.2%}")
    
    if analyzer.correlations_file.exists():
        print("\nCorrelation Report:")
        print(analyzer.generate_correlation_report())
    else:
        print("\nNo correlation data available yet.")

if __name__ == '__main__':
    asyncio.run(main())