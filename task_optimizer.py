"""
Optimizes ARC task processing and analysis
"""

import numpy as np
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from enhanced_pattern_analysis import EnhancedPatternAnalyzer

@dataclass
class TaskMetrics:
    task_id: str
    difficulty: float
    complexity: float
    pattern_types: List[str]
    required_skills: List[str]

class TaskOptimizer:
    def __init__(self):
        self.pattern_analyzer = EnhancedPatternAnalyzer()
        self.performance_history = {}
        
    def get_mastered_skills(self, completed_tasks: List[Dict]) -> Set[str]:
        """Determine which skills have been mastered based on performance"""
        skill_successes = {}
        
        for task in completed_tasks:
            task_id = task['task_id']
            if task_id in self.performance_history:
                metrics = self.analyze_task_difficulty(task)
                success = self.performance_history[task_id].get('success', False)
                
                for skill in metrics.required_skills:
                    if skill not in skill_successes:
                        skill_successes[skill] = {'success': 0, 'total': 0}
                    skill_successes[skill]['total'] += 1
                    if success:
                        skill_successes[skill]['success'] += 1
                        
        # Consider a skill mastered if success rate >= 80%
        mastered = set()
        for skill, stats in skill_successes.items():
            if stats['total'] >= 3 and (stats['success'] / stats['total']) >= 0.8:
                mastered.add(skill)
                
        return mastered
        
    def calculate_task_score(self, task: Dict, metrics: TaskMetrics, 
                           last_difficulty: float, mastered_skills: Set[str]) -> float:
        """Calculate score for task selection"""
        # Prefer small difficulty increases
        difficulty_score = 1.0 - abs(metrics.difficulty - last_difficulty - 0.1)
        
        # Reward using mastered skills while learning new ones
        new_skills = set(metrics.required_skills) - mastered_skills
        mastered_used = len(set(metrics.required_skills) & mastered_skills)
        skill_score = (mastered_used * 0.2) + (len(new_skills) * 0.1)
        
        # Consider pattern type diversity
        pattern_score = len(metrics.pattern_types) * 0.1
        
        # Combine scores
        return difficulty_score + skill_score + pattern_score
        
    def optimize_testing_strategy(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Create optimized testing strategy"""
        ordered_tasks = self.optimize_task_order(tasks)
        
        return {
            'task_sequence': ordered_tasks,
            'checkpoint_intervals': self.determine_checkpoints(ordered_tasks),
            'skill_progression': self.plan_skill_progression(ordered_tasks),
            'estimated_completion': self.estimate_completion_time(ordered_tasks)
        }
        
    def determine_checkpoints(self, ordered_tasks: List[Dict]) -> List[int]:
        """Determine optimal points for progress assessment"""
        checkpoints = []
        
        # Add checkpoints based on difficulty jumps and new skills
        last_metrics = None
        for i, task in enumerate(ordered_tasks):
            metrics = self.analyze_task_difficulty(task)
            
            if last_metrics:
                # Check for significant difficulty increase
                if metrics.difficulty - last_metrics.difficulty > 0.2:
                    checkpoints.append(i)
                # Check for new skill introduction
                elif not set(metrics.required_skills).issubset(set(last_metrics.required_skills)):
                    checkpoints.append(i)
                    
            last_metrics = metrics
            
        return checkpoints
        
    def plan_skill_progression(self, ordered_tasks: List[Dict]) -> Dict[str, List[str]]:
        """Plan expected skill progression through tasks"""
        progression = {}
        current_skills = set()
        
        for i, task in enumerate(ordered_tasks):
            metrics = self.analyze_task_difficulty(task)
            new_skills = set(metrics.required_skills) - current_skills
            
            if new_skills:
                progression[f'stage_{i}'] = list(new_skills)
                current_skills.update(new_skills)
                
        return progression
        
    def estimate_completion_time(self, ordered_tasks: List[Dict]) -> Dict[str, float]:
        """Estimate time needed for task completion"""
        total_time = 0
        time_per_difficulty = {
            'easy': 30,    # seconds
            'medium': 60,
            'hard': 120,
            'very_hard': 180
        }
        
        for task in ordered_tasks:
            metrics = self.analyze_task_difficulty(task)
            
            # Determine difficulty category
            if metrics.difficulty < 0.3:
                category = 'easy'
            elif metrics.difficulty < 0.6:
                category = 'medium'
            elif metrics.difficulty < 0.8:
                category = 'hard'
            else:
                category = 'very_hard'
                
            total_time += time_per_difficulty[category]
            
        return {
            'total_seconds': total_time,
            'minutes': total_time / 60,
            'tasks_per_hour': 3600 / (total_time / len(ordered_tasks))
        }
        
    def track_performance(self, task_id: str, success: bool, time_taken: float,
                         error_types: List[str] = None) -> None:
        """Track task performance for optimization"""
        self.performance_history[task_id] = {
            'success': success,
            'time_taken': time_taken,
            'error_types': error_types or [],
            'timestamp': np.datetime64('now')
        }
        
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends to guide optimization"""
        if not self.performance_history:
            return {'error': 'No performance data available'}
            
        trends = {
            'success_rate': {
                'overall': 0,
                'by_difficulty': {},
                'by_pattern_type': {},
                'by_skill': {}
            },
            'completion_times': {
                'average': 0,
                'trend': 'stable'
            },
            'error_patterns': {},
            'skill_mastery': self.analyze_skill_mastery()
        }
        
        # Calculate success rates
        successes = sum(1 for p in self.performance_history.values() if p['success'])
        total = len(self.performance_history)
        trends['success_rate']['overall'] = successes / total if total > 0 else 0
        
        # Analyze completion times
        times = [p['time_taken'] for p in self.performance_history.values()]
        trends['completion_times']['average'] = np.mean(times)
        
        # Analyze error patterns
        all_errors = []
        for p in self.performance_history.values():
            all_errors.extend(p.get('error_types', []))
        for error in set(all_errors):
            trends['error_patterns'][error] = all_errors.count(error)
            
        return trends
        
    def analyze_skill_mastery(self) -> Dict[str, float]:
        """Analyze mastery level of different skills"""
        skill_performance = {}
        
        for task_id, performance in self.performance_history.items():
            task_metrics = self.analyze_task_difficulty({'task_id': task_id})
            
            for skill in task_metrics.required_skills:
                if skill not in skill_performance:
                    skill_performance[skill] = {'success': 0, 'total': 0}
                    
                skill_performance[skill]['total'] += 1
                if performance['success']:
                    skill_performance[skill]['success'] += 1
                    
        return {
            skill: (stats['success'] / stats['total'] if stats['total'] > 0 else 0)
            for skill, stats in skill_performance.items()
        }

def main():
    """Test the task optimizer"""
    optimizer = TaskOptimizer()
    
    # Example task
    task = {
        'task_id': 'test_001',
        'train': [
            {
                'input': [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                'output': [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
            }
        ]
    }
    
    # Analyze task
    metrics = optimizer.analyze_task_difficulty(task)
    print(f"\nTask Analysis:")
    print(f"Difficulty: {metrics.difficulty:.2f}")
    print(f"Complexity: {metrics.complexity:.2f}")
    print(f"Pattern Types: {metrics.pattern_types}")
    print(f"Required Skills: {metrics.required_skills}")

if __name__ == '__main__':
    main()