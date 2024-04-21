import subprocess
import sys
import json

def run_commands(container_name, command_sequence):
    combined_command = " && ".join(command_sequence)
    exec_command = f"docker exec -i {container_name} /bin/bash -c '{combined_command}'"
    exec_result = subprocess.run(exec_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if exec_result.returncode != 0:
        result = f"Error executing commands in container {container_name}:", exec_result.stderr
        output = {
            'command': exec_command,
            'result': result,
            'success': False
        }
    else:
        result = exec_result.stdout
        output = {
            'command': exec_command,
            'result': result,
            'success': True
        }

    print(json.dumps(output, indent=4))

# define container name
container_name = sys.argv[1]

# Combined commands sequence
commands_sequence = [
    "cd /dev",
    "ls",
    "mount",
    "ls cpu",
    "ls core",
    "ls ram5",
    "ls input",
    "ls mapper",
    "ls kmsg",
    "ls console",
    "ls ptmx",
    "ls bsg"
]

run_commands(container_name, commands_sequence)