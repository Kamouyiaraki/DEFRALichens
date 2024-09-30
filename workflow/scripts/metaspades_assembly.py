import os
import sys
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pathlib

# Ensure the logs directory exists
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Ensure assembly directory exists
assembly_dir = "./assemblies"
os.makedirs(assembly_dir, exist_ok=True)

# Set up logging to both stdout and a file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    file_handler = logging.FileHandler(os.path.join(log_dir, "metaspades_processed.log"))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def get_ids(seq_dir):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return set()

    logger.info(f"Scanning directory: {dir_path}")
    ids = {match.group(1) for file in dir_path.glob("*_unmapped_reads.*") 
           if (match := re.match(r'(.+?)_unmapped_reads', file.stem))}

    if not ids:
        logger.warning("No IDs found.")
    else:
        logger.info(f"Found IDs: {', '.join(ids)}")
    
    return ids

def run_metaspades(id, seq_dir, unmerged_dir):
    logger.info(f"Starting MetaSPAdes for {id}")

    # Construct paths based on the ID
    merged_file = f"{seq_dir}/{id}_unmapped_reads.fastq"  # Corrected merged file path
    unmerged1_file = f"{unmerged_dir}/{id}_unmerged_1.fq"  # Corrected unmerged file 1 path
    unmerged2_file = f"{unmerged_dir}/{id}_unmerged_2.fq"  # Corrected unmerged file 2 path

    # Debug: Print the constructed paths
    logger.debug(f"Looking for merged file: {merged_file}")
    logger.debug(f"Looking for unmerged file 1: {unmerged1_file}")
    logger.debug(f"Looking for unmerged file 2: {unmerged2_file}")

    # Check if the necessary files exist
    if os.path.exists(merged_file) and os.path.exists(unmerged1_file) and os.path.exists(unmerged2_file):
        command = [
            "python3.8", 
            "../../../users/marik2/apps/SPAdes-4.0.0-Linux/bin/metaspades.py", 
            "--merged", merged_file, "-1", unmerged1_file, "-2", unmerged2_file, 
            "--phred-offset", "33",
            "-o", f"{assembly_dir}/{id}_metaspades/"
        ]

        logger.debug(f"Running command: {' '.join(command)}")

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logger.info(f"MetaSPAdes completed for {id}")
            
            # Save the output and error logs
            with open(f"{log_dir}/{id}_MetaSPAdes_processed_output.log", "w") as f_out:
                f_out.write(result.stdout)
            with open(f"{log_dir}/{id}_MetaSPAdes_processed_error.log", "w") as f_err:
                f_err.write(result.stderr)

        except subprocess.CalledProcessError as e:
            logger.error(f"MetaSPAdes failed for {id}: {e.stderr}")
        except IOError as io_err:
            logger.error(f"Error writing logs for {id}: {io_err}")

        if result.returncode == 0:
            logger.info(f"Successfully processed {id}")
        else:
            logger.error(f"MetaSPAdes processing failed for {id} with return code {result.returncode}")
    else:
        logger.error(f"Required files for {id} are missing. Skipping...")
        logger.debug(f"Expected merged file: {merged_file}")
        logger.debug(f"Expected unmerged file 1: {unmerged1_file}")
        logger.debug(f"Expected unmerged file 2: {unmerged2_file}")


def main(seq_dir, unmerged_dir, max_workers=4):
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Pass both `seq_dir` and `unmerged_dir` to `run_metaspades`
        futures = {executor.submit(run_metaspades, id, seq_dir, unmerged_dir): id for id in ids}

        for future in as_completed(futures):
            id = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"MetaSPAdes processing failed for {id}: {e}")

if __name__ == "__main__":
    seq_dir = './decontaminated_reads'
    unmerged_dir = './fastp_processed'

    # Now call the function with the correct number of arguments
    main(seq_dir, unmerged_dir, max_workers=2)
