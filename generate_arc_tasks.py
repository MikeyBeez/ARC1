"""Generate the complete set of ARC tasks"""

import json
from pathlib import Path

def generate_basic_transformation_tasks():
    """Generate basic transformation tasks"""
    tasks = [
        {
            "task_id": "basic_001",
            "category": "basic_transformation",
            "train": [
                {
                    "input": [[0, 0, 0], [0, 1, 0], [0, 0, 0]],
                    "output": [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
                },
                {
                    "input": [[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
                    "output": [[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 0, 0, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]],
                    "output": [[1, 1, 1, 1, 1], [1, 0, 0, 0, 1], [1, 1, 1, 1, 1]]
                }
            ]
        },
        {
            "task_id": "basic_002",
            "category": "basic_transformation",
            "train": [
                {
                    "input": [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[2, 0, 0], [0, 0, 0], [0, 0, 0]]
                },
                {
                    "input": [[0, 1, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[0, 2, 0], [0, 0, 0], [0, 0, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 1], [0, 0, 0], [0, 0, 0]],
                    "output": [[0, 0, 2], [0, 0, 0], [0, 0, 0]]
                }
            ]
        }
    ]
    return tasks

def generate_pattern_completion_tasks():
    """Generate pattern completion tasks"""
    tasks = [
        {
            "task_id": "pattern_001",
            "category": "pattern_completion",
            "train": [
                {
                    "input": [[1, 0, 1], [0, 1, 0], [0, 0, 0]],
                    "output": [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
                }
            ],
            "test": [
                {
                    "input": [[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 0, 0]],
                    "output": [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0]]
                }
            ]
        },
        {
            "task_id": "pattern_002",
            "category": "pattern_completion",
            "train": [
                {
                    "input": [[1, 0, 0], [0, 1, 0], [0, 0, 0]],
                    "output": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 1], [0, 1, 0], [0, 0, 0]],
                    "output": [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
                }
            ]
        }
    ]
    return tasks

def generate_spatial_reasoning_tasks():
    """Generate spatial reasoning tasks"""
    tasks = [
        {
            "task_id": "spatial_001",
            "category": "spatial_reasoning",
            "train": [
                {
                    "input": [[1, 1, 1], [0, 0, 0], [0, 0, 0]],
                    "output": [[0, 0, 0], [0, 0, 0], [1, 1, 1]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 0], [1, 1, 1], [0, 0, 0]],
                    "output": [[0, 0, 0], [0, 0, 0], [1, 1, 1]]
                }
            ]
        },
        {
            "task_id": "spatial_002",
            "category": "spatial_reasoning",
            "train": [
                {
                    "input": [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[0, 0, 1], [0, 0, 0], [0, 0, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 1, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[0, 0, 0], [0, 0, 1], [0, 0, 0]]
                }
            ]
        }
    ]
    return tasks

def generate_abstract_rule_tasks():
    """Generate abstract rule tasks"""
    tasks = [
        {
            "task_id": "abstract_001",
            "category": "abstract_rules",
            "train": [
                {
                    "input": [[1, 1, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[2, 2, 0], [0, 0, 0], [0, 0, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 0], [1, 1, 0], [0, 0, 0]],
                    "output": [[0, 0, 0], [2, 2, 0], [0, 0, 0]]
                }
            ]
        },
        {
            "task_id": "abstract_002",
            "category": "abstract_rules",
            "train": [
                {
                    "input": [[1, 1], [1, 0]],
                    "output": [[2, 2], [2, 1]]
                }
            ],
            "test": [
                {
                    "input": [[0, 1], [1, 1]],
                    "output": [[1, 2], [2, 2]]
                }
            ]
        }
    ]
    return tasks

def generate_multi_step_tasks():
    """Generate tasks requiring multiple steps"""
    tasks = [
        {
            "task_id": "multi_001",
            "category": "multi_step_reasoning",
            "train": [
                {
                    "input": [[1, 0, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 1], [0, 0, 0], [0, 0, 0]],
                    "output": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                }
            ]
        },
        {
            "task_id": "multi_002",
            "category": "multi_step_reasoning",
            "train": [
                {
                    "input": [[1, 1, 0], [0, 0, 0]],
                    "output": [[0, 0, 1], [1, 1, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 1, 1], [0, 0, 0]],
                    "output": [[1, 0, 0], [0, 1, 1]]
                }
            ]
        }
    ]
    return tasks

def generate_conditional_tasks():
    """Generate tasks with conditional rules"""
    tasks = [
        {
            "task_id": "conditional_001",
            "category": "conditional_logic",
            "train": [
                {
                    "input": [[1, 1, 0], [0, 0, 0], [0, 0, 0]],
                    "output": [[2, 2, 0], [0, 0, 0], [0, 0, 0]]
                },
                {
                    "input": [[0, 0, 0], [1, 0, 1], [0, 0, 0]],
                    "output": [[0, 0, 0], [3, 0, 3], [0, 0, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 0, 0], [0, 0, 0], [1, 1, 0]],
                    "output": [[0, 0, 0], [0, 0, 0], [2, 2, 0]]
                }
            ]
        },
        {
            "task_id": "conditional_002",
            "category": "conditional_logic",
            "train": [
                {
                    "input": [[2, 0, 0], [1, 1, 0]],
                    "output": [[3, 0, 0], [2, 2, 0]]
                }
            ],
            "test": [
                {
                    "input": [[0, 2, 0], [0, 1, 1]],
                    "output": [[0, 3, 0], [0, 2, 2]]
                }
            ]
        }
    ]
    return tasks

def write_tasks_to_files(base_dir: Path):
    """Write all generated tasks to files"""
    task_dir = base_dir / 'data/arc_tasks'
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate all task types
    all_tasks = (
        generate_basic_transformation_tasks() +
        generate_pattern_completion_tasks() +
        generate_spatial_reasoning_tasks() +
        generate_abstract_rule_tasks() +
        generate_multi_step_tasks() +
        generate_conditional_tasks()
    )
    
    # Create task categories metadata
    categories = {
        "basic_transformation": "Tasks testing basic grid transformations",
        "pattern_completion": "Tasks requiring pattern recognition and completion",
        "spatial_reasoning": "Tasks testing spatial manipulation and understanding",
        "abstract_rules": "Tasks requiring understanding of abstract transformation rules",
        "multi_step_reasoning": "Tasks requiring multiple transformation steps",
        "conditional_logic": "Tasks with conditional transformation rules"
    }
    
    # Write categories metadata
    with open(task_dir / 'task_categories.json', 'w') as f:
        json.dump(categories, f, indent=2)
        print("Generated task categories metadata")
    
    # Write individual task files
    for task in all_tasks:
        task_file = task_dir / f"{task['task_id']}.json"
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2)
        print(f"Generated task: {task['task_id']}")

def main():
    base_dir = Path('/users/bard/mcp/arc_testing')
    write_tasks_to_files(base_dir)
    print("Task generation complete!")

if __name__ == '__main__':
    main()