import os
import sys
import pandas as pd
from pathlib import Path
import pathlib
import logging
import csv

# Ensure the logs directory exists
log_dir = os.path.dirname("./logs/Generate_Samples_Csv.log")
os.makedirs(log_dir, exist_ok=True)  # Creates the directory if it doesn't exist

# Configure logger
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("./logs/ids2csv.log"))
logger.setLevel(logging.INFO)

def xlsx2csv(file_path):
    # Check if the provided file exists
    if not Path(file_path).is_file():
        logger.error(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)

    # Read the Excel sheet
    xlsx_read = pd.read_excel(file_path)

    # Extract the name of the Excel file without the extension
    csv_name = pathlib.Path(file_path).stem
    dirname = os.path.dirname(file_path)

    # Convert the Excel sheet to a CSV file
    csv_file_path = f"{dirname}/{csv_name}.csv"
    xlsx_read.to_csv(csv_file_path, index=None, header=True)

    logger.info(f"Successfully converted '{file_path}' to '{csv_file_path}'")
    return csv_file_path


def get_ids(file_path, column_name, delimiter):
    # Reading in file
    df = pd.read_csv(file_path, delimiter=delimiter)
    ids = df[column_name]
    return ids


def find_files(project_dir, ids):
    # Initialize a dictionary to store the results
    results = {}

    # Loop through each id
    for id in ids:
        dir = pathlib.Path(project_dir)
        files = [str(file) for file in dir.glob(f"**/*{id}*.f*q.gz")]
        files = sorted(files)

        if len(files) == 0:
            logger.warning(f"ID {id}: No reads found.")
            continue

        if len(files) == 1:
            logger.warning("ID {id}: Your read files are unpaired.")
            continue

        if len(files) > 2:
            logger.warning("ID {id}: You have too many files with the same ID.")
            continue

        r1_path = files[0]
        r2_path = files[1]
        # this gives relative file path for full path: str(files[0].resolve())

        if r1_path and r2_path:
            results[id] = (r1_path, r2_path)

    return results


def write_to_csv(results, output_filename):
    with open(output_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "forward", "reverse"])
        for subfolder, (r1_path, r2_path) in results.items():
            writer.writerow([subfolder, r1_path, r2_path])


def main(project_dir, file_path, column_name, delimiter):
    # If the file is an XLSX, convert it to CSV
    if pathlib.Path(file_path).suffix == ".xlsx":
        file_path = xlsx2csv(file_path)
    
    # Extract IDs from the CSV
    ids = get_ids(file_path, column_name, delimiter)
    logger.info(f"Extracted IDs: {list(ids)}")

    # Find the corresponding files
    files_info = find_files(project_dir, ids)

    # Write the results to a CSV
    output_filename = os.getcwd() + "/samples_out.csv"
    write_to_csv(files_info, output_filename)
    logger.info(f"CSV file '{output_filename}' created successfully.")

    
if __name__ == "__main__":
    # Define project-specific arguments
    delimiter = ','  
    project_dir = 'Test_dir/SRA_dir'
    file_path = 'Test_dir/SRA_lichen_metagenome_test.xlsx'
    column_name = 'Run_ID'

    # Call the main function with the arguments
    main(project_dir, file_path, column_name, delimiter)
