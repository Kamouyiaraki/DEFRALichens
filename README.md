# DEFRALichens

*template for snakemake + scripts for Lichen pipeline*

*note: this will avoid using any Anaconda/bioconda reliance* 

## Script details and descriptions:

### Public service announcement:

**The first script (`ids2csv.py`) is set up so can be run using system arguments independently, the rest of the scripts will require input parameters changed within the main argument at the bottom of the script if planning to customise** 

**all error checking and logs are output to `./log/` directory that is generated in the first script**


### 1. ids2csv.py:

**input = a file that includes at least one column with the ID that matches raw sequence data.**


        "Usage: python ids2csv.py <project_dir> <sample_info_file> <column_name> <file_delimiter>"

1) Checks if the input file is a .xlsx or a .csv file
2) Converts an .xlsx file into a .csv file by reading the Excel file and writing its contents as a CSV.
3) Reads a CSV file to extract a specific column (based on the provided column name).
4) Looks for files matching IDs from that column in a given directory.
5) Logs errors for missing, unpaired, or excessive files.
6) Writes the found file paths (forward and reverse reads) to a new CSV file.

### 2. fastqc_raw.py:

**input = the raw file names for each ID in the spreadsheet**

1) Runs FastQC on the raw sequence files for manual quality control and checking purposes.
2) Outputs FastQC files to a directory per ID found and sequences analysed

### 3. fastp.py


### 4. fastqc_processed.py:

**input = directory of fastp outputs**

1) Uses the names of the files to derive IDs
2) Will then run FastQC on each fastp output for manual quality control and checking purposes.
3) The default for fastp is to merge files, so FastQC should result in a single `.html` and `.zip` output per ID (all outputs will be directed to the same folder as `fastqc_raw.py`

### 5. 
