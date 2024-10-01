import os
import sys
import subprocess
import re
import logging
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


def run_checks(assembler):
    # Initializing list of valid assemblers
    assembler_list = ["megahit", "metaspades", "idba-ud", "mhm2"]
    logger.info(f"Checking if {assembler} exists in the assembler list.")

    # Checking if the assembler exists in the list
    if assembler in assembler_list:
        logger.info(f"Valid assembler specified: {assembler}.")
        cmd = [
            "python3.8", f"check_assemblies_{assembler}.py"
        ]
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"Successfully ran the assembly check for {assembler}.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error while running assembly check for {assembler}: {e}")
    else:
        logger.error(f"Invalid assembler specified. Valid assemblers are: 'megahit', 'metaspades', 'idba-ud', 'mhm2'.")


def main(assembler):
    run_checks(assembler)


if __name__ == "__main__":
    assembler = 'idba-ud'  
    main(assembler)
