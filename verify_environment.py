"""
Environment verification script to run at start of each session.
Submits commands to verify:
1. Command daemon is running
2. Ollama is running
3. Conda environment is ready
"""

from pathlib import Path
import json
import time

def create_command(command_json):
    """Create a command in the queue"""
    queue_dir = Path('/users/bard/mcp/memory_files/command_queue/pending')
    timestamp = int(time.time())
    filename = f"verify_{timestamp}.json"
    
    with open(queue_dir / filename, 'w') as f:
        json.dump(command_json, f, indent=2)
        
    # Wait briefly for command to complete
    time.sleep(2)

def verify_environment():
    # Test 1: Command daemon 
    test_command = {
        "command": "echo",
        "args": ["verify_command_daemon"],
        "description": "Verify command daemon is running" 
    }
    create_command(test_command)
    
    # Test 2: Ollama
    ollama_command = {
        "command": "bash",
        "args": ["-c", "ps -ef | grep ollama"],
        "description": "Verify Ollama is running"
    }
    create_command(ollama_command)
    
    # Test 3: Conda env
    conda_command = {
        "command": "conda",
        "args": ["run", "-n", "arc_env", "python", "-c", "print('Conda environment verified')"],
        "description": "Verify conda environment"
    }
    create_command(conda_command)
    
verify_environment()