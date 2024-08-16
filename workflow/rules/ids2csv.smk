# Snakefile

import os

# Configurations (these can be passed from the command line or config.yaml)
project_dir = config["project_dir"]
sample_ids = config["sample_ids"]
sample_ids_col_name = config["sample_ids_col_name"]
delimiter = config["delimiter"]

rule all:
    input:
        "samples.csv"

rule extract_ids:
    input:
        sample_ids
    output:
        temp("ids.txt")
    params:
        sample_ids_col_name=sample_ids_col_name,
        delimiter=delimiter
    script:
        "scripts/extract_ids.py"

rule find_files:
    input:
        ids="ids.txt",
        project_dir=project_dir
    output:
        temp("file_paths.csv")
    script:
        "scripts/find_files.py"

rule write_to_csv:
    input:
        "file_paths.csv"
    output:
        "samples.csv"
    script:
        "scripts/write_to_csv.py"
