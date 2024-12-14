"""
Monitors learning progress through periodic ARC testing and graph analysis
"""

import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from arc_tester import ARCTester

class LearningMonitor:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.progress_file = self.base_dir / 'learning_progress.json'
        self.metrics_file = self.base_dir / 'cognitive_metrics.md'
        self.load_progress()
        
    def load_progress(self) -> None:
        """Load progress history"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                self.progress = json.load(f)
        else:
            self.progress = {
                'test_runs': [],
                'baseline_established': False,
                'graph_metrics': [],
                'correlations': []
            }
    
    def save_progress(self) -> None:
        """Save progress history"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)

    def analyze_graph(self) -> Dict[str, Any]:
        """Analyze the current state of the knowledge graph"""
        try:
            # Read the graph data
            graph_file = Path('/users/bard/mcp/memory_files/graph.json')
            if not graph_file.exists():
                return {
                    'error': 'Graph file not found',
                    'metrics': {}
                }

            with open(graph_file, 'r') as f:
                graph_data = json.load(f)

            # Calculate metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'node_count': len(graph_data.get('nodes', [])),
                'edge_count': len(graph_data.get('edges', [])),
                'relationship_types': len(set(edge['type'] for edge in graph_data.get('edges', []))),
                'concept_clusters': self.identify_clusters(graph_data),
                'pattern_nodes': len([n for n in graph_data.get('nodes', []) 
                                   if 'pattern' in n.get('type', '').lower()]),
                'reasoning_nodes': len([n for n in graph_data.get('nodes', [])
                                     if 'reason' in n.get('type', '').lower()])
            }

            return {
                'success': True,
                'metrics': metrics
            }
        except Exception as e:
            return {
                'error': str(e),
                'metrics': {}
            }

    def identify_clusters(self, graph_data: Dict) -> int:
        """Identify conceptual clusters in the graph"""
        # Simple cluster counting based on connected components
        # Could be made more sophisticated
        edges = graph_data.get('edges', [])
        nodes = set()
        connections = {}
        
        for edge in edges:
            source = edge['source']
            target = edge['target']
            nodes.add(source)
            nodes.add(target)
            
            if source not in connections:
                connections[source] = set()
            if target not in connections:
                connections[target] = set()
                
            connections[source].add(target)
            connections[target].add(source)
        
        # Count connected components
        visited = set()
        clusters = 0
        
        def dfs(node):
            visited.add(node)
            for neighbor in connections.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
        
        for node in nodes:
            if node not in visited:
                clusters += 1
                dfs(node)
        
        return clusters
    
    async def run_test_suite(self) -> Dict[str, Any]:
        """Run ARC test suite and record results"""
        tester = ARCTester()
        tester.load_tasks()
        
        results = await tester.run_test_suite()
        
        # Analyze graph state
        graph_state = self.analyze_graph()
        
        # Add to progress history
        test_run = {
            'timestamp': datetime.now().isoformat(),
            'arc_results': results,
            'graph_metrics': graph_state['metrics']
        }
        
        self.progress['test_runs'].append(test_run)
        
        if not self.progress['baseline_established'] and len(self.progress['test_runs']) == 1:
            self.progress['baseline_established'] = True
            
        self.save_progress()
        self.update_metrics_document(test_run)
        
        return results
    
    def update_metrics_document(self, test_run: Dict[str, Any]) -> None:
        """Update the metrics markdown document"""
        try:
            with open(self.metrics_file, 'r') as f:
                content = f.read()
            
            # Add new test run results
            new_content = f"\n### Test Run - {test_run['timestamp']}\n"
            new_content += "#### ARC Results\n"
            new_content += f"- Tasks Attempted: {test_run['arc_results']['summary']['attempted']}\n"
            new_content += f"- Tasks Solved: {test_run['arc_results']['summary']['solved']}\n"
            new_content += f"- Success Rate: {test_run['arc_results']['summary']['success_rate']:.2%}\n\n"
            
            new_content += "#### Graph Metrics\n"
            new_content += f"- Nodes: {test_run['graph_metrics']['node_count']}\n"
            new_content += f"- Edges: {test_run['graph_metrics']['edge_count']}\n"
            new_content += f"- Relationship Types: {test_run['graph_metrics']['relationship_types']}\n"
            new_content += f"- Concept Clusters: {test_run['graph_metrics']['concept_clusters']}\n"
            new_content += f"- Pattern-related Nodes: {test_run['graph_metrics']['pattern_nodes']}\n"
            new_content += f"- Reasoning-related Nodes: {test_run['graph_metrics']['reasoning_nodes']}\n\n"
            
            # Insert after the Progress Tracking section
            track_index = content.find("## Progress Tracking")
            if track_index != -1:
                content = content[:track_index] + "## Progress Tracking\n" + new_content + content[track_index+len("## Progress Tracking"):]
            
            with open(self.metrics_file, 'w') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error updating metrics document: {str(e)}")
    
    def analyze_progress(self) -> Dict[str, Any]:
        """Analyze learning progress over time"""
        if len(self.progress['test_runs']) < 2:
            return {
                'trend': 'insufficient_data',
                'message': 'Need at least 2 test runs to analyze progress'
            }
            
        baseline = self.progress['test_runs'][0]
        latest = self.progress['test_runs'][-1]
        
        # ARC performance change
        success_delta = (
            latest['arc_results']['summary']['success_rate'] - 
            baseline['arc_results']['summary']['success_rate']
        )
        
        # Graph complexity change
        graph_growth = {
            'nodes': latest['graph_metrics']['node_count'] - baseline['graph_metrics']['node_count'],
            'edges': latest['graph_metrics']['edge_count'] - baseline['graph_metrics']['edge_count'],
            'clusters': latest['graph_metrics']['concept_clusters'] - baseline['graph_metrics']['concept_clusters']
        }
        
        return {
            'arc_trend': 'improving' if success_delta > 0 else 'declining',
            'baseline_rate': baseline['arc_results']['summary']['success_rate'],
            'current_rate': latest['arc_results']['summary']['success_rate'],
            'improvement': success_delta,
            'graph_growth': graph_growth,
            'num_tests': len(self.progress['test_runs'])
        }

async def main():
    """Run a learning progress check"""
    monitor = LearningMonitor()
    
    print("Running ARC test suite...")
    results = await monitor.run_test_suite()
    
    print("\nResults Summary:")
    print(f"Total tasks: {results['summary']['total']}")
    print(f"Attempted: {results['summary']['attempted']}")
    print(f"Solved: {results['summary']['solved']}")
    print(f"Success rate: {results['summary']['success_rate']:.2%}")
    
    progress = monitor.analyze_progress()
    print("\nLearning Progress:")
    if progress['trend'] == 'insufficient_data':
        print(progress['message'])
    else:
        print(f"ARC Performance Trend: {progress['arc_trend']}")
        print(f"Success Rate Change: {progress['improvement']:.2%}")
        print("\nGraph Growth:")
        print(f"New Nodes: {progress['graph_growth']['nodes']}")
        print(f"New Edges: {progress['graph_growth']['edges']}")
        print(f"New Clusters: {progress['graph_growth']['clusters']}")

if __name__ == '__main__':
    asyncio.run(main())