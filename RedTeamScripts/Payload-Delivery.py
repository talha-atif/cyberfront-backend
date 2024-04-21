import subprocess
import sys
import json
import pathlib

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return result.stderr.strip()
    except Exception as e:
        return(f"An error occurred: {e}")

# Get the container name from the command line arguments
container_name = sys.argv[1]

# get the absolute path to the file './executable/main'
main_path = pathlib.Path(__file__).parent.absolute() / 'executable' / 'main'

# Ensure the 'main' binary is executable
chmod_command = f"chmod +x {main_path}"
result = execute_command(chmod_command)

# Copy the 'main' binary to the container
cp_command1 = f"docker cp {main_path} {container_name}:/main"
result1 = execute_command(cp_command1)


output = {
    "command": chmod_command + " && " + cp_command1,
    "result": "Permission granted to the main binary. \n Main binary copied to the container",
}

print(json.dumps(output))