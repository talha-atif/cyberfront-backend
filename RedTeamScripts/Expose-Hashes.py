import subprocess
import json
import sys

# Define the container name
container_name = sys.argv[1]

# Define the command to run
command = ["docker", "exec", container_name, "cat", "/etc/shadow"]

# Execute the command
try:
    exec_result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    shadow_content = exec_result.stdout.strip()

    output= {
        "command": " ".join(command),
        "result": shadow_content,
        "success": True
        }
    print(json.dumps(output))
except subprocess.CalledProcessError as e:
    output= {
        "command": " ".join(command),
        "result": e.stderr,
        "success": False
        }
    print(json.dumps(output))