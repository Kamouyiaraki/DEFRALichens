import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import re
import pathlib

# Ensure the logs directory exists
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Set up logging to both stdout and a file
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(os.path.join(log_dir, "decontam_processed.log"))

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
    ids = {match.group(1) for file in dir_path.glob("*processed.f*q")
           if (match := re.match(r'(.+?)_processed', file.stem))}

    logger.info(f"Found IDs: {', '.join(ids)}")
    return ids

def find_files(seq_dir, ids):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return {}

    results = {id: str(files[0]) for id in ids
               if (files := sorted(dir_path.glob(f"*{id}*processed.f*q")))}

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

def run_bbduk(id, file_path, output_dir, temp_dir):
    output_file = os.path.join(temp_dir, f"{id}_nophiX.fq")
    command = [
        "../../../users/marik2/apps/bbmap/bbduk.sh",
        f"in={file_path}",
        f"out={output_file}",
        "ref=./ref/NC_001422.1_escherichia_phage_phiX174.fasta",
        "k=31",
        "hdist=1",
        "-Xmx2g",
        f"stats={output_dir}/{id}_nophiX_stats.txt"
    ]
    run_subprocess(command, id, "bbduk")
    logger.info(f"Processed {id} for PhiX contamination")
    return output_file  # Return the processed file path

def run_bwa_mem_and_samtools(id, input_file, output_dir, temp_dir):
    genome_fasta = "./ref/GCF_000001405.40_GRCh38.p14_genomic.fna"
    bam_file = f"{temp_dir}/{id}_output.bam"
    sorted_bam_file = f"{temp_dir}/{id}_output_sorted.bam"
    unmapped_fastq = f"{output_dir}/{id}_decontaminated_reads.fastq"
    stats_file = f"{output_dir}/{id}_human_mapping_idxstats.txt"

    try:
        # Run BWA MEM to align the reads and pipe directly to samtools view
        logger.info(f"Running BWA MEM and SAMtools for {id}")
        bwa_cmd = ["bwa", "mem", "-M", "-t", "8", genome_fasta, input_file]
        samtools_view_cmd = ["../../../users/marik2/apps/samtools-1.20/samtools", "view", "-b", "-o", bam_file]
        with open(bam_file, "w") as bam_out:
            p1 = subprocess.Popen(bwa_cmd, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(samtools_view_cmd, stdin=p1.stdout, stdout=bam_out)
            p1.stdout.close()
            p2.communicate()

        # Sort BAM file
        logger.info(f"Sorting BAM file for {id}")
        subprocess.run(["../../../users/marik2/apps/samtools-1.20/samtools", "sort", "-o", sorted_bam_file, bam_file], check=True)

        # Extract unmapped reads and output as FASTQ
        logger.info(f"Extracting unmapped reads for {id}")
        with open(unmapped_fastq, "w") as fastq_out:
            p1 = subprocess.Popen(["../../../users/marik2/apps/samtools-1.20/samtools", "view", "-f4", sorted_bam_file], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["../../../users/marik2/apps/samtools-1.20/samtools", "fastq"], stdin=p1.stdout, stdout=fastq_out)
            p1.stdout.close()
            p2.communicate()

        # Generate statistics
        logger.info(f"Generating statistics for {id}")
        subprocess.run(["../../../users/marik2/apps/samtools-1.20/samtools", "idxstat", sorted_bam_file], stdout=open(stats_file, "w"), check=True)

        logger.info(f"Successfully processed {id} for genome alignment and stats generation")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error during processing of {id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during processing of {id}: {e}")

def main(seq_dir, output_dir, max_workers=None):
    # Dynamically set number of workers to CPU count if not provided
    max_workers = max_workers or os.cpu_count()

    temp_dir = os.path.join(output_dir, "temp_dir")
    os.makedirs(temp_dir, exist_ok=True)

    ids = get_ids(seq_dir)
    if not ids:
        logger.error("No IDs found. Exiting.")
        return

    files = find_files(seq_dir, ids)
    if not files:
        logger.error("No files found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_bbduk, id, file_path, output_dir, temp_dir) for id, file_path in files.items()]

        for future in as_completed(futures):
            try:
                result = future.result()
                id = result.split("/")[-1].split("_")[0]  # Extract ID from result
                executor.submit(run_bwa_mem_and_samtools, id, result, output_dir, temp_dir)
            except Exception as e:
                logger.error(f"Error processing a file: {e}")

if __name__ == "__main__":
    seq_dir = './fastp_processed/'
    output_dir = './decontaminated_reads'

    main(seq_dir, output_dir)