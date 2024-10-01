# DEFRALichens

*template for snakemake + scripts for Lichen pipeline*

*note: this will avoid using any Anaconda/bioconda reliance* 


## Script details and descriptions:

### Public service announcement:

All error checking and logs are output to `./log/` directory that is generated in the first script.

### 1. generate_samples_csv.py:

> input = a file that includes at least one column with the ID that matches raw sequence datafiles.
>
> output = `samples_out.csv` with ID, FW read file location, RV read file location


        "Usage: python generate_samples_csv.py <project_dir> <sample_info_file> <column_name> <file_delimiter>"

1) Reads a file (file delimited can be specified) to extract a specific column that contains sample IDs that will correspond to raw sequence data IDs (based on the provided column name). If this file is `.xlsx` it will convert it first to a `.csv` before running.
2) Looks for files matching IDs from that column in a given directory.
3) Logs errors for missing, unpaired, or excessive files.
4) Writes the found file paths (forward and reverse reads) to a new `.csv` file.


### 2. fastqc_raw.py:

> input = `samples_out.csv`
>
> output = directory for each ID in file, with FW and RV FastQC output files in


1) Runs [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) on the raw sequence files for manual quality control and checking purposes.
2) Outputs FastQC files to a directory per ID found and sequences analysed


### 3. fastp.py

> input = `samples_out.csv`
>
> output = `fastp_proccessed` directory


One-pass FASTQ data preprocessing: quality control, deduplication, merging of paired reads, and trimming using [fastp](https://github.com/OpenGene/fastp)

Parameters:

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

> input = `fastp_proccessed` directory
>
> output = FastQC output files in each ID directory

1) Uses the names of the files to derive IDs
2) Will then run FastQC on each fastp output for manual quality control and checking purposes.
3) The default for fastp is to merge files, so FastQC should result in a single `.html` and `.zip` output per ID (all outputs will be directed to the same folder as `fastqc_raw.py`


### 4b. decontam.py

> input = `fastp_proccessed` directory
> 
> output = `decontaminated_reads` directory

1) Identify sequence files from a given directory.
For each file:
2) Run [BBDuk](https://github.com/BioInfoTools/BBMap/blob/master/sh/bbduk.sh) to remove PhiX contamination. 
3) Then align reads to the human genome with [BWA MEM](https://github.com/lh3/bwa).
4) Filter out human sequences and save the non-human reads.
5) Generate statistics on the alignment.


### 5a. ASSEMBLY

> input = `decontaminated_reads` directory (MetaSPADES ONLY also includes: unmerged reads from `./fastp_processed`)
>
> output = `assemblies` directory with subdirectory for each assembly type in the format of `<ID>_<ASSEMBLER>`

