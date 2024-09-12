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

    file_handler = logging.FileHandler(os.path.join(log_dir, "idba-ud_processed.log"))
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

def find_files(seq_dir, ids):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return {}

    results = {}
    for id in ids:
        files = sorted(dir_path.glob(f"*{id}*_*unmapped_reads*"))

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

def run_seqtk(file):
    # Extract the full filename without the extension for logging and output file naming
    file_id = pathlib.Path(file).stem
    
    # Define the output filename in the same directory as the input files
    output_file = pathlib.Path(file).parent / f"{file_id}.fa"
    
    try:
        # Open the output file
        with open(output_file, "w") as out_fh:
            # Run the SeqTK command and capture output and errors
            p1 = subprocess.run(
                ["seqtk", "seq", "-a", file],
                stdout=out_fh,  # Direct output to the file
                stderr=subprocess.PIPE,  # Capture errors
                text=True,
                check=True
            )
        
        # Write stderr to the error log file
        with open(f"./logs/{file_id}_fastq2fasta_error.log", "w") as f_err:
            f_err.write(p1.stderr)
        
        logger.info(f"Processed {file_id}")

    except Exception as e:
        logger.error(f"Error processing {file_id}: {str(e)}")

    return str(output_file)

def run_idba_ud(id, r1_path, r2_path=None):
    logger.info(f"Starting idba-ud for {id}")

    # Convert FASTQ to FASTA if needed
    if r1_path.endswith(".fastq") or r1_path.endswith(".fq"):
        logger.info(f"ID {id}: Converting R1 FASTQ to FASTA")
        r1_path = run_seqtk(r1_path)
    if r2_path and (r2_path.endswith(".fastq") or r2_path.endswith(".fq")):
        logger.info(f"ID {id}: Converting R2 FASTQ to FASTA")
        r2_path = run_seqtk(r2_path)

    command = ["../../../users/marik2/apps/idba-1.1.3/bin/idba_ud", "-r", r1_path, "-o", f"assemblies/{id}_idba_ud/"]
    if r2_path:
        command = ["../../../users/marik2/apps/idba-1.1.3/bin/idba_ud", "-r", r1_path, "-l", r2_path, "-o", f"assemblies/{id}_idba_ud/"]

    logger.debug(f"Running command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        logger.info(f"IDBA-UD completed for {id}")
    except subprocess.CalledProcessError as e:
        logger.error(f"IDBA-UD failed for {id}: {e.stderr}")

    with open(f"{log_dir}/{id}_IDBA-UD_processed_output.log", "w") as f_out:
        f_out.write(result.stdout)
    with open(f"{log_dir}/{id}_IDBA-UD_processed_error.log", "w") as f_err:
        f_err.write(result.stderr)

    if result.returncode == 0:
        logger.info(f"Successfully processed {id}")
    else:
        logger.error(f"IDBA-UD processing failed for {id} with return code {result.returncode}")

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
        futures = {executor.submit(run_idba_ud, id, *paths): id for id, paths in results.items()}

        for future in as_completed(futures):
            id = futures[future]
            try:
                future.result()
            except Exception as e:
                logger.error(f"IDBA-UD processing failed for {id}: {e}")

if __name__ == "__main__":
    seq_dir = './Test_dir/test_processed/'
    main(seq_dir, max_workers=2)
