import subprocess
import sys
import time
import re
import csv
import json

container_name = sys.argv[1]

# Define the name for the log file and CSV file
log_file = "./RedTeamScripts/output-files/container_stats.log"
csv_file = "./RedTeamScripts/output-files/container_stats.csv"

# Run the stress test in the existing container
try:
    result = subprocess.run(
        f"docker exec -d {container_name} sh -c 'apt-get update && apt-get install stress -y && stress --vm 2 --vm-bytes 2G --timeout 30'",
        shell=True,
        check=True
    )
except subprocess.CalledProcessError as e:
    output = {
    "command": [ f"docker exec -d {container_name} sh -c 'apt-get update && apt-get install stress -y && stress --vm 2 --vm-bytes 2G --timeout 30'",
                 f"docker stats --no-stream {container_name}" ],
    "result": f"Failed to start stress test in container {container_name}: {e}",
    "success": False
    }
    print(json.dumps(output))
    sys.exit(1)

# Duration of the stress test
stress_test_duration = 30  # in seconds
start_time = time.time()

# Function to remove control characters and escape sequences from a string
def remove_control_characters(input_string):
    control_chars = ''.join(map(chr, list(range(0, 32)) + list(range(127, 160))))
    control_chars_pattern = re.compile(f"[{re.escape(control_chars)}]")
    return control_chars_pattern.sub("", input_string)

# Start monitoring the container and append the output to the log file
result = []
with open(log_file, "w") as log:
    while time.time() - start_time < stress_test_duration:
        # Execute docker stats command
        stats_output = subprocess.check_output(
            f"docker stats --no-stream {container_name}",
            shell=True,
            text=True
        )
        result.append(stats_output)
        log.write(stats_output)
        time.sleep(1)  # Sleep for a short interval

# Parse the log file and store data in a CSV file
max_cpu = 0.0
cpu_usage = []

with open(log_file, "r") as log, open(csv_file, "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    header_written = False

    for line in log:
        cleaned_line = remove_control_characters(line)
        if "CONTAINER ID" in cleaned_line and not header_written:
            header = ['CONTAINER ID', 'NAME', 'CPU %', 'MEM USAGE / LIMIT', 'NET I/O', 'BLOCK I/O', 'PIDS']
            csv_writer.writerow(header)
            header_written = True
        elif header_written and "CONTAINER ID" not in cleaned_line:
            columns = cleaned_line.split()
            if columns:
                csv_writer.writerow(columns[:7])
                try:
                    current_cpu = float(columns[2].rstrip('%'))
                    cpu_usage.append(columns[:7])  # Append the entire row to cpu_usage
                    if current_cpu > max_cpu:
                        max_cpu = current_cpu
                except ValueError:
                    pass

# Prepare final output
output = {
    "command": [ f"docker exec -d {container_name} sh -c 'apt-get update && apt-get install stress -y && stress --vm 2 --vm-bytes 2G --timeout 30'",
                 f"docker stats --no-stream {container_name}" ],
    "result": result,
    "success": True
}

print(json.dumps(output))
