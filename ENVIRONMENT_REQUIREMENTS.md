# Critical Environment Requirements

## Pre-run Checks
1. ALWAYS verify command daemon is running:
   ```json
   {
       "command": "bash",
       "args": ["-c", "echo test_command_daemon"],
       "description": "Test if command daemon is running"
   }
   ```

2. ALWAYS verify Ollama is running:
   ```json
   {
       "command": "bash", 
       "args": ["-c", "ps -ef | grep ollama"],
       "description": "Check if Ollama is running"
   }
   ```

## Command Execution
1. ALL commands MUST be run through the command queue
2. NEVER try to execute commands directly
3. Command queue location: /users/bard/mcp/memory_files/command_queue/pending/
4. For commands with pipes/shell features, use bash -c:
   ```json
   {
       "command": "bash",
       "args": ["-c", "your_command | pipe_command"],
       "description": "Description"
   }
   ```

## Python Environment
1. ALWAYS use the 'arc_env' conda environment:
```json
{
    "command": "conda",
    "args": ["run", "-n", "arc_env", "python", "<script_path>"],
    "cwd": "<working_directory>",
    "env": {
        "PYTHONPATH": "<python_path>"
    }
}
```

DO NOT FORGET THESE REQUIREMENTS - they are essential for all testing and execution!