Assemblers: 
- [MEGAHIT](https://github.com/voutcn/megahit)
- [MetaSPADES](https://github.com/ablab/spades)
- [IDBA-UD](https://github.com/loneknightpy/idba)
- [MetaHipMer2](https://bitbucket.org/berkeleylab/mhm2/src/master/)


#### MetaSPADES Parameters:
        --merged <fastp_merged_file>
        -1 <unmerged1_file>
        -2 <unmerged2_file> 
        --phred-offset 33

#### IDBA-UD Parameters:

        --num_threads 1
        
        Additional change: Insert lengths reduced following [guidance](https://www.seqanswers.com/forum/bioinformatics/bioinformatics-aa/24625-250bp-reads-in-idba_ud)


### 5b. Assembly Checkpoint - run_assembly_check.py
> input(1)  = assembler type 

> input (2) = `assemblies` directory with subdirectory for each assembly type in the format of `<ID>_<ASSEMBLER>`

`run_assembly_check.py` is used to call a "check assembly" script specific to each assembler (Valid assemblers are: 'megahit', 'metaspades', 'idba-ud', 'mhm2'):

- check_assemblies_megahit.py

If a `final.contigs.fa` file is not found, it will attempt to "resume" MEGAHIT (`--continue`)
  
- check_assemblies_metaspades.py

If a `scaffolds.fasta` file is not found, it will attempt to "resume" MetaSPADES (`--continue`)


- check_assemblies_idba-ud.py

If a `contig.fa` **OR** `scaffold.fa` file is not found, it will spit out an error message. IDBA-UD does not offer a resume option, therefore the assembly will have to be restarted or a different assembler will have to be used. 


- <mhm2 TBC> 

*mhm2 TBC*

Each check assembly script requires a specified assembly directory (input(2)). 

### 6. bwa_unassembled_reads.py

> input =
>
> output = 

1) Scans a specified directory for IDs.
2) For each ID, it identifies the appropriate assembly file based on the selected assembler (e.g., megahit, metaspades, or idba-ud). If idba-ud is used, it checks for alternative assembly files.
3) Uses BWA to output unassembled Reads and Stats
4) Concatenates the unassembled Reads with the final contigs file.


## Directory strucutre

```
├── assemblies
│   ├── <ID>_idba_ud
│   ├── <ID>_megahit
│   ├── <ID>_metaspades
│   ├── <ID>_mhm2
├── decontaminated_reads
├── fastp_processed
├── <ID>
├── logs
├── ref
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna.amb
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna.ann
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna.bwt
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna.pac
│   ├── GCF_000001405.40_GRCh38.p14_genomic.fna.sa
│   ├── lichendb
│   │   ├── Ascomycota
│   │   │   ├── Coniocybomycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── Coniocybomycetes_genome_accessions.txt
│   │   │   │   └── README.md
│   │   │   ├── Dothideomycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── README.md
│   │   │   │   └── Reduced_Dothideomycetes_genome_accessions.txt
│   │   │   ├── Eurotiomycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── README.md
│   │   │   │   └── Reduced_Eurotiomycetes_genome_accessions.txt
│   │   │   ├── Lecanoromycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── README.md
│   │   │   │   └── Reduced_Lecanoromycetes_genome_accessions.txt
│   │   │   ├── Leotiomycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── README.md
│   │   │   │   └── Reduced_Leotiomycetes_genome_accessions.txt
│   │   │   ├── Lichinomycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── Lichinomycetes_genome_accessions.txt
│   │   │   │   └── README.md
│   │   │   ├── Sordariomycetes
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   ├── README.md
│   │   │   │   └── Reduced_Sordariomycetes_genome_accessions.txt
│   │   │   └── Thelocarpaceae
│   │   │       ├── concatenated_genomes.fa
│   │   │       ├── README.md
│   │   │       └── Thelocarpaceae_genome_accessions.txt
│   │   ├── Basidiomycota
│   │   │   ├── Basidiomycetes
│   │   │   │   ├── Basidiomycetes_genome_accessions.txt
│   │   │   │   ├── concatenated_genomes.fa
│   │   │   │   └── README.md
│   │   │   └── Urediniomycetes
│   │   │       ├── concatenated_genomes.fa
│   │   │       ├── README.md
│   │   │       ├── Urediniomycetes_genome_accessions.txt
│   ├── NC_001422.1_escherichia_phage_phiX174.fasta
│   ├── uniref90.fasta.dmnd
│   ├── uniref90.fasta.gz
│    uniref90.fasta.taxlist.gz
└── samples_out.csv

```


## References
- Simon Andrews, 2010. FastQC:  A Quality Control Tool for High Throughput Sequence Data [Online]. Available online at: http://www.bioinformatics.babraham.ac.uk/projects/fastqc/
- Shifu Chen, 2023. Ultrafast one-pass FASTQ data preprocessing, quality control, and deduplication using fastp. iMeta 2: e107. https://doi.org/10.1002/imt2.107
- Shifu Chen, Yanqing Zhou, Yaru Chen, Jia Gu, 2018. fastp: an ultra-fast all-in-one FASTQ preprocessor, Bioinformatics, 34, 17, i884–i890. https://doi.org/10.1093/bioinformatics/bty560
- Bushnell B. – sourceforge.net/projects/bbmap/
- Heng Li, Richard Durbin, 2009. Fast and accurate short read alignment with Burrows–Wheeler transform, Bioinformatics, 25, 14, 1754–1760, https://doi.org/10.1093/bioinformatics/btp324
- Heng Li, 2013 Aligning sequence reads, clone sequences and assembly contigs with BWA-MEM. arXiv:1303.3997v2 [q-bio.GN].
- Li, D., Liu, C-M., Luo, R., Sadakane, K., and Lam, T-W., 2015. MEGAHIT: An ultra-fast single-node solution for large and complex metagenomics assembly via succinct de Bruijn graph. Bioinformatics, doi: 10.1093/bioinformatics/btv033 [PMID: 25609793].
- Li, D., Luo, R., Liu, C.M., Leung, C.M., Ting, H.F., Sadakane, K., Yamashita, H. and Lam, T.W., 2016. MEGAHIT v1.0: A Fast and Scalable Metagenome Assembler driven by Advanced Methodologies and Community Practices. Methods.
- Nurk S, Meleshko D, Korobeynikov A, Pevzner PA, 2017. metaSPAdes: a new versatile metagenomic assembler. Genome Res.;27(5):824-834. doi: 10.1101/gr.213959.116. Epub 2017 Mar 15. PMID: 28298430; PMCID: PMC5411777.
- Yu Peng, Henry C. M. Leung, S. M. Yiu, Francis Y. L. Chin, 2012. IDBA-UD: a de novo assembler for single-cell and metagenomic sequencing data with highly uneven depth, Bioinformatics, 28, 11, 1420–1428, https://doi.org/10.1093/bioinformatics/bts174
- Hofmeyr, S., Egan, R., Georganas, E. et al. 2020. Terabase-scale metagenome coassembly with MetaHipMer. Sci Rep 10, 10689.
