import os
import sys
import subprocess
import logging
import pathlib
import re
from pathlib import Path

# Ensure the logs directory exists
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Set up logging to both stdout and a file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    file_handler = logging.FileHandler(Path(log_dir) / "check_assembly.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def get_ids(seq_dir):
    dir_path = Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return set()

    logger.info(f"Scanning directory: {dir_path}")
    ids = {match.group(1) for file in dir_path.glob("*_decontaminated_reads.*") 
           if (match := re.match(r'(.+?)_decontaminated_reads', file.stem))}
    
    if not ids:
        logger.warning("No IDs found.")
    else:
        logger.info(f"Found IDs: {', '.join(ids)}")
    
    return ids

def run_idba_ud(id, assembly_dir):
    logger.info(f"Starting idba-ud for {id}")
	
    command = [
        "idba_ud",
        "-r", f"{id}_decontaminated_reads.fas",
        "--num_threads", "1",
        "-o", f"{assembly_dir}/{id}_idba_ud/"
    ]

    logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"IDBA-UD completed for {id}")
    except subprocess.CalledProcessError as e:
        logger.error(f"IDBA-UD failed for {id}: {e.stderr}")
        return

    try:
        with open(Path(log_dir) / f"{id}_IDBA-UD_processed_output.log", "w") as f_out:
            f_out.write(result.stdout)
        with open(Path(log_dir) / f"{id}_IDBA-UD_processed_error.log", "w") as f_err:
            f_err.write(result.stderr)
    except IOError as e:
        logger.error(f"Error writing logs for {id}: {e}")

    if result.returncode == 0:
        logger.info(f"Successfully processed {id}")
    else:
        logger.error(f"IDBA-UD processing failed for {id} with return code {result.returncode}")

def check_assembly(id, assembly_dir):
    contigs_file = Path(assembly_dir) / f"{id}_idba_ud/contig.fa"

    # Check if contigs file exists
    if contigs_file.is_file():
        logger.info(f"Contigs file already exists for {id}.")
    else:
        logger.info(f"Final contigs file missing for {id}. Checking for scaffolds.")
        scaffolds_file = Path(assembly_dir) / f"{id}_idba_ud/scaffold.fa"
        
        if scaffolds_file.is_file():
            logger.info(f"Scaffolds file successfully found for {id}.")
        else:
            logger.error(f"IDBA-UD failed for {id} previously. Trying again for {id}.")
            run_idba_ud(id, assembly_dir)

def main(seq_dir, assembly_dir, max_workers=4):
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    for id in ids:
        check_assembly(id, assembly_dir)

if __name__ == "__main__":
    seq_dir = './decontaminated_reads/'
    assembly_dir = './assemblies'

    main(seq_dir, assembly_dir, max_workers=4)
