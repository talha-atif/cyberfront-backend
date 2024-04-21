import subprocess
import json
import sys

# Define the container name
container_name = sys.argv[1]

# Define the command to run within the container
# The command is a combination of 'head /etc/mtab' and the 'sed' command
command = f"docker exec {container_name} sh -c 'head /etc/mtab && sed -n \"s/.*\\perdir=\\([^,]*\\).*/\\1/p\" /etc/mtab'"

# Execute the command
try:
    exec_result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    command_output = exec_result.stdout.strip()
    output = {
        'command': command,
        'result': command_output,
        'success': True
    }

    print(json.dumps(output))
except subprocess.CalledProcessError as e:
    output = {
        'command': command,
        'result': e.stderr,
        'success': False
    }
    print(json.dumps(output))
