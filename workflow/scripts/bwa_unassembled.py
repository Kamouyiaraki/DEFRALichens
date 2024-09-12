import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor
import logging
import re
import pathlib

# Ensure the logs directory exists
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

#Create a temporary assembly directory 
tmp_dir = "./assemblies/temp"
os.makedirs(tmp_dir, exist_ok=True)

# Set up logging to both stdout and a file
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(os.path.join(log_dir, "unassembled_reads.log"))

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
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

    results = {id: str(files[0]) for id in ids
               if (files := sorted(dir_path.glob(f"*{id}*_*unmapped_reads.f*q")))}

    missing_ids = ids - results.keys()
    if missing_ids:
        logger.warning(f"No reads found for IDs: {', '.join(missing_ids)}")

    return results

def run_subprocess(command, id, log_prefix):
    result = subprocess.run(command, capture_output=True, text=True)
    with open(f"{log_dir}/{id}_{log_prefix}_output.log", "w") as f_out, open(f"{log_dir}/{id}_{log_prefix}_error.log", "w") as f_err:
        f_out.write(result.stdout)
        f_err.write(result.stderr)

    if result.returncode != 0:
        logger.error(f"Error running {log_prefix} for {id}. See log for details.")
        raise subprocess.CalledProcessError(result.returncode, command)

def run_bwa_unassembled(id, input_file):
    assembly_fasta = pathlib.Path(f"./assemblies/{id}_megahit/final.contigs.fa")
    sam_file = pathlib.Path(f"./assemblies/temp/{id}_assembly_mapped.sam")
    bam_file = pathlib.Path(f"./assemblies/temp/{id}_assembly_mapped.bam")
    sorted_bam_file = pathlib.Path(f"./assemblies/temp/{id}_assembly_mapped_sorted.bam")
    unassembled_fasta = pathlib.Path(f"./assemblies/{id}_megahit/unassembled.fa")
    assembly_stats_file = pathlib.Path(f"./assemblies/{id}_megahit/assembly_stats.txt"

    if assembly_fasta.is_file():
        try:
            # Indexing Assembly
            logger.info(f"Indexing Assembly for {id}")
            subprocess.run(["bwa", "index", str(assembly_fasta)], check=True)

            # Running BWA MEM
            with open(sam_file, "w") as sam_out:
                logger.info(f"Running BWA MEM for {id}")
                subprocess.run(["bwa", "mem", "-M", "-t", "8", assembly_fasta, input_file], stdout=sam_out, check=True)

            # Convert SAM to BAM
            logger.info(f"Converting SAM to BAM for {id}")
            subprocess.run(["../../../users/marik2/apps/samtools-1.20/samtools", "view", "-b", "-S", sam_file, "-o", bam_file], check=True)

            # Sort BAM file
            logger.info(f"Sorting BAM file for {id}")
            subprocess.run(["../../../users/marik2/apps/samtools-1.20/samtools", "sort", "-o", sorted_bam_file, bam_file], check=True)

            # Extract unassembled reads
            logger.info(f"Extracting unassembled reads for {id}")
            with unassembled_fasta.open("w") as fastq_out:
                subprocess.run(["../../../users/marik2/apps/samtools-1.20/samtools", "fasta", "-f", "4", sorted_bam_file], stdout=fastq_out, check=True)

            # Generate statistics
            logger.info(f"Generating statistics for {id}")
            subprocess.run(["../../../users/marik2/apps/samtools-1.20/samtools", "stats", sorted_bam_file], stdout=open(assembly_stats_file, "w"), check=True)

            logger.info(f"Successfully processed {id} for unassembled sequences")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error during processing of {id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during processing of {id}: {e}")

    else:
        logger.info(f"No assembly found for {id}, proceeding with unassembled reads")
        subprocess.run(["cp", input_file, f"./assemblies/{id}_megahit/unassembled.fa"], check=True)

def main(seq_dir, max_workers=6):
    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    files = find_files(seq_dir, ids)
    if not files:
        logger.error("No files found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for id, file_path in files.items():
            future_bwa = executor.submit(run_bwa_unassembled, id, file_path)
            futures.append(future_bwa)

        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing a file: {e}")

if __name__ == "__main__":
    seq_dir = './bbduk_processed/'

    main(seq_dir, max_workers=6)
