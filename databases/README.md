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
	- [BWA](https://github.com/lh3/bwa)

## Decontamination database compilation: 

**1) PhiX:** does not need to be compiled into a DB

```
wget ftp://ftp.ncbi.nlm.nih.gov/genomes/Viruses/enterobacteria_phage_phix174_sensu_lato_uid14015/NC_001422.fna
```

**2) HG38 *Homo sapiens*:**

```
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz
gunzip GCF_000001405.40_GRCh38.p14_genomic.fna.gz
bwa index GCF_000001405.40_GRCh38.p14_genomic.fna

```

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
./apps/bin/taxonkit lineage scaffold_ref_genomes.txt --data-dir ./apps/bin/taxonkit_db/ > scaffold_ref_genomes_lineages.txt
./apps/bin/taxonkit reformat scaffold_ref_genomes_lineages.txt --data-dir ./apps/bin/taxonkit_db > scaffold_ref_genomes_lineages_reformat.txt


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

## Concatenate genomes into a single file in each class directory 
	## For JGI genomes:
	### For Dothideomycetes
    find ./Bimnz1/ -type f -exec mv {} ./// \;
    find ./Veren1/ -type f -exec mv {} ./// \;
    rm -r ./Bimnz1/
    rm -r ./Veren1/

	### 	Eurotiomycetes
    find ./Cocba1/ -type f -exec mv {} ./// \;
    find ./Parmar1/ -type f -exec mv {} ./// \;
    rm -r ./Cocba1/
    rm -r ./Parmar1/

	###	Lecanoromycetes
    find ./Grascr1/ -type f -exec mv {} ./// \;
    rm -r ./Grascr1/

	###	Leotiomycetes
    find ./Atrpi1/ -type f -exec mv {} ./// \;
    find ./Lopnit1_1/ -type f -exec mv {} ./// \;
    find ./Bulin1/ -type f -exec mv {} ./// \;
    find ./Cocst1/ -type f -exec mv {} ./// \;
    find ./Pseel1/ -type f -exec mv {} ./// \;
    find ./Spafl1/ -type f -exec mv {} ./// \;
    find ./Themi1/ -type f -exec mv {} ./// \;
    find ./Elyde1/ -type f -exec mv {} ./// \;
    find ./Greab1/ -type f -exec mv {} ./// \;
    find ./Greabi1/ -type f -exec mv {} ./// \;        
    find ./Psever1/ -type f -exec mv {} ./// \;
    find ./PseVKM3775_1/ -type f -exec mv {} ./// \;  
    find ./PseVKM4514_1/ -type f -exec mv {} ./// \;
    find ./Thest1/ -type f -exec mv {} ./// \;           
    rm -r ./Atrpi1/ 
    rm -r  /Lopnit1_1/ 
    rm -r ./Bulin1/ 
    rm -r ./Cocst1/ 
    rm -r ./Pseel1/ 
    rm -r ./Spafl1/ 
    rm -r ./Themi1/ 
    rm -r ./Elyde1/ 
    rm -r ./Greab1/ 
    rm -r ./Greabi1/        
    rm -r ./Psever1/
    rm -r ./PseVKM3775_1/   
    rm -r ./PseVKM4514_1/ 
    rm -r ./Thest1/

	###	Sordariomycetes
    find ./Nieex1/ -type f -exec mv {} ./// \;
    rm -r ./Nieex1/
```

#### The following was then run once per directory:

```
rm -r *.zip
bash cat_genomes.sh
```


**5) Makeblastdb Lichen DB**

Blast databases were made for each of the references using `makeblastdb` version 2.11.0+. 

```
_dir="/absolute/path/to/ref/lichendb/Ascomycota/*/"

for f in $_dir
do
    if [ -d "$f" ]; then
        dir_name=$(basename "$f")
        echo "Running makeblastdb for $dir_name"
        makeblastdb -in "${f}/concatenated_genomes.fa" -dbtype nucl -title "${dir_name}_genomes"
    fi
done


_dir2="/absolute/path/to/ref/lichendb/Basidiomycota/*/"

