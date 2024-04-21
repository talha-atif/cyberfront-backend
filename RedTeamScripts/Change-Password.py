import subprocess
import sys
import json

container_name = sys.argv[1]

# Dummy password
dummy_password = "5TxerMA96bLMvB" 

# Command to change the root password of the container
change_password_command = f"docker exec {container_name} sh -c 'echo root:{dummy_password} | chpasswd'"

change_password_result = subprocess.run(change_password_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Constructing the output as a JSON object
output_data = {
    "command": change_password_command,
    "result": change_password_result.returncode,
    "success": False
}

if change_password_result.returncode != 0:
    output_data["result"] = change_password_result.stderr.strip()
    print(json.dumps(output_data))
else:
    output_data["result"] = f"Password changed for container {container_name} to {dummy_password}"
    output_data["success"] = True
    print(json.dumps(output_data))
