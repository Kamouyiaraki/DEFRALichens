import subprocess
import os
import glob
import gzip
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_and_unzip_files(input_directory):
    """Find and unzip .fq.gz files in the specified directory."""
    logging.info("Finding and unzipping input files...")
    input_files = []

    # Debugging: Log matched files
    matched_files = glob.glob(os.path.join(input_directory, "Undetermined*.fq.gz"), recursive=False)
    logging.info(f"Matched files: {matched_files}")

    for file in matched_files:
        # Validate filename explicitly for expected patterns
        if not file.endswith("_1.fq.gz") and not file.endswith("_2.fq.gz"):
            logging.warning(f"Skipping unexpected file: {file}")
            continue

        unzipped_file = file[:-3]  # Remove .gz extension
        with gzip.open(file, 'rb') as f_in:
            with open(unzipped_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        input_files.append(unzipped_file)

    if len(input_files) < 2:
        logging.error("Insufficient input files found in the directory.")
        raise ValueError("Insufficient input files found in the directory.")

    # Sort input files to maintain consistent pairing
    input_files.sort()
    logging.info(f"Found and unzipped files: {input_files}")
    return input_files

def pair_input_files(input_files):
    """Pair _1 and _2 files for Cutadapt processing."""
    logging.info("Pairing input files...")
    paired_files = []
    file_dict = {}

    # Group files by common prefix (ignoring the _1/_2 suffix)
    for file in input_files:
        prefix = file.rsplit('_', 1)[0]  # Remove the _1 or _2 suffix
        if prefix not in file_dict:
            file_dict[prefix] = []
        file_dict[prefix].append(file)

    # Check for complete pairs and sort _1 before _2
    for prefix, files in file_dict.items():
        if len(files) != 2:
            logging.error(f"Incomplete pair found for prefix: {prefix}")
            raise ValueError(f"Incomplete pair found for prefix: {prefix}")
        files.sort(key=lambda x: '_1' in x)  # Ensure _1 comes before _2
        paired_files.append(files)

    logging.info(f"Paired files: {paired_files}")
    return paired_files

def run_cutadapt(input_files, output_name, cutadapt_error_rate, i7_barcodes, i5_barcodes):
    """Run the cutadapt command."""
    logging.info(f"Running cutadapt for pair: {input_files}...")
    cutadapt_command = [
        "cutadapt",
        "-e", str(cutadapt_error_rate),
        "--no-indels",
        "-g", f"^file:{i5_barcodes}",
        "-G", f"^file:{i7_barcodes}",
        "-o", "{name}.1.fastq",
        "-p", "{name}.2.fastq",
        "--revcomp",
        "--action=none",
        *input_files,
        f"--json={output_name}.cutadapt.json"
    ]
    subprocess.run(cutadapt_command, check=True)
    logging.info(f"Cutadapt completed successfully for pair: {input_files}.")

def generate_seqkit_stats(stats_output):
    """Generate statistics with seqkit."""
    logging.info("Generating statistics with seqkit...")
    fastq_files = glob.glob("*.fastq")
    if not fastq_files:
        logging.error("No .fastq files found for statistics generation.")
        raise ValueError("No .fastq files found for statistics generation.")
    seqkit_command = ["seqkit", "stats", *fastq_files]
    with open(stats_output, "w") as stats_file:
        subprocess.run(seqkit_command, stdout=stats_file, check=True)
    logging.info(f"Statistics written to {stats_output}.")

def main(cutadapt_error_rate, i7_barcodes, i5_barcodes, input_directory):
    """Main workflow."""
    stats_output = "undetermined_cutadapt.stats"

    # Unzip and sort input files
    input_files = find_and_unzip_files(input_directory)

    # Pair files
    paired_files = pair_input_files(input_files)

    # Process each pair with Cutadapt in parallel
    max_workers = min(len(paired_files), os.cpu_count())  # Adjust workers based on number of pairs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for pair in paired_files:
            prefix = os.path.basename(pair[0]).rsplit('_', 1)[0]
            output_name = f"{prefix}_cutadapt"
            futures.append(executor.submit(run_cutadapt, pair, output_name, cutadapt_error_rate, i7_barcodes, i5_barcodes))

        # Wait for all tasks to complete
        for future in futures:
            future.result()

    # Generate statistics
    generate_seqkit_stats(stats_output)

if __name__ == "__main__":
    # Configuration variables
    cutadapt_error_rate = 1
    i7_barcodes = "i7_barcodes.fasta"
    i5_barcodes = "i5_barcodes.fasta"
    input_directory = "./raw_data/"  # Directory containing input files

    # Run the script
    main(cutadapt_error_rate, i7_barcodes, i5_barcodes, input_directory)