for g in $_dir2
do
    if [ -d "$g" ]; then
        dir_name2=$(basename "$g")
        echo "Running makeblastdb for $dir_name2"
        makeblastdb -in "${g}/concatenated_genomes.fa" -dbtype nucl -title "${dir_name2}_genomes"
    fi
done

```

In some instances, concatenating sequences resulted in duplicated seq IDs. This was resolved using `fasta-unique-names` from [MEME suite](https://web.mit.edu/meme_v4.11.4/share/doc/fasta-unique-names.html#:~:text=Description,any%20names%20which%20are%20duplicates.)

Installation of [MEME suite v 5.5.7](https://meme-suite.org/meme//doc/download.html) was done as follows: 

```
wget https://meme-suite.org/meme/meme-software/5.5.7/meme-5.5.7.tar.gz
tar zxf meme-5.5.7.tar.gz
cd meme-5.5.7
./configure --prefix=$HOME/meme --with-url=http://meme-suite.org --enable-build-libxml2 --enable-build-libxslt
make
make test
make install
```

*Example usage:* 

```
cd ../Ascomycota/Eurotiomycetes/
./apps/meme-5.5.7/scripts/fasta-unique-names -r ./concatenated_genomes.fa
```


**JGI Genome data details**
JGI Genomes were downloaded to supplement families that were not found in NCBI. This requires a valid JGI account and log in details, but can be downloaded using the JGI API (find download options [here](https://genome.jgi.doe.gov/portal/help/download.jsf#/api))


### JGI Terms and Conditions to be aware of:

> By accessing JGI data, you agree not to publish any articles containing analyses of genes or genomic data prior to publication by the principal investigators of its comprehensive analysis without the consent of the project's principal investigator(s). These restrictions will be lifted upon publication(s) of the dataset or two years after the public release of this data, whichever is first. Scientists are expected to contact the principal investigator about their intentions to include any data from this project in a publication prior to publication of the primary report in order to ensure that their publication does not compete directly with planned publications (e.g. reserved analyses) of the principal investigators.

> If these data are used for publication, the following acknowledgment should be included: ‘These sequence data were produced by the US Department of Energy Joint Genome Institute https://www.jgi.doe.gov/ in collaboration with the user community.’ We also request that you appropriately cite any JGI resources used for analysis (such as IMG, Phytozome or Mycocosm) and that you notify us upon publication.

## Accession numbers

|Reference | NCBI Accession| JGI Link | Total Size |
|---|---|---|---|
|Escherichia phage phiX174, complete genome|NC_001422.1| --| 6 KB|
| | | | |
|Genome assembly GRCh38.p14|GCF_000001405.40| --| 3.11 GB |
| | | |
|Ascomycota, Coniocybomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Coniocybomycetes_genome_accessions.txt)| -- | 46.2 MB|
|Ascomycota, Dothideomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Reduced_Dothideomycetes_genome_accessions.txt) | [JGI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/jgi_dothideomycetes_links)| 953 MB|
|Ascomycota, Eurotiomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Reduced_Eurotiomycetes_genome_accessions.txt) | [JGI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/jgi_eurotiomycetes_links)| 428 MB|
|Ascomycota, Lecanoromycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Reduced_Lecanoromycetes_genome_accessions.txt) | [JGI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/jgi_lecanoromycetes_links) | 1.31 GB|
|Ascomycota, Leotiomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Reduced_Leotiomycetes_genome_accessions.txt) | [JGI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/jgi_leotiomycetes_links) | 3.30 GB|
|Ascomycota, Lichinomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Lichinomycetes_genome_accessions.txt) | -- | 58.1 MB|
|Ascomycota, Sordariomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Reduced_Sordariomycetes_genome_accessions.txt) |[JGI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/jgi_sordariomycetes_links) | 871 MB |
|Ascomycota, *Incertae sedis*, Thelocarpaceae|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Thelocarpaceae_genome_accessions.txt) | -- | 20.7 MB |
| | |
|Basidiomycota, Basidiomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Basidiomycetes_genome_accessions.txt) | -- | 911 MB|
|Basidiomycota, Urediniomycetes|[NCBI](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/Urediniomycetes_genome_accessions.txt) | -- | 2.30 GB|
