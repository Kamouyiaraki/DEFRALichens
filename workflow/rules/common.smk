import csv
import sys
import pandas
import pathlib
import logging
from snakemake.utils import min_version


# define min version
min_version("8.4.12")


# set configfile
configfile: "config/config.yaml"


# configfile parameters
sample_ids = config["sample_ids"]
sample_ids_col_num = config["sample_ids_col_num"]
delimiter = config["delimiter"]
project_dir = config["project_dir"]
go_reference = config["go_reference"]
forward_adapter = config["forward_adapter"]
reverse_adapter = config["reverse_adapter"]
fastp_dedup = config["fastp_dedup"]
plot_height = config["plot_height"]
plot_width = config["plot_width"]


# read sample data
if os.path.exists(config["samples"]):
    sample_data = pd.read_csv(config["samples"]).set_index("ID", drop=False)
else:
    sys.exit(f"Error: samples.csv file '{config['samples']}' does not exist")


# functions to get metadata sample list
def get_forward(wildcards):
    return sample_data.loc[wildcards.sample, "r1_path"]


def get_reverse(wildcards):
    return sample_data.loc[wildcards.sample, "r2_path"]


def get_fastq(wildcards):
    fwd = sample_data.loc[wildcards.sample, "r1_path"]
    rev = sample_data.loc[wildcards.sample, "r2_path"]
    return [fwd, rev]


# config paramter checks
if go_reference == "go_fetch" and user_email == "user@example_email.com":
    sys.exit(
        f"Error: if using go_fetch to download references, please change the example email provided in the config file'"
    )
if go_reference != "go_fetch" and go_reference != "custom":
    sys.exit(f"Error: go_reference must be 'go_fetch' or 'custom'")
if not isinstance(fastp_dedup, bool):
    sys.exit(f"Error: fastp_dedup must be 'True' or 'False'")
if mitos_refseq not in [
    "refseq39",
    "refseq63f",
    "refseq63m",
    "refseq63o",
    "refseq89f",
    "refseq89m",
    "refseq89o",
]:
    sys.exit(
        "Error: mitos_refseq must be one of 'refseq39', 'refseq63f', 'refseq63m', 'refseq63o', 'refseq89f', 'refseq89m', 'refseq89o'"
    )
if mitos_code not in [2, 4, 5, 9, 13, 14]:
    sys.exit("Error: mitos_code must be one of 2, 4, 5, 9, 13, 14")
if (
    not isinstance(missing_threshold, float)
    or missing_threshold < 0.0
    or missing_threshold > 1.0
):
    sys.exit("Error: missing_threshold must be a float between 0.0 and 1.0")
if alignment_trim not in ["gblocks", "clipkit"]:
    sys.exit("Error: alignment_trim must be 'gblocks' or 'clipkit'")

# samples.csv check
if any(sample_data["ID"].duplicated()):
    sys.exit(
        f"Error: duplicated sample names present: {list(sample_data['ID'][sample_data['ID'].duplicated()])}"
    )
for i in sample_data["forward"]:
    if not os.path.exists(i):
        sys.exit(f"Error: forward reads path '{i}' does not exist")
for i in sample_data["reverse"]:
    if not os.path.exists(i):
        sys.exit(f"Error: reverse reads path '{i}' does not exist")

wildcard_constraints:
    sample=r"[^*/~]+",
