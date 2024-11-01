import os
import sys
import pandas as pd
from pathlib import Path
import pathlib
import logging
import csv
import subprocess

# Ensure the logs directory exists
log_dir = os.path.dirname("./logs/get_taxids.log")
os.makedirs(log_dir, exist_ok=True)  # Creates the directory if it doesn't exist

# Configure logger
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(logging.FileHandler("./logs/get_taxids.log"))
logger.setLevel(logging.INFO)

def detect_delimiter(file_path):
    with open(file_path, 'r') as csvfile:
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        return dialect.delimiter

def read_file(file_path):
    # Check if the provided file exists
    if not Path(file_path).is_file():
        logger.error(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    
    # If the file is an XLSX read_excel, else read_csv
    if pathlib.Path(file_path).suffix == ".xlsx":
        df = pd.read_excel(file_path)
    else:
        delimiter = detect_delimiter(file_path)
        df = pd.read_csv(file_path, delimiter=delimiter)
    
    # Drop rows that are entirely empty
    df.dropna(how="all", inplace=True)


    return df

def merge_df(df):
    filename = os.path.basename(file_path)
    filename = filename.replace(".xlsx", "")  # Remove the `.xlsx` extension
    filepath = os.path.dirname(file_path)
    taxoutfile = os.path.join(filepath, f"{filename}_taxids_only.out")

    lin = pd.read_csv(taxoutfile, header=None, delimiter="\t")
    lin.columns = ["Taxonomic_name", "TaxID"]
    
    merged_df = pd.concat([df, lin], axis=1)
    
    # Define output file path and save the merged dataframe
    filename = os.path.basename(file_path)
    filename = filename.replace(".xlsx", "")  # Remove the `.xlsx` extension
    filepath = os.path.dirname(file_path)
    outfile = os.path.join(filepath, f"{filename}_taxids.csv")
    
    merged_df.to_csv(outfile, sep=',', index=False)
    return outfile

def get_taxids(df, column_name, file_path):
    ids = [str(item) for item in df[column_name]]
    with open('ids.txt', 'w') as f:
        f.write("\n".join(ids))
    
    filename = os.path.basename(file_path)
    filename = filename.replace(".xlsx", "")  # Remove the `.xlsx` extension
    filepath = os.path.dirname(file_path)
    taxoutfile = os.path.join(filepath, f"{filename}_taxids_only.out")

    command = f"cat ids.txt | ../../../../users/marik2/apps/bin/taxonkit name2taxid --data-dir ../../../../users/marik2/apps/bin/taxonkit_db/ > {taxoutfile}"
    
    # Execute the shell command
    subprocess.run(command, shell=True, check=True)
    
    # Read the generated taxids.out file
    taxids_df = pd.read_csv(taxoutfile, header=None, delimiter="\t", names=["Taxonomic_name", "TaxID"])
    null_mask = taxids_df.isnull().any(axis=1)
    null_rows = taxids_df[null_mask]
    null_outfile = os.path.join(filepath, f"{filename}_null_taxids.csv")
    null_rows.to_csv(null_outfile, sep=',', index=False)

    return taxids_df

def main(file_path, column_name):
    # Read the input file
    df = read_file(file_path)
    
    # Extract TaxIDs or other IDs
    taxids_df = get_taxids(df, column_name, file_path)
    logger.info(f"Extracted IDs: {taxids_df.head()}")

    # Merge data and write results to CSV
    output_filename = merge_df(df)
    logger.info(f"CSV file '{output_filename}' created successfully.")

if __name__ == "__main__":
    # Define project-specific arguments
    file_path = 'Batch_4_Lichen_Tracking_Sheet.xlsx'
    column_name = 'Taxonomic_name'

    # Call the main function with the arguments
    main(file_path, column_name)
