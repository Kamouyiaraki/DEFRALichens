# Database compilation information 

In this pipeline there are **4** instances of reference data used: 

1) Initial decontamination step - removal of PhiX DNA using the reference genome: NC_001422.1
2) Initial decontamination step - removal of human DNA using reference genome:HG38 *Homo sapiens* reference genome GRCh38.p14 (GCF_000001405.40)
3) Initial binning step - DIAMOND - [uniref90 database](ftp://ftp.expasy.org/databases/uniprot/current_release/uniref/uniref90/)
4) Initial binning step - Blastn/BBSplit - custom database for 10 lichen classes


## Dependencies
	- python3.8 + [pandas](https://pandas.pydata.org/docs/getting_started/install.html)
	- [Taxonkit](https://bioinf.shenwei.me/taxonkit/download/)
	- [NCBI datasets](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/)


## Decontamination database compilation: 

**1) PhiX:** does not need to be compiled into a DB

**2) HG38 *Homo sapiens*:**

**3) DIAMOND:**

```
wget ftp://ftp.expasy.org/databases/uniprot/current_release/uniref/uniref90/uniref90.fasta.gz
perl -lane 'if(/^>(\w+)\s.+TaxID\=(\d+)/){print "$1 $2"}' <(zcat uniref90.fasta.gz) | gzip > uniref90.fasta.taxlist.gz
diamond makedb --in uniref90.fasta.gz -d uniref90.fasta.dmnd
```

**4) Custom Lichen DB - scripts referenced are available in `/scripts/`**

```
## Get taxID column from scaffold_reference_genomes.txt 
awk -F"\t" '{print $4}' scaffold_reference_genomes.txt | tail -n +2 > scaffold_ref_genomes.txt

## Run taxonkit to get lineage information + reformatted lineage information to standardize lineage across all
../../../../../users/marik2/apps/bin/taxonkit lineage scaffold_ref_genomes.txt --data-dir ../../../../../users/marik2/apps/bin/taxonkit_db/ > scaffold_ref_genomes_lineages.txt
../../../../../users/marik2/apps/bin/taxonkit reformat scaffold_ref_genomes_lineages.txt --data-dir ../../../../../users/marik2/apps/bin/taxonkit_db > scaffold_ref_genomes_lineages_reformat.txt


## Make directories to be used as db's
mkdir Basidiomycota
mkdir Ascomycota

## subset by search term in lineage
mkdir Ascomycota/Coniocybomycetes
mkdir Ascomycota/Dothideomycetes 
mkdir Ascomycota/Eurotiomycetes
mkdir Ascomycota/Lecanoromycetes
mkdir Ascomycota/Leotiomycetes
mkdir Ascomycota/Lichinomycetes
mkdir Ascomycota/Sordariomycetes
mkdir Ascomycota/Thelocarpaceae 			
	#(Ascomycota incertae sedis) 
mkdir Basidiomycota/Basidiomycetes 
mkdir Basidiomycota/Urediniomycetes 

python3.8 lichen_groups.py
	#merges the scaffold_reference_genomes.txt table and the output from taxonkit (scaffold_ref_genomes_lineages_reformat.txt > scaffold_reference_genomes_lineages.csv)
	#goes through each class (in some cases Families - defined within python script) of fungi and subsets table to output a single csv with genome information for that class

## After manual check of folders - filter files with more than 10 hits to keep at least 1 hit per family, with best quality assembly (complete genome/chromosome)
python3.8 subset_references.py

## Get accession numbers from each of these spreadsheets
bash get_accessions.sh

## Download the 
bash download_genomes.sh
```

## Accession numbers

|Reference | NCBI Accession|
|---|---|
|Escherichia phage phiX174, complete genome|NC_001422.1|
| | |
|Genome assembly GRCh38.p14|GCF_000001405.40|
| | |
|Ascomycota, Coniocybomycetes|`[/ref/]() `|
|Ascomycota, Dothideomycetes|`[/ref/]() ` |
|Ascomycota, Eurotiomycetes|`[/ref/]() ` |
|Ascomycota, Lecanoromycetes|`[/ref/]() ` |
|Ascomycota, Leotiomycetes|`[/ref/]() ` |
|Ascomycota, Lichinomycetes|`[/ref/]() ` |
|Ascomycota, Sordariomycetes|`[/ref/]() ` |
|Ascomycota, *Incertae sedis*, Thelocarpaceae|`[/ref/]() ` |
| | |
|Basidiomycota, Basidiomycetes|`[/ref/]() ` |
|Basidiomycota, Urediniomycetes|`[/ref/]() ` |