import os
import sys
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Ensure the logs directory exists
log_dir = Path("./logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    file_handler = logging.FileHandler(log_dir / "check_and_cat_assembly.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def get_ids(seq_dir):
    dir_path = Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return set()

    logger.info(f"Scanning directory: {dir_path}")
    ids = {match.group(1) for file in dir_path.glob("*_processed.fq") 
           if (match := re.match(r'(.+?)_processed\.fq$', file.name))}

    if not ids:
        logger.warning("No IDs found.")
    else:
        logger.info(f"Found IDs: {', '.join(ids)}")

    return ids

def concatenate_files(id, fastp_dir):
    processed_file = Path(fastp_dir) / f"{id}_processed.fq"
    unmerged_file1 = Path(fastp_dir) / f"{id}_unmerged_1.fq"
    unmerged_file2 = Path(fastp_dir) / f"{id}_unmerged_2.fq"
    output_file_path = Path(fastp_dir) / f"{id}_all_processed_reads.fq"

    try:
        with output_file_path.open('w') as output_file:
            for input_file in [processed_file, unmerged_file1, unmerged_file2]:
                if input_file.exists():
                    logger.info(f"Including {input_file} in {output_file_path.name}")
                    with input_file.open('r') as f:
                        for line in f:
                            output_file.write(line)
                else:
                    logger.warning(f"File {input_file} not found. Skipping.")
        logger.info(f"Successfully concatenated files for {id}.")
    except Exception as e:
        logger.error(f"Error concatenating files for {id}: {e}", exc_info=True)

def main(seq_dir, max_workers=4):
    fastp_dir = Path(seq_dir)
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(concatenate_files, id, fastp_dir): id for id in ids}

        for future in as_completed(futures):
            id = futures[future]
            try:
                future.result()  # Trigger exception handling for any errors
            except Exception as e:
                logger.error(f"Failed to process sample {id}: {e}. Continuing with next sample.")

if __name__ == "__main__":
    seq_dir = './fastp_processed'
    main(seq_dir, max_workers=4)
