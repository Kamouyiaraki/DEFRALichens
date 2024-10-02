import os
import sys
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import pathlib

# Ensure necessary directories exist
log_dir = "./logs"
assembly_dir = "./assemblies"
os.makedirs(log_dir, exist_ok=True)
os.makedirs(assembly_dir, exist_ok=True)

# Set up logging to both stdout and a file
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    file_handler = logging.FileHandler(os.path.join(log_dir, "idba-ud_processed.log"))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def get_ids(seq_dir):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return set()

    logger.info(f"Scanning directory: {dir_path}")
    ids = {match.group(1) for file in dir_path.glob("*_unmapped_reads.*f*q") 
           if (match := re.match(r'(.+?)_unmapped_reads', file.stem))}

    if ids:
        logger.info(f"Found IDs: {', '.join(ids)}")
    else:
        logger.warning("No IDs found.")
    
    return ids

def run_fq2fa(id, seq_dir):
    merged_file = f"{seq_dir}/{id}_unmapped_reads.fastq"  # Corrected merged file path
    output_file = f"{seq_dir}/{id}_unmapped_reads.fas"

    command = ["../../../users/marik2/apps/idba-1.1.3/bin/fq2fa", merged_file, output_file]

    try:
        with open(output_file, "w") as out_fh:
            result = subprocess.run(command, stdout=out_fh, stderr=subprocess.PIPE, text=True, check=True)

        with open(f"{log_dir}/{id}_fastq2fasta_error.log", "w") as f_err:
            f_err.write(result.stderr)

        logger.info(f"Processed {id} from FASTQ to FASTA")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing {id}: {e.stderr}")
    except IOError as e:
        logger.error(f"File error for {id}: {str(e)}")

    return output_file

def run_idba_ud(id, fasta_file):
    logger.info(f"Starting idba-ud for {id}")

    command = [
        "../../../users/marik2/apps/idba-1.1.3/bin/idba_ud",
        "-r", fasta_file,
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
        with open(f"{log_dir}/{id}_IDBA-UD_processed_output.log", "w") as f_out:
            f_out.write(result.stdout)
        with open(f"{log_dir}/{id}_IDBA-UD_processed_error.log", "w") as f_err:
            f_err.write(result.stderr)
    except IOError as e:
        logger.error(f"Error writing logs for {id}: {e}")

    if result.returncode == 0:
        logger.info(f"Successfully processed {id}")
    else:
        logger.error(f"IDBA-UD processing failed for {id} with return code {result.returncode}")

def main(seq_dir, max_workers=4):
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        for id in ids:
            fasta_file = f"{seq_dir}/{id}_unmapped_reads.fas"

            # Check if FASTA already exists, if not, convert FASTQ to FASTA
            if not os.path.exists(fasta_file):
                futures[executor.submit(run_fq2fa, id, seq_dir)] = id

        # Wait for all FASTQ-to-FASTA conversions to complete before running idba-ud
        for future in as_completed(futures):
            id = futures[future]
            try:
                fasta_file = future.result()  # Get the resulting FASTA file
                # Submit idba_ud for this ID
                executor.submit(run_idba_ud, id, fasta_file)
            except Exception as e:
                logger.error(f"FASTQ to FASTA conversion failed for {id}: {e}")

if __name__ == "__main__":
    seq_dir = './decontaminated_reads/'
    main(seq_dir, max_workers=2)
