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

# Set up logging to both stdout and a file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    file_handler = logging.FileHandler(os.path.join(log_dir, "fastqc_processed.log"))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def get_ids(seq_dir):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return set()

    logger.info(f"Scanning directory: {dir_path}")
    ids = {match.group(1) for file in dir_path.glob("*_processed.f*q") 
           if (match := re.match(r'(.+?)_processed', file.stem))}
    
    if not ids:
        logger.warning("No IDs found.")
    else:
        logger.info(f"Found IDs: {', '.join(ids)}")
    
    return ids

def find_files(seq_dir, ids):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return {}

    results = {}
    for id in ids:
        files = sorted(dir_path.glob(f"*{id}*_processed.f*q"))

        if not files:
            logger.warning(f"ID {id}: No reads found.")
        elif len(files) == 1:
            logger.info(f"ID {id}: Single-read or merged file.")
            results[id] = (str(files[0]), None)
        elif len(files) == 2:
            logger.info(f"ID {id}: Paired-end files.")
            results[id] = tuple(map(str, files))
        else:
            logger.warning(f"ID {id}: Unexpected number of files found.")

    return results

def run_fastqc(id, r1_path, r2_path=None):
    logger.info(f"Starting FastQC for {id}")
    os.makedirs(id, exist_ok=True)

    command = ["fastqc", "-o", id, "-t", "2", r1_path]  # Reduced to 2 threads
    if r2_path:
        command.append(r2_path)

    logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"FastQC completed for {id}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FastQC failed for {id}: {e.stderr}")

    with open(f"{log_dir}/{id}_fastqc_processed_output.log", "w") as f_out:
        f_out.write(result.stdout)
    with open(f"{log_dir}/{id}_fastqc_processed_error.log", "w") as f_err:
        f_err.write(result.stderr)

    if result.returncode == 0:
        logger.info(f"Successfully processed {id}")
    else:
        logger.error(f"FastQC processing failed for {id} with return code {result.returncode}")

def main(seq_dir, max_workers=4):
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    results = find_files(seq_dir, ids)
    if not results:
        logger.error("No files found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_fastqc, id, *paths): id for id, paths in results.items()}

        for future in as_completed(futures):
            id = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"FastQC processing failed for {id}: {e}")

if __name__ == "__main__":
    seq_dir = './fastp_processed/'
    main(seq_dir, max_workers=2)
