import subprocess
import sys
import json

def expose_secrets(container_id):
    try:
        env_vars_command = ["docker", "exec", container_id, "env"]
        env_vars_result = subprocess.run(env_vars_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if env_vars_result.returncode != 0:
            return {
                "error": env_vars_result.stderr.strip()
            }

        env_vars = env_vars_result.stdout.strip()

        # Basic checks for potential secrets
        potential_secrets = []
        for var in env_vars.split('\n'):
            if "KEY" in var or "PASSWORD" in var or "SECRET" in var or "TOKEN" in var:
                potential_secrets.append(var.split('=')[0])

        return {
            "environment_variables": env_vars,
            "potential_secrets": potential_secrets
        }
    except subprocess.CalledProcessError as e:
        return {
            "error": f"Error retrieving environment variables: {e.output.decode('utf-8')}"
        }

container_name = sys.argv[1]
result = expose_secrets(container_name)

output = {
    "command": f"docker exec {container_name} env",
    "result": result
}

if "error" in result:
    output['result'] = result['error']
    output['success'] = False
else:
    if result["potential_secrets"]:
        output['result'] = result["environment_variables"]
        output['success'] = True
    else:
        output['result'] = "No exposed passwords or API keys found in environment variables."
        output['success'] = False

print(json.dumps(output, indent=2))