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
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for more detailed logs

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    file_handler = logging.FileHandler(os.path.join(log_dir, "check_assembly.log"))
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

def run_metaspades(id, assembly_dir):
    output_dir = f"{assembly_dir}/{id}_metaspades"

    cmd = [
        "metaspades",
        "--continue", 
        "-o", output_dir
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"MetaSPAdes succeeded for {id}.")
        else:
            logger.error(f"MetaSPAdes failed for {id}. Error: {result.stderr}")
    except Exception as e:
        logger.error(f"MetaSPAdes execution error for {id}: {e}")


def check_assembly(id, assembly_dir):
    contigs_file = Path(f"{assembly_dir}/{id}_metaspades/scaffolds.fasta")

    # Check if contigs file exists
    if contigs_file.is_file():
        logger.info(f"Contigs file already exists for {id}.")
    else:
        logger.info(f"Final contigs file missing for {id}. Running MetaSPAdes.")
        run_metaspades(id, assembly_dir)

        # Check again if contigs file exists after running MetaSPAdes
        if contigs_file.is_file():
            logger.info(f"Contigs file successfully created for {id}.")
        else:
            logger.error(f"MetaSPAdesfailed for {id} and cannot continue further.")

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

    main(seq_dir, assembly_dir, max_workers=2)
