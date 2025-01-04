import os
import gzip
import shutil
import pathlib
import pandas as pd
import logging

# Set up logging
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

def get_ids(file_path, column_name, delimiter=","):
    df = pd.read_csv(file_path, delimiter=delimiter)
    return df[column_name].tolist()

def find_files(input_dirs, ids):
    matched_files = []
    for input_dir in input_dirs:
        dir_path = pathlib.Path(input_dir)
        if not dir_path.is_dir():
            logger.warning(f"Directory {input_dir} does not exist. Skipping.")
            continue

        for id in ids:
            files = list(dir_path.glob(f"*{id}*.f*q"))
            matched_files.extend([str(file) for file in files])

    return matched_files

def gzip_files(file_paths):
    for file_path in file_paths:
        gzipped_file_path = f"{file_path}.gz"
        if not file_path.endswith(".gz"):  # Avoid double-compression
            try:
                with open(file_path, 'rb') as f_in:
                    with gzip.open(gzipped_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                logger.info(f"File gzipped: {file_path} -> {gzipped_file_path}")
            except Exception as e:
                logger.error(f"Failed to gzip {file_path}: {e}")

def main(file_path, column_name, input_dirs):
    if pathlib.Path(file_path).suffix == ".xlsx":
        file_path = xlsx2csv(file_path)
        if not file_path:
            return

    ids = get_ids(file_path, column_name)
    if not ids:
        logger.error("No IDs found in input file. Exiting.")
        return

    matched_files = find_files(input_dirs, ids)
    if not matched_files:
        logger.warning("No matching files found. Exiting.")
        return

    gzip_files(matched_files)

if __name__ == "__main__":
    file_path = "PRJEB81712/X204SC24116678-Z01-F001/Batch_1_Lichen_Tracking_Sheet.csv"  # Input spreadsheet
    column_name = "Novogene_Sub_Library_Name"  # Column with IDs

    input_dirs = ["PRJEB81712/X204SC24116678-Z01-F001/demultiplexed/"]  # Directories to search

    main(file_path, column_name, input_dirs)
