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

# Create a temporary assembly directory
assembly_dir = './assemblies'
tmp_dir = pathlib.Path(f"{assembly_dir}/temp")
tmp_dir.mkdir(exist_ok=True)

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(os.path.join(log_dir, "unassembled_reads.log"))
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

def get_ids_and_files(seq_dir):
    dir_path = pathlib.Path(seq_dir)
    if not dir_path.is_dir():
        logger.error(f"Directory {seq_dir} does not exist.")
        return {}

    # Log available files in the directory
    logger.info(f"Scanning directory: {dir_path}")

    # Look for fastq or fq files and extract IDs from filenames
    results = {re.match(r'(.+?)_.*', file.stem).group(1): str(file)
               for file in dir_path.glob("*decontaminated_reads.f*q*")}

    if not results:
        logger.error(f"No reads found in {seq_dir}")
    else:
        logger.info(f"Found IDs and files: {results}")

    return results

def run_subprocess(command, id, log_prefix):
    result = subprocess.run(command, capture_output=True, text=True)
    with open(f"{log_dir}/{id}_{log_prefix}_output.log", "w") as f_out, \
         open(f"{log_dir}/{id}_{log_prefix}_error.log", "w") as f_err:
        f_out.write(result.stdout)
        f_err.write(result.stderr)

    if result.returncode != 0:
        logger.error(f"Error running {log_prefix} for {id}. See log for details.")
        raise subprocess.CalledProcessError(result.returncode, command)

def concatenate_files(id, assembler):
    contigs_file = find_assembly_file(assembler, id)
    unassembled_file = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/unassembled.fa")
    final_assembly_file = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/assembly.fa")

    if contigs_file.exists() and unassembled_file.exists():
        try:
            with final_assembly_file.open('w') as output_file:
                for input_file in [contigs_file, unassembled_file]:
                    output_file.write(input_file.read_text())
            logger.info(f"Successfully concatenated files for {id}.")
        except Exception as e:
            logger.error(f"Error concatenating files for {id}: {e}")
    else:
        logger.error(f"Missing contigs or unassembled file for {id}.")

import pathlib

def find_assembly_file(assembler, id):
    assembly_files = {
        "megahit": "final.contigs.fa",
        "metaspades": "scaffolds.fasta",
        "idba_ud": ["contig.fa", "scaffold.fa"]
    }

    # Check for idba-ud files
    if assembler == "idba_ud":
        file_name1 = assembly_files["idba_ud"][0]
        file_name2 = assembly_files["idba_ud"][1]

        # Construct paths for both file options
        file_path1 = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/{file_name1}")
        file_path2 = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/{file_name2}")

        # Check if the first file exists
        if file_path1.is_file():
            return file_path1

        # Check if the second file exists if the first doesn't
        elif file_path2.is_file():
            return file_path2

        # Log an error if neither file exists
        else:
            logger.error(f"Missing {assembler} {file_path1} or {file_path2} file for {id}.")
            return None

    # For non-idba-ud assemblers, return the appropriate file
    else:
        file_name = assembly_files.get(assembler)
        if file_name:
            file_path = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/{file_name}")
            if file_path.is_file():
                return file_path
            else:
                logger.error(f"Missing {assembler} assembly file for {id}.")
                return None
        else:
            logger.error(f"Unknown assembler: {assembler}")
            return None


def run_bwa_unassembled(id, assembler, input_file):
    logger.info(f"Processing with assembler: {assembler}")

    assembly_fasta = find_assembly_file(assembler, id)
    sam_file = pathlib.Path(f"{assembly_dir}/temp/{id}_assembly_mapped.sam")
    bam_file = pathlib.Path(f"{assembly_dir}/temp/{id}_assembly_mapped.bam")
    sorted_bam_file = pathlib.Path(f"{assembly_dir}/temp/{id}_assembly_mapped_sorted.bam")
    unassembled_fasta = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/unassembled.fa")
    assembly_stats_file = pathlib.Path(f"{assembly_dir}/{id}_{assembler}/assembly_stats.txt")

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
            subprocess.run(["samtools", "view", "-b", "-S", sam_file, "-o", bam_file], check=True)

            # Sort BAM file
            logger.info(f"Sorting BAM file for {id}")
            subprocess.run(["samtools", "sort", "-o", sorted_bam_file, bam_file], check=True)

            # Extract unassembled reads
            logger.info(f"Extracting unassembled reads for {id}")
            with unassembled_fasta.open("w") as fastq_out:
                subprocess.run(["samtools", "fasta", "-f", "4", sorted_bam_file], stdout=fastq_out, check=True)

            # Generate statistics
            logger.info(f"Generating statistics for {id}")
            subprocess.run(["samtools", "stats", sorted_bam_file], stdout=open(assembly_stats_file, "w"), check=True)

            logger.info(f"Successfully processed {id} for unassembled sequences")

        except subprocess.CalledProcessError as e:
            logger.error(f"Error during processing of {id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during processing of {id}: {e}")

    else:
        logger.info(f"No assembly found for {id}, proceeding with unassembled reads")
        subprocess.run(["cp", input_file, f"./assemblies/{id}_megahit/unassembled.fa"], check=True)

def main(seq_dir, assembler, max_workers=6):
    """Main function to process all IDs found in the sequence directory."""
    id_to_file = get_ids_and_files(seq_dir)
    if not id_to_file:
        logger.error("No input files found. Exiting.")
        return

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_bwa_unassembled, id, assembler, input_file) for id, input_file in id_to_file.items()]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error processing a file: {e}")

    # After processing all files, concatenate the results
    for id in id_to_file.keys():
        try:
            concatenate_files(id, assembler)
        except Exception as e:
            logger.error(f"Error concatenating files for {id}: {e}")

if __name__ == "__main__":
    seq_dir = './decontaminated_reads/'
    assembler = 'metaspades'

    main(seq_dir, assembler, max_workers=6)
