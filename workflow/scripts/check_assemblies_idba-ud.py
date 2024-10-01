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

def check_assembly(id, assembly_dir):
    contigs_file = Path(f"{assembly_dir}/{id}_idba_ud/contig.fa")

    # Check if contigs file exists
    if contigs_file.is_file():
        logger.info(f"Contigs file already exists for {id}.")
    else:
        logger.info(f"Final contigs file missing for {id}. Checking for scaffolds.")
        scaffolds_file = Path(f"{assembly_dir}/{id}_idba_ud/scaffold.fa")
        
        # Check again if contigs file exists after running MEGAHIT
        if scaffolds_file.is_file():
            logger.info(f"Scaffolds file successfully found for {id}.")
        else:
            logger.error(f"IDBA-UD failed for {id} and cannot continue further, please consider a different assembler.")

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
