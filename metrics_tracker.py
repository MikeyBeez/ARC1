"""
Comprehensive metrics tracking system for ARC challenge progress
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class PerformanceMetrics:
    avg_cpu_usage: float
    avg_memory_usage: float
    avg_model_latency: float
    task_throughput: float
    error_rate: float
    response_quality: float

class MetricsTracker:
    def __init__(self):
        self.base_dir = Path('/users/bard/mcp/arc_testing')
        self.metrics_file = self.base_dir / 'detailed_metrics.json'
        self.daily_report_file = self.base_dir / 'daily_reports'
        self.history = self.load_history()

    def analyze_efficiency(self, recent_count: int = 50) -> PerformanceMetrics:
        """Analyze system efficiency metrics"""
        system = self.history.get('system_metrics', [])
        if not system:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0)
            
        recent = system[-recent_count:]
        
        metrics = PerformanceMetrics(
            avg_cpu_usage=np.mean([s['cpu_usage'] for s in recent]),
            avg_memory_usage=np.mean([s['memory_usage'] for s in recent]),
            avg_model_latency=np.mean([s['model_latency'] for s in recent]),
            task_throughput=np.mean([s['task_throughput'] for s in recent]),
            error_rate=sum(1 for s in recent if s.get('errors')) / len(recent),
            response_quality=np.mean([s.get('response_quality', 0) for s in recent])
        )
        
        return metrics

    def get_recent_milestones(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get most recent milestones"""
        milestones = self.history.get('milestones', [])
        return sorted(milestones, key=lambda x: x['timestamp'], reverse=True)[:count]

    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate comprehensive daily report"""
        today = datetime.now().date().isoformat()
        report = {
            'date': today,
            'test_summary': self.summarize_daily_tests(),
            'learning_progress': self.summarize_learning_progress(),
            'system_performance': asdict(self.analyze_efficiency()),
            'areas_for_improvement': self.identify_improvement_areas(),
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        report_path = self.daily_report_file / f'report_{today}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report

    def summarize_daily_tests(self) -> Dict[str, Any]:
        """Summarize test results for the day"""
        today = datetime.now().date().isoformat()
        today_tests = [
            t for t in self.history.get('test_metrics', [])
            if t['timestamp'].startswith(today)
        ]
        
        if not today_tests:
            return {'status': 'No tests run today'}
            
        return {
            'total_tests': len(today_tests),
            'successful_tests': sum(1 for t in today_tests if t['success']),
            'average_time': np.mean([t['time_taken'] for t in today_tests]),
            'pattern_recognition': np.mean([t['pattern_recognition_score'] for t in today_tests]),
            'reasoning_quality': np.mean([t['reasoning_quality_score'] for t in today_tests]),
            'solution_efficiency': np.mean([t['solution_efficiency_score'] for t in today_tests])
        }

    def summarize_learning_progress(self) -> Dict[str, Any]:
        """Summarize learning progress"""
        if not self.history.get('learning_metrics'):
            return {'status': 'No learning data available'}
            
        current = self.history['learning_metrics'][-1]
        initial = self.history['learning_metrics'][0]
        
        return {
            'graph_growth': {
                'nodes': current['graph_nodes'] - initial['graph_nodes'],
                'edges': current['graph_edges'] - initial['graph_edges'],
                'clusters': current['concept_clusters'] - initial['concept_clusters']
            },
            'skills_mastered': len(current['mastered_skills']),
            'new_skills_today': set(current['mastered_skills']) - set(initial['mastered_skills'])
        }

    def identify_improvement_areas(self) -> List[Dict[str, Any]]:
        """Identify areas needing improvement"""
        areas = []
        
        # Analyze recent test performance
        recent_tests = self.history.get('test_metrics', [])[-20:]
        if recent_tests:
            success_rate = sum(1 for t in recent_tests if t['success']) / len(recent_tests)
            if success_rate < 0.8:
                areas.append({
                    'area': 'test_performance',
                    'metric': success_rate,
                    'threshold': 0.8,
                    'priority': 'high'
                })
                
        # Check system performance
        metrics = self.analyze_efficiency()
        if metrics.avg_cpu_usage > 80:
            areas.append({
                'area': 'system_resources',
                'metric': metrics.avg_cpu_usage,
                'threshold': 80,
                'priority': 'medium'
            })
            
        # Check learning progress
        learning = self.history.get('learning_metrics', [])
        if len(learning) >= 2:
            last = learning[-1]
            prev = learning[-2]
            growth_rate = (last['graph_nodes'] - prev['graph_nodes']) / prev['graph_nodes']
            if growth_rate < 0.1:
                areas.append({
                    'area': 'learning_rate',
                    'metric': growth_rate,
                    'threshold': 0.1,
                    'priority': 'high'
                })
                
        return areas

    def generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        areas = self.identify_improvement_areas()
        
        for area in areas:
            if area['area'] == 'test_performance':
                recommendations.extend([
                    "Increase focus on pattern recognition training",
                    "Add more test cases for failed patterns",
                    "Review and optimize solution strategies"
                ])
            elif area['area'] == 'system_resources':
                recommendations.extend([
                    "Optimize resource usage in pattern analysis",
                    "Implement batch processing for tests",
                    "Review and clean up graph database"
                ])
            elif area['area'] == 'learning_rate':
                recommendations.extend([
                    "Expand pattern variety in training",
                    "Increase complexity of test cases gradually",
                    "Enhance pattern extraction algorithms"
                ])
                
        return recommendations

def main():
    """Test the metrics tracker"""
    tracker = MetricsTracker()
    
    # Generate daily report
    report = tracker.generate_daily_report()
    
    print("\nDaily Report Summary:")
    print(f"Tests Run: {report['test_summary'].get('total_tests', 0)}")
    print(f"Success Rate: {report['test_summary'].get('successful_tests', 0)}")
    
    # Show improvement areas
    print("\nAreas for Improvement:")
    for area in report.get('areas_for_improvement', []):
        print(f"- {area['area']}: {area['metric']:.2f} vs threshold {area['threshold']}")
    
    # Show recommendations
    print("\nRecommendations:")
    for rec in report.get('recommendations', []):
        print(f"- {rec}")

if __name__ == '__main__':
    main()