import shutil
import subprocess
from pathlib import Path
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Process and organize sequencing files.")
parser.add_argument(
    "master_dir", type=str, help="Path to the master directory where files will be processed."
)
parser.add_argument(
    "links_file", type=str, help="Path to the links.csv file containing download URLs."
)
args = parser.parse_args()

# Convert arguments to Path objects
master_dir = Path(args.master_dir)
links_file = Path(args.links_file)

# Validate the links_file
if not links_file.exists() or links_file.stat().st_size == 0:
    raise ValueError(f"The specified links file '{links_file}' is missing or empty.")

# Read the first URL to extract the ID
with links_file.open("r") as f:
    first_url = f.readline().strip()
    if not first_url:
        raise ValueError(f"The links file '{links_file}' is empty.")

# Extract ID from the first URL (before the first underscore)
url_id = Path(first_url).stem.split('_')[0]  # Get the part before '_'

# Define subdirectory paths
sub_dir = master_dir / url_id
raw_data_dir = sub_dir / "raw_data"  # Directory to store all .fq.gz files

# Create directories
raw_data_dir.mkdir(parents=True, exist_ok=True)

# Download files using wget
try:
    subprocess.run(["wget", "-i", str(links_file), "-P", str(sub_dir)], check=True)
except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Error: Download failed. {e}")

# Extract all .tar files in sub_dir
for tar_file in sub_dir.glob("*.tar"):
    try:
        print(f"Extracting {tar_file}...")
        subprocess.run(
            ["tar", "-xvf", str(tar_file), "-C", str(sub_dir)],
            check=True  # Ensures an exception is raised if the command fails
        )
        tar_file.unlink()  # Remove the .tar file after successful extraction
        print(f"Removed {tar_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed for {tar_file}: {e}. Moving to the next file.")
        continue

# Recursively unzip all .zip files within subdirectories
for zip_file in sub_dir.rglob("*.zip"):
    try:
        print(f"Unzipping {zip_file}...")
        subprocess.run(["unzip", str(zip_file), "-d", str(zip_file.parent)], check=True)
        zip_file.unlink()  # Remove the .zip file after successful extraction
        print(f"Removed {zip_file}.")
    except subprocess.CalledProcessError as e:
        print(f"Unzipping failed for {zip_file}: {e}. Moving to the next file.")
        continue

# Run MD5 checksum validation
md5_file = sub_dir / "MD5.txt"
if md5_file.is_file():
    try:
        print("Validating checksums using MD5.txt...")
        subprocess.run(["md5sum", "-c", str(md5_file)], cwd=sub_dir, check=True)
        print("Checksum validation completed.")
    except subprocess.CalledProcessError as e:
        print(f"MD5 checksum validation failed: {e}.")
else:
    print("No MD5.txt file found. Skipping checksum validation.")

# Move all .fq.gz files to the raw_data directory
for fq_gz_file in sub_dir.rglob("*.fq.gz"):
    target_path = raw_data_dir / fq_gz_file.name
    if fq_gz_file != target_path:
        fq_gz_file.rename(target_path)
        print(f"Moved {fq_gz_file} to {target_path}.")

# Delete subdirectories, leaving only the raw_data directory
for dir_path in sub_dir.glob("*"):
    if dir_path.is_dir() and dir_path != raw_data_dir:
        shutil.rmtree(dir_path)
        print(f"Removed subdirectory {dir_path}.")

print("Script completed successfully. Processed files are in:")
print(raw_data_dir)

#Example usage: 
#python3.12 setup_library_dir.py MasterProjectID/ ./IlluminaDownloadLinks.csv
