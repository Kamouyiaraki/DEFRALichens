import os
import csv
import sys
import pandas as pd
import pathlib
import logging

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("../logs/ids2csv.log"))
logger.setLevel(logging.INFO)

def get_ids(file_path, column_name, delimiter):
    df = pd.read_csv(file_path, delimiter=delimiter)
    ids = df[column_name]
    return ids

def find_files(project_dir, ids):
    results = {}
    for id in ids:
        dir = pathlib.Path(project_dir)
        files = [str(file) for file in dir.glob(f"**/*{id}*.f*q.gz")]
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

def write_to_csv(results, output_filename):
    with open(output_filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "forward", "reverse"])
        for subfolder, (r1_path, r2_path) in results.items():
            writer.writerow([subfolder, r1_path, r2_path])

if __name__ == "__main__":
    project_dir = snakemake.input[0]
    file_path = snakemake.input[1]
    column_name = snakemake.input[2]
    delimiter = snakemake.input[3]
    output_filename = snakemake.output[0]

    ids = get_ids(file_path, column_name, delimiter)
    files_info = find_files(project_dir, ids)
    write_to_csv(files_info, output_filename)

    logger.info(f"CSV file '{output_filename}' created successfully.")
