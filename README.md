# DEFRALichens

*template for snakemake + scripts for Lichen pipeline*

*note: this will avoid using any Anaconda/bioconda reliance* 

## Script details and descriptions:

### Public service announcement:

**all error checking and logs are output to `./log/` directory that is generated in the first script**

### 1. generate_samples_csv.py:

**input = a file that includes at least one column with the ID that matches raw sequence data.**

        "Usage: python generate_samples_csv.py <project_dir> <sample_info_file> <column_name> <file_delimiter>"

1) Reads a file (file delimited can be specified) to extract a specific column that contains sample IDs that will correspond to raw sequence data IDs (based on the provided column name). If this file is `.xlsx` it will convert it first to a `.csv` before running.
2) Looks for files matching IDs from that column in a given directory.
3) Logs errors for missing, unpaired, or excessive files.
4) Writes the found file paths (forward and reverse reads) to a new `.csv` file.

### 2. fastqc_raw.py:

**input = the raw file names for each ID in the spreadsheet**

1) Runs [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on the raw sequence files for manual quality control and checking purposes.
2) Outputs FastQC files to a directory per ID found and sequences analysed

### 3. fastp.py

One-pass FASTQ data preprocessing: quality control, deduplication, merging of paired reads, and trimming using [fastp](https://github.com/OpenGene/fastp)

**Parameters selected:**

        --dedup
        --min phred = 4
        --merge
        --PE
        --trim poly g
        --correction of PE
        --out1
        --out2
        --unpaired1 
        --unpaired2

### 4a. fastqc_processed.py:

**input = directory of fastp outputs**

1) Uses the names of the files to derive IDs
2) Will then run FastQC on each fastp output for manual quality control and checking purposes.
3) The default for fastp is to merge files, so FastQC should result in a single `.html` and `.zip` output per ID (all outputs will be directed to the same folder as `fastqc_raw.py`

### 4b. decontam.py

**input = directory of fastp outputs**

1) Identify sequence files from a given directory.
For each file:
2) Run [BBDuk](https://github.com/BioInfoTools/BBMap/blob/master/sh/bbduk.sh) to remove PhiX contamination. 
3) Then align reads to the human genome with [BWA MEM](https://github.com/lh3/bwa).
4) Filter out human sequences and save the non-human reads.
5) Generate statistics on the alignment.

### 5. ASSEMBLY

## References

> Simon Andrews, 2010. FastQC:  A Quality Control Tool for High Throughput Sequence Data [Online]. Available online at: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/

> Shifu Chen, 2023. Ultrafast one-pass FASTQ data preprocessing, quality control, and deduplication using fastp. iMeta 2: e107. https://doi.org/10.1002/imt2.107

> Shifu Chen, Yanqing Zhou, Yaru Chen, Jia Gu, 2018. fastp: an ultra-fast all-in-one FASTQ preprocessor, Bioinformatics, 34, 17, i884–i890. https://doi.org/10.1093/bioinformatics/bty560

> Bushnell B. – sourceforge.net/projects/bbmap/

> Heng Li, Richard Durbin, 2009. Fast and accurate short read alignment with Burrows–Wheeler transform, Bioinformatics, 25, 14, 1754–1760, https://doi.org/10.1093/bioinformatics/btp324

> Heng Li, 2013 Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. arXiv:1303.3997v2 [q-bio.GN].
