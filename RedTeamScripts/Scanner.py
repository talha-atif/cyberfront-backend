import sys
import json
import subprocess

def handle_subprocess_error(e):
    """ Standardizes the error handling for subprocess calls. """
    return "No results found"  # Standard message for all errors

def check_privileged_mode(container_id):
    try:
        privileged_output = subprocess.check_output(
            ['docker', 'inspect', '--format={{.HostConfig.Privileged}}', container_id]
        ).strip().lower()
        return privileged_output == b'true'
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def check_can_be_privileged(container_id):
    try:
        config_output = subprocess.check_output(['docker', 'inspect', container_id])
        container_config = json.loads(config_output)
        return 'Privileged' in str(container_config[0]['HostConfig'])
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def check_linux_capabilities(container_id):
    try:
        return subprocess.check_output(
            ['docker', 'exec', container_id, 'capsh', '--print']
        ).strip().decode('utf-8')
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def check_seccomp_profile(container_id):
    try:
        security_opts = subprocess.check_output(
            ['docker', 'inspect', '--format={{.HostConfig.SecurityOpt}}', container_id]
        ).strip().decode('utf-8')
        
        # Extract only the seccomp profile part
        for opt in security_opts.split(","):
            if "seccomp" in opt:
                return opt
        return "No seccomp profile found"
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def check_apparmor_profile(container_id):
    try:
        security_opts = subprocess.check_output(
            ['docker', 'inspect', '--format={{.HostConfig.SecurityOpt}}', container_id]
        ).strip().decode('utf-8')

        # Extract only the AppArmor profile part
        for opt in security_opts.split(","):
            if "apparmor" in opt.lower():
                return opt
        return "No AppArmor profile found"
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)


def check_open_ports(container_id):
    try:
        return subprocess.check_output(
            ['docker', 'exec', container_id, 'netstat', '-tuln']
        ).strip().decode('utf-8')
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def check_outdated_packages(container_id):
    try:
        outdated_packages_command = (
            "sh -c 'command -v apt-get && apt-get update && apt-get -s upgrade || "
            "command -v apk && apk update && apk outdated || "
            "command -v yum && yum check-update || echo No package manager found'"
        )
        return subprocess.check_output(
            ['docker', 'exec', container_id, outdated_packages_command], shell=True
        ).strip().decode('utf-8')
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def retrieve_image_details(container_id):
    try:
        inspect_output = subprocess.check_output(['docker', 'inspect', container_id])
        return json.loads(inspect_output)[0]
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def find_world_writable_files(container_id):
    try:
        ww_files_command = ["docker", "exec", container_id, "find", "/", "-xdev", "-type", "f", "-perm", "-0002", "-print"]
        ww_files = subprocess.check_output(ww_files_command).strip().decode('utf-8')
        return ww_files if ww_files else "No world-writable files found."
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def get_environment_variables(container_id):
    try:
        env_vars_command = ["docker", "exec", container_id, "env"]
        env_vars = subprocess.check_output(env_vars_command).strip().decode('utf-8')
        return env_vars
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)
    
def check_resource_limits(container_id):
    try:
        resource_limits = subprocess.check_output(
            ['docker', 'inspect', '--format={{.HostConfig.CpuQuota}} {{.HostConfig.CpuPeriod}} {{.HostConfig.Memory}}', container_id]
        ).strip().decode('utf-8')
        cpu_quota, cpu_period, memory_limit = resource_limits.split()
        cpu_quota = int(cpu_quota)
        cpu_period = int(cpu_period)
        memory_limit = int(memory_limit)
        limits = {}
        if cpu_quota > 0 and cpu_period > 0:
            limits['CPU'] = f"{cpu_quota/cpu_period} cores"
        else:
            limits['CPU'] = "No limit"
        if memory_limit > 0:
            limits['Memory'] = f"{memory_limit/(1024*1024)} MB"
        else:
            limits['Memory'] = "No limit"
        return limits
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e)

def get_environment_variables_and_check_secrets(container_id):
    try:
        env_vars_command = ["docker", "exec", container_id, "env"]
        env_vars = subprocess.check_output(env_vars_command).strip().decode('utf-8')
        potential_secrets = []
        for var in env_vars.split('\n'):
            if "KEY" in var or "PASSWORD" in var or "SECRET" in var or "TOKEN" in var:
                potential_secrets.append(var.split('=')[0])
        return env_vars, potential_secrets
    except subprocess.CalledProcessError as e:
        return handle_subprocess_error(e), []

def perform_security_checks(container_id):
    results = {
        "Is Privileged": check_privileged_mode(container_id),
        "Can Be Privileged": check_can_be_privileged(container_id),
        "Linux Capabilities": check_linux_capabilities(container_id),
        "Seccomp Profile": check_seccomp_profile(container_id),
        "AppArmor Profile": check_apparmor_profile(container_id),
        "Open Ports": check_open_ports(container_id),
        #"Outdated Packages": check_outdated_packages(container_id),
        "World-Writable Files": find_world_writable_files(container_id),
        "Environment Variables": get_environment_variables(container_id),
        "Resource Limits": check_resource_limits(container_id),
        #"Potential Secrets": get_environment_variables_and_check_secrets(container_id)[1]
    }

    container_info = retrieve_image_details(container_id)
    results["Docker Image Details"] = {
        "Image": container_info.get("Config", {}).get("Image", "No results found"),
        "Image ID": container_info.get("Image", "No results found"),
        "Created At": container_info.get("Created", "No results found")
    }

    return results

container_id = sys.argv[1]
security_check_results = perform_security_checks(container_id)
print(json.dumps(security_check_results, indent=4))
