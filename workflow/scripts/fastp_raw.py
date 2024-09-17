import os
import sys
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor
import logging

# Ensure the logs directory exists
log_dir = os.path.dirname("./logs/")
os.makedirs(log_dir, exist_ok=True)  # Creates the directory if it doesn't exist

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("./logs/fastp_processing.log"))
logger.setLevel(logging.INFO)


# Function to run fastp
def run_fastp(ids, r1_path, r2_path, output_dir="fastp_processed"):
    # Create output directory for each sample
    os.makedirs(output_dir, exist_ok=True)

    # Define the fastp command with appropriate options
    command = [
        "../../../users/marik2/apps/bin/fastp", "-i", r1_path, "-I", r2_path,
        "--merge",
        "--merged_out", f"{output_dir}/{ids}_processed.fq",
	"--qualified_quality_phred=8",
        "--detect_adapter_for_pe",
        "--disable_length_filtering",
        "--trim_poly_g",
        "--correction",
        "--dedup",
        "--out1", f"{output_dir}/{ids}_unmerged_1.fq",
        "--out2", f"{output_dir}/{ids}_unmerged_2.fq",
        "--unpaired1", f"{output_dir}/{ids}_unpaired_1.fq",
        "--unpaired2", f"{output_dir}/{ids}_unpaired_2.fq",
        "--html", f"{output_dir}/{ids}_fastp.html",
        "--json", f"{output_dir}/{ids}_fastp.json",
        "--thread", "6"
    ]

    # Run the command and capture the output and errors
    result = subprocess.run(command, capture_output=True, text=True)

    # Write stdout and stderr to log files
    with open(f"logs/{ids}_fastp_output.log", "w") as f_out:
        f_out.write(result.stdout)
    with open(f"logs/{ids}_fastp_error.log", "w") as f_err:
        f_err.write(result.stderr)

    print(f"Processed {ids}")

def main(csv_file, max_workers=4):
    # Read the CSV file
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Use ThreadPoolExecutor to run fastp commands in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for row in reader:
                ids = row['ID'].strip()        # Adjust the column name to match your CSV
                r1_path = row['forward'].strip()  # Adjust the column name to match your CSV
                r2_path = row['reverse'].strip()  # Adjust the column name to match your CSV

                # Submit the fastp job to the executor
                futures.append(executor.submit(run_fastp, ids, r1_path, r2_path))

            # Wait for all futures to complete
            for future in futures:
                future.result()  # To re-raise exceptions if any occurred

    print("All samples processed!")

if __name__ == "__main__":
    # Specify the CSV file to be read
    csv_file = 'samples_out.csv'

    # Run the main function with parallelism
    #1 hour 10 minutes for 8 libraries with 4 workers. 
    main(csv_file, max_workers=4)
    
