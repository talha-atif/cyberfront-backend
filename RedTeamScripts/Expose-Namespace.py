import subprocess
import sys
import json

# Define the container name or ID
container_name = sys.argv[1]

# Define the command to be executed
command = ["docker", "exec", container_name, "ps", "aux"]

# Execute the command and capture the output
result = subprocess.run(command, capture_output=True, text=True)

# Parse the output into lines
lines = result.stdout

output = {
    'command': " ".join(command),
    'result': lines,
    'success': True
}

# Convert the list of processes to JSON
json_output = json.dumps(output, indent=4)

# Print or return the JSON output
print(json_output)