import subprocess
import json
import re
import os

def run_docker_benchmark():
    # Capture the output of the benchmark script
    subprocess.run(["git", "clone", "https://github.com/docker/docker-bench-security.git"], text=True)
    
    # Run the benchmark script using bash shell
    benchmark_output = subprocess.check_output(["bash", "-c", "cd docker-bench-security && bash docker-bench-security.sh"], text=True)
    
    subprocess.run(["rm", "-rf", "docker-bench-security"])

    # Create a dictionary to store the captured output
    output_dict = {
        "benchmark_output": benchmark_output
    }

    # Write the output to a JSON file
    with open("./output_files/benchmark_output.json", "w") as json_file:
        json.dump(output_dict, json_file)

def restructure_benchmark_output(input_file_path, output_file_path):
    # Load the original JSON file
    with open(input_file_path, 'r') as file:
        json_data = json.load(file)

    # Extracting the benchmark output text
    benchmark_output = json_data.get("benchmark_output", "")

    # Splitting the text into lines
    lines = benchmark_output.split('\n')

    # Regex patterns for identifying different types of lines
    info_pattern = re.compile(r'\[INFO\]')
    warn_pattern = re.compile(r'\[WARN\]')
    pass_pattern = re.compile(r'\[PASS\]')

    # Structured storage for the data
    structured_data = {
        "INFO": [],
        "WARN": [],
        "PASS": []
    }

    # Categorizing each line
    for line in lines:
        if info_pattern.search(line):
            structured_data["INFO"].append(line)
        elif warn_pattern.search(line):
            structured_data["WARN"].append(line)
        elif pass_pattern.search(line):
            structured_data["PASS"].append(line)

    # Save the structured data into a new JSON file
    with open(output_file_path, 'w') as new_file:
        json.dump(structured_data, new_file, indent=4)

    return output_file_path

# run_docker_benchmark()

# Get the current working directory
current_directory = os.getcwd()

# Construct the path to the Dockerfiles folder
input_file = os.path.join(current_directory, "BlueTeamScripts/output_files/benchmark_output.json")
output_file = os.path.join(current_directory, "BlueTeamScripts/output_files/formated_output.json")

restructured_file = restructure_benchmark_output(input_file, output_file)

with open(output_file, 'r') as file:
    formated_output = json.load(file)

# Count the instances
count_info = len(formated_output['INFO'])
count_warn = len(formated_output['WARN'])
count_pass = len(formated_output['PASS'])

counts = {
    "INFO": count_info,
    "WARN": count_warn,
    "PASS": count_pass
}

output = {
    "result": formated_output,
    "counts": counts
}

# Print the counts
print(json.dumps(output, indent=4))