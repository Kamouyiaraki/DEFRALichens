import pathlib
import csv
import logging
import pandas as pd
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def xlsx2csv(file_path):
    if not pathlib.Path(file_path).is_file():
        logger.error(f"Error: The file '{file_path}' does not exist.")
        return None

    xlsx_read = pd.read_excel(file_path)
    csv_name = pathlib.Path(file_path).stem
    dirname = os.path.dirname(file_path)
    csv_file_path = f"{dirname}/{csv_name}.csv"
    xlsx_read.to_csv(csv_file_path, index=None, header=True)
    logger.info(f"Successfully converted '{file_path}' to '{csv_file_path}'")
    return csv_file_path

def get_ids(file_path, column_name, delimiter=','):
    df = pd.read_csv(file_path, delimiter=delimiter)
    return df[column_name].tolist()

def seqkit_cleanup(project_dir, id, direction):
    command = [
        "seqkit", "sana",
        f"{project_dir}/{id}.{direction}.fastq",
        "-o",
        f"{project_dir}/{id}.{direction}.sanitised.fastq"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    with open(f"logs/{id}_seqkit_cleanup_output.log", "w") as f_out:
        f_out.write(result.stdout)
    with open(f"logs/{id}_seqkit_cleanup_error.log", "w") as f_err:
        f_err.write(result.stderr)

    logger.info(f"Sanitized {id} in {direction} direction")

def find_files(project_dir, ids):
    results = {}

    for id in ids:
        dir = pathlib.Path(project_dir)
        files = [str(file) for file in dir.glob(f"**/*{id}*.sanitised.fastq")]
        files = sorted(files)

        if len(files) == 0:
            logger.warning(f"ID {id}: No reads found.")
            continue

        if len(files) == 1:
            logger.warning(f"ID {id}: Your read files are unpaired.")
            continue

        if len(files) > 2:
            logger.warning(f"ID {id}: You have too many files with the same ID.")
            continue

        r1_path = files[0]
        r2_path = files[1]

        if r1_path and r2_path:
            results[id] = (r1_path, r2_path)

    return results

def seqkit_pair(id, r1_path, r2_path):
    command = [
        "seqkit", "pair",
        "-1", r1_path,
        "-2", r2_path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    with open(f"logs/{id}_seqkit_pair_output.log", "w") as f_out:
        f_out.write(result.stdout)
    with open(f"logs/{id}_seqkit_pair_error.log", "w") as f_err:
        f_err.write(result.stderr)

    logger.info(f"Paired reads for {id}")

def main(input_file, column_name, project_dir):
    logs_dir = pathlib.Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
# Step 1: Check and convert .xlsx to .csv if necessary
    if input_file.endswith(".xlsx"):
        input_file = xlsx2csv(input_file)
        if input_file is None:
            return

    # Step 2: Extract IDs from the CSV file
    ids = get_ids(input_file, column_name)

    # Step 3: Run seqkit_cleanup for each ID in both directions
    directions = ["1", "2"]
    cleanup_futures = []
    with ThreadPoolExecutor() as executor:
        for id in ids:
            for direction in directions:
                cleanup_futures.append(executor.submit(seqkit_cleanup, project_dir, id, direction))
        for future in as_completed(cleanup_futures):
            future.result()  # Ensure all cleanups are complete before proceeding

    # Step 4: Find paired files
    paired_files = find_files(project_dir, ids)

    # Step 5: Execute seqkit_pair on paired files
    pair_futures = []
    with ThreadPoolExecutor() as executor:
        for id, (r1_path, r2_path) in paired_files.items():
            pair_futures.append(executor.submit(seqkit_pair, id, r1_path, r2_path))
        for future in as_completed(pair_futures):
            future.result()  # Ensure all pairing is complete

if __name__ == "__main__":
    input_file = "./Batch_1_Lichen_Tracking_Sheet.csv"  # Replace with your input file path
    column_name = "Novogene_Sub_Library_Name"  # Replace with the column name containing IDs
    project_dir = "./demultiplexed"  # Replace with your project directory

    main(input_file, column_name, project_dir)
