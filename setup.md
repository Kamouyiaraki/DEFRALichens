# Setting up your project directory

The script [`setup.py`](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/workflow/scripts/setup.py) can be used to set up a master project directory. 

This script automates the setup of a bioinformatics project directory, downloading necessary reference genomes and tools, performing file decompression, and organizing the workspace.

## Features
### 1. Directory Setup

Creates the main project directory and subdirectories:
- `ref/` for reference files.
- `ref/lichendb/` for lichen database genomes.

### 2. Reference Genome Downloads

Downloads and decompresses:
- The human genome (`GRCh38.p14`).
- The PhiX phage genome.

### 3. Genome Indexing
Indexes the human genome using BWA for alignment.

### 4. Reference Lichen Database Setup

Downloads genome files listed in [lichen_reference_genomes.csv](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/lichen_reference_genomes.csv) into the `lichendb/` directory.
Validates file integrity using md5sum.

### 5. File Extraction

Extracts all `.zip` files in the lichendb/ directory.

### 6. Tool Installation

Downloads and extracts [BBMap](https://github.com/BioInfoTools/BBMap) for sequence analysis.

### 7. File Cleanup

- Removes all `.zip` files from the working directory and `lichendb/`.
- Deletes the `BBMap` tarball after extraction.
  
### 8. Completion Notification

Outputs a message confirming the setup is complete.

## Usage

**Prerequisites**
Ensure the following tools are installed:
- wget
- gunzip
- bwa
- unzip

**Command line usage**

```
python setup_project.py <project_id>
```

`<project_id>`: Name for the main project directory; recommended: a unique project ID.


## Output Structure
After execution, the directory structure will be as follows:

```
<project_id>/
├── ref/
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna
│   ├── GCA_000819615.1_ViralProj14015_genomic.fna
│   ├── lichendb/
│       ├── <downloaded genome files>
│       ├── MD5.txt
│       └── ...
├── BBMap/
└── ...
```

## Key Notes
Any `.zip` files in `lichendb/` are automatically extracted.
The script verifies downloaded lichen genome files using `MD5.txt`.
Cleans up unnecessary `.zip` and tarball files to save space.

## Final Message
Once completed, you will see the message:

```
Your working directory is now ready to go!
```


# Setting up library directories

The script [`setup_library_dir.py`](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/workflow/scripts/setup_library_dir.py) is designed to specifically streamline adding in sequence data into the set up project directory for analysis. 

This script automates the processing and organization of sequencing files. It downloads files from provided URLs, extracts archives, validates file integrity, and organizes .fq.gz files into a designated directory.
This script assumes that libraries downloaded will follow the naming scheme of: <library-id>_<integer>.tar

## Features

### 1. Directory Setup

Will search for the master project directory (using `setup.py`). If not found, this script will create a master project directory. It then organizes files by subdirectories derived from the first URL ID assuming that the ID matches the library name.

### 2. Generates a raw_data/ directory to consolidate all .fq.gz files.

### 3. File Downloads

- Reads a links.csv file containing download URLs.
- Downloads files using `wget` into a subdirectory named after the URL ID.

### 4. File Extraction

- Extracts `.tar` and `.zip` files within the subdirectory.
- Removes archive files post-extraction to save space.

### 5. Checksum Validation

- Validates file integrity using an `MD5.txt` file (if present) via md5sum.

### 6. File Organization

- Moves all `.fq.gz` files into the `raw_data/` directory.
- Cleans up unnecessary subdirectories, retaining only `raw_data/`.

### 7. Completion Notification

Outputs the location of processed files upon successful execution.

## Usage
**Prerequisites**
Ensure the following tools are installed:
- wget
- tar
- unzip
- md5sum

**Command line usage**

```
python setup_library_dir.py <master_dir> <links_file>
```

`<master_dir>`: Path to the project’s master directory.

`<links_file>`: Path to a links.csv file containing the download URLs.


## Output Structure
After execution, the directory structure will be:

```
<project_dir>/
└── <url_id>/
    └── raw_data/
        ├── file1.fq.gz
        ├── file2.fq.gz
        └── ...
```

## Key Notes
### Input Validation
- The script verifies the links.csv file is present and not empty.

### Error Handling
- Automatically skips and logs failed extractions or downloads.

### File Cleanup
- `.tar` and `.zip` files are deleted after extraction.
- Unnecessary subdirectories are removed, leaving only `raw_data/`.

### Checksum Validation
- If `MD5.txt` is available, the script validates the integrity of the downloaded files.

## Final Message
Once the script completes, you will see:

```
Script completed successfully. Processed files are in:
<path_to_raw_data>
```
