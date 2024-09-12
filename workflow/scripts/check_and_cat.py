import os
import sys
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pathlib
from pathlib import Path

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

    file_handler = logging.FileHandler(os.path.join(log_dir, "check_and_cat_assembly.log"))
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

def concatenate_files(id):
    contigs_file = Path(f"{assembly_dir}/{id}_megahit/final.contigs.fa")
    unassembled_file = Path(f"{assembly_dir}/{id}_megahit/unassembled.fa")
    final_assembly_file = Path(f"{assembly_dir}/{id}_megahit/final_assembly.fa")

    try:
        if contigs_file.exists() and unassembled_file.exists():
            with final_assembly_file.open('w') as output_file:
                for input_file in [contigs_file, unassembled_file]:
                    output_file.write(input_file.read_text())
            logger.info(f"Successfully concatenated files for {id}.")
        else:
            logger.error(f"Missing contigs or unassembled file for {id}.")
    except Exception as e:
        logger.error(f"Error concatenating files for {id}: {e}")

def run_megahit(id):
    output_dir = f"{assembly_dir}/{id}_megahit"
    cmd = [
        "megahit",
        "-o", output_dir,
        "--continue"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"MEGAHIT succeeded for {id}.")
            concatenate_files(id)
        else:
            logger.error(f"MEGAHIT failed for {id}. Error: {result.stderr}")
    except Exception as e:
        logger.error(f"MEGAHIT execution error for {id}: {e}")

def run_check_and_cat(id):
    contigs_file = Path(f"{assembly_dir}/{id}_megahit/final.contigs.fa")

    # Check if contigs file exists
    if contigs_file.is_file():
        concatenate_files(id)
    else:
        logger.info(f"Final contigs file missing for {id}. Running MEGAHIT.")
        run_megahit(id)

        # Check again if contigs file exists after running MEGAHIT
        if contigs_file.is_file():
            concatenate_files(id)
        else:
            logger.error(f"MEGAHIT failed for {id} and cannot continue further.")
            # Continue to the next sample (handled by ThreadPoolExecutor in main)

def main(seq_dir, max_workers=4):
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_check_and_cat, id): id for id in ids}

        for future in as_completed(futures):
            id = futures[future]
            try:
                future.result()  # Trigger exception handling for any errors
            except Exception as e:
                logger.error(f"Failed to process sample {id}: {e}. Continuing with next sample.")

if __name__ == "__main__":
    seq_dir = './bbduk_processed/'
    assembly_dir = './assemblies'
    main(seq_dir, max_workers=2)
