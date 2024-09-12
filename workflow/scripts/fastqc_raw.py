import os
import sys
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor
import logging

# Ensure the logs directory exists
log_dir = os.path.dirname("./logs")
os.makedirs(log_dir, exist_ok=True)  # Creates the directory if it doesn't exist

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("./logs/fastqc_raw.log"))
logger.setLevel(logging.INFO)

# Function to run FastQC
def run_fastqc(ids, r1_path, r2_path):
    # Create output directory for each sample
    os.makedirs(ids, exist_ok=True)

    # Define the FastQC command with output directed to the appropriate directory
    command = ["fastqc", "-o", ids, r1_path, r2_path]

    # Run the command and capture the output and errors
    result = subprocess.run(command, capture_output=True, text=True)

    # Write stdout and stderr to log files
    with open(f"./logs/{ids}_fastqc_raw_output.log", "w") as f_out:
        f_out.write(result.stdout)
    with open(f"./logs/{ids}_fastqc_raw_error.log", "w") as f_err:
        f_err.write(result.stderr)

    print(f"Processed {ids}")

def main(csv_file, max_workers=4):
    # Read the CSV file
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Use ThreadPoolExecutor to run FastQC commands in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for row in reader:
                ids = row['ID'].strip()        # Updated to match your column name
                r1_path = row['forward'].strip()  # Updated to match your column name
                r2_path = row['reverse'].strip()  # Updated to match your column name

                # Submit the FastQC job to the executor
                futures.append(executor.submit(run_fastqc, ids, r1_path, r2_path))

            # Wait for all futures to complete
            for future in futures:
                future.result()  # To re-raise exceptions if any occurred

if __name__ == "__main__":
    # Specify the CSV file to be read
    csv_file = 'samples_out.csv'

    # Run the main function with parallelism
    main(csv_file, max_workers=4)
