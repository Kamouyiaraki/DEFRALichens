import os
from pathlib import Path
import subprocess
import zipfile
import argparse
##requires: bwa 

# Helper functions
def create_dir(directory: Path):
    """Create a directory if it doesn't already exist."""
    directory.mkdir(parents=True, exist_ok=True)

def run_command(command: list, error_message: str, cwd: Path = None):
    """Run a subprocess command with error handling, optionally in a specific working directory."""
    try:
        subprocess.run(command, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{error_message}\nError Details: {e}")
        exit(1)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Setup a project directory.")
parser.add_argument("project_id", type=str, help="Name of the project directory.")
args = parser.parse_args()

# Set up directories
project_dir = Path(args.project_id)
ref_dir = project_dir / "ref"
lichen_db_dir = ref_dir / "lichendb"

# Create directories
create_dir(project_dir)
create_dir(ref_dir)
create_dir(lichen_db_dir)

# URLs and file paths
HUMAN_GENOME_URL = "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz"
PHAGE_GENOME_URL = "ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/viral/Sinsheimervirus_phiX174/latest_assembly_versions/GCA_000819615.1_ViralProj14015/GCA_000819615.1_ViralProj14015_genomic.fna.gz"
BBMAP_URL = "https://sourceforge.net/projects/bbmap/files/BBMap_39.10.tar.gz"

human_genome_gz = ref_dir / "GCF_000001405.40_GRCh38.p14_genomic.fna.gz"
phage_genome_gz = ref_dir / "GCA_000819615.1_ViralProj14015_genomic.fna.gz"
human_genome_fna = ref_dir / "GCF_000001405.40_GRCh38.p14_genomic.fna"
lichen_db_csv = "lichen_reference_genomes.csv"
lichen_md5_file = lichen_db_dir / "MD5.txt"
bbmap_tarball = project_dir / "BBMap_39.10.tar.gz"

# Lichen DB setup
run_command(
    ["wget", "-i", str(lichen_db_csv), "-P", lichen_db_dir, "-q"],
    "Failed to download Lichen DB genomes."
)

# Run md5sum in the Lichen DB directory
run_command(
    ["md5sum", "-c", lichen_md5_file.name],  # Use only the file name
    "MD5 checksum validation failed.",
    cwd=lichen_db_dir  # Change the working directory to lichendb
)

# Unzip all ZIP files in the Lichen DB directory using run_command
zip_files = list(lichen_db_dir.glob("*.zip"))
if zip_files:
    for zip_file in zip_files:
        try:
            print(f"Extracting {zip_file}...")
            run_command(
                ["unzip", str(zip_file), "-d", str(lichen_db_dir)],
                f"Failed to unzip {zip_file}."
            )
            print(f"Extraction of {zip_file} completed.")
        except SystemExit:
            print(f"Extraction failed for {zip_file}. Moving to the next file.")
            continue  # Move to the next file
else:
    logger.info(f"No ZIP files found in {lichen_db_dir}.")

# Download and extract BBMap
run_command(
    ["wget", BBMAP_URL, "-P", project_dir, "-q"],
    "Failed to download BBMap."
)

run_command(
    ["tar", "zvxf", str(bbmap_tarball), "-C", str(project_dir)],
    "Failed to extract BBMap."
)


# Remove all .zip files from the working directory and Lichen DB directory
def remove_zip_files(directories):
    for directory in directories:
        zip_files = list(directory.glob("*.zip"))
        for zip_file in zip_files:
            try:
                zip_file.unlink()  # Deletes the file
                print(f"Removed {zip_file}.")
            except Exception as e:
                print(f"Failed to remove {zip_file}: {e}")

# Directories to clean
directories_to_clean = [Path("."), lichen_db_dir]
remove_zip_files(directories_to_clean)

run_command(
    ["rm", str(bbmap_tarball)],
    "Failed to remove BBMap.tar"
)

#Finishing statement
print("Your working directory is now ready to go!")
