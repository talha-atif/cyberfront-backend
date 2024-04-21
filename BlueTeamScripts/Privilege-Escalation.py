import subprocess
import sys
import os
import json

output = []

def run_command(command):
    """ Helper function to run a shell command and return its output """
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output.append(command)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def container_exists(container_name):
    """ Check if a container exists """
    output, error, returncode = run_command(f"docker ps -a -q -f name=^{container_name}$")
    return returncode == 0 and output != ""

def stop_and_remove_container(container_name):
    """ Stop and remove a container """
    stop_cmd = f"docker stop {container_name}"
    remove_cmd = f"docker rm {container_name}"
    run_command(stop_cmd)
    run_command(remove_cmd)

def create_dockerfile(dockerfile_path, container_name):
    """ Create a Dockerfile with a specified user. """
    dockerfile_contents = f"""FROM ubuntu:latest

CMD ["tail", "-f", "/dev/null"]"""

    dockerfile_full_path = os.path.join(dockerfile_path, f"{image_name}.Dockerfile")
    with open(dockerfile_full_path, "w") as file:
        file.write(dockerfile_contents)
    return dockerfile_full_path

def build_and_run_container(container_name, dockerfiles_folder="."):
    """ Build and run a new container with detailed logging """
    # Set the path for Dockerfile
    dockerfile_full_path = os.path.join(dockerfiles_folder, f"{image_name}.Dockerfile")
    
    # Check if Dockerfile exists, if not, create one
    if not os.path.isfile(dockerfile_full_path):
        print_statement = "No Dockerfile found for {container_name} in {dockerfiles_folder}. Creating a basic Dockerfile..."
        output.append(print_statement)
        dockerfile_full_path = create_dockerfile(dockerfiles_folder, container_name)

    # Building the new Docker image
    build_cmd = f"docker build -t {image_name} -f {dockerfile_full_path} {dockerfiles_folder}"
    build_output, build_error, build_returncode = run_command(build_cmd)

    if build_output:
        output.append("Docker Build Output:")
        output.append(build_output)
    if build_error:
        output.append("Docker Build Output:")
        output.append(build_error)

    if build_returncode != 0:
        output.append("Failed to build Docker image.")
        return False

    # Running the new container
    run_cmd = f"docker run --name {container_name} -d {image_name}"
    run_output, run_error, run_returncode = run_command(run_cmd)

    if run_output:
        output.append("Docker Run Output:")
        output.append(run_output)
    if run_error:
        output.append("Docker Run Error:")
        output.append(run_error)

    if run_returncode != 0:
        output.append("Failed to run container.")
        return False

    return True

def rebuild_container(container_name, dockerfile_folder="."):
    """ Main function to rebuild a container with improved error handling """
    if container_exists(container_name):
        output.append(f"Container '{container_name}' exists. Stopping and removing...")
        stop_and_remove_container(container_name)
        output.append(f"Building and running a new container '{container_name}'...")
        if build_and_run_container(container_name, dockerfile_folder):
            output.append(f"Container '{container_name}' has been rebuilt and is running.")
        else:
            output.append("Failed to rebuild the container. Please check the error messages above.")
    else:
        output.append(f"No container found with the name '{container_name}'.")

# Set your container name here
container_name = sys.argv[1]
image_name = sys.argv[2]

# Get the current working directory
current_directory = os.getcwd()

# Construct the path to the Dockerfiles folder
dockerfiles_folder = os.path.join(current_directory, "BlueTeamScripts/Dockerfiles")

# Execute the rebuild container process
rebuild_container(container_name, dockerfiles_folder)

print(json.dumps(output))