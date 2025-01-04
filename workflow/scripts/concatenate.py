import pathlib
import csv
import logging
import pandas as pd
import os
from concurrent.futures import ThreadPoolExecutor

# Set up logger
logger = logging.getLogger(__name__)

## FUNCTIONS TO READ IDS
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

def get_ids(file_path, column_name, delimiter):
    df = pd.read_csv(file_path, delimiter=delimiter)
    return df[column_name].tolist()

### FUNCTION TO FIND FILES FOR EACH DIRECTION	
def find_files(input_dirs, ids, direction):
    # Generate the output CSV filename based on direction
    output_csv = f"files_found_{direction}.csv"
    
    # Initialize results: A nested dictionary for each ID and directory
    results = {id: {input_dir: None for input_dir in input_dirs} for id in ids}
    missing_ids = set(ids)

    for input_dir in input_dirs:
        dir_path = pathlib.Path(input_dir)
        if not dir_path.is_dir():
            logger.warning(f"Directory {input_dir} does not exist. Skipping.")
            continue

        for id in ids:
            file_pattern = f"*{id}*{direction}*.f*q.gz"
            files = sorted(dir_path.glob(file_pattern))

            if files:
                results[id][input_dir] = str(files[0])
                missing_ids.discard(id)  # Remove found ID from missing_ids

    # Log missing IDs
    if missing_ids:
        logger.warning(f"No reads found for IDs: {', '.join(missing_ids)}")

    # Write results to CSV
    write_results_to_csv(results, input_dirs, output_csv)
    return results

### FUNCTION TO WRITE TO CSV 
def write_results_to_csv(results, input_dirs, output_csv):
    # Prepare CSV header
    header = ["ID"] + input_dirs 

    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        # Write each ID and its corresponding filepaths
        for id, dir_results in results.items():
            row = [id] + [dir_results.get(dir, None) for dir in input_dirs]
            writer.writerow(row)

    logger.info(f"Results have been written to {output_csv}")

## FUNCTION TO CONCATENATE R1 AND R2 FILES
def concatenate_files_per_id(output_dir, direction):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # output directory name   
    output_csv = f"files_found_{direction}.csv"

    # Open the CSV file for reading
    with open(output_csv, "r") as f:
        reader = csv.DictReader(f)
        
        # Iterate through each row in the CSV
        for row in reader:
            id = row["ID"]  # Get the ID from the first column

            # Create the output filename based on the ID and direction
            output_filename = pathlib.Path(output_dir) / f"{id}_concatenated_reads_{direction}.fq.gz"
            
            # Open the output file in write binary mode
            with open(output_filename, "wb") as out_f:
                for key, file_path in row.items():
                    if key != "ID" and file_path:  # Skip the "ID" column and check if the file path exists
                        try:
                            # Open each file in read binary mode and write its content to the output file
                            with open(file_path, "rb") as in_f:
                                out_f.write(in_f.read())  # Append the content of the file
                            logger.info(f"Appended {file_path} to {output_filename}")
                        except Exception as e:
                            logger.error(f"Failed to append {file_path} for ID {id}: {e}")

def main(file_path, input_dirs, output_dir, max_workers=8):
    if pathlib.Path(file_path).suffix == ".xlsx":
        file_path = xlsx2csv(file_path)
        if not file_path:
            return
    
    ids = get_ids(file_path, column_name, delimiter=",")
    
    if not ids:
        logger.error("No IDs found in input file. Exiting.")
        return

    directions = ["1", "2"]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        # Submit find_files for each direction
        for direction in directions:
            futures.append(executor.submit(find_files, input_dirs, ids, direction))

        # Wait for all find_files tasks to complete before submitting concatenate_files_per_id
        for future in futures:
            future.result()  # Ensure find_files completes first

        # Now submit concatenate_files_per_id for each direction
        for direction in directions:
            executor.submit(concatenate_files_per_id, output_dir, direction)

        # Wait for all concatenate tasks to complete
        for future in futures:
            future.result()  # To re-raise exceptions if any occurred

    print("All samples concatenated!")

if __name__ == "__main__":
    # Specify directories
    csv_file = "PRJEB81712/X204SC24116678-Z01-F001/Batch_1_Lichen_Tracking_Sheet.csv"
    input_dirs = ["PRJEB81712/X204SC24116678-Z01-F001/raw_data", "PRJEB81712/X204SC24116678-Z01-F001/demultiplexed"]
    column_name = "Novogene_Sub_Library_Name"  # or whatever your actual column name is

    output_dir = "PRJEB81712/X204SC24116678-Z01-F001/input_reads"
    main(csv_file, input_dirs, output_dir)