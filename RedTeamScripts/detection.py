#!/usr/bin/env python3

import docker
import json
import subprocess

# Specify the name of the context you want to switch to
context_name = "desktop-linux"

# Get the Docker daemon URL from the context
base_url = subprocess.run(["docker", "context", "inspect", "-f", '{{.Endpoints.docker.Host}}', context_name], capture_output=True, text=True, check=True).stdout.strip()

# Create Docker client
client = docker.DockerClient(base_url=base_url)

# Get all containers
containers = client.containers.list()

containers_list = []

for container in containers:
    # Decode the bytes object to a string
    logs = container.logs().decode('utf-8')

    image_tags = container.image.tags
    image_tag = image_tags[0] if image_tags else None

    container_details = {
        "id": container.id,
        "name": container.name,
        "image": image_tag,
        "Pid": container.attrs["State"]["Pid"],
        "status": container.status,
        "ports": container.ports,
        "labels": container.labels,
        "network": container.attrs["NetworkSettings"]["Networks"],
        "environment": container.attrs["Config"]["Env"],
        "logs": logs
    }

    containers_list.append(container_details)

containers_json = json.dumps(containers_list, indent=2)
print(containers_json)
