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

## Decontamination database

**1) PhiX:** does not need to be compiled into a DB

```
wget ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/viral/Sinsheimervirus_phiX174/latest_assembly_versions/GCA_000819615.1_ViralProj14015/GCA_000819615.1_ViralProj14015_genomic.fna.gz

```

 
*Update 2024-11-26: the link: ftp://ftp.ncbi.nlm.nih.gov/genomes/Viruses/enterobacteria_phage_phix174_sensu_lato_uid14015/NC_001422.fna is not longer valid. Most up to date genome used instead.*

**2) HG38 *Homo sapiens*:**

```
wget https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GCF_000001405.40_GRCh38.p14_genomic.fna.gz
gunzip GCF_000001405.40_GRCh38.p14_genomic.fna.gz
bwa index GCF_000001405.40_GRCh38.p14_genomic.fna

```

## DIAMOND Binning

```
wget ftp://ftp.expasy.org/databases/uniprot/current_release/uniref/uniref90/uniref90.fasta.gz
perl -lane 'if(/^>(\w+)\s.+TaxID\=(\d+)/){print "$1 $2"}' <(zcat uniref90.fasta.gz) | gzip > uniref90.fasta.taxlist.gz
diamond makedb --in uniref90.fasta.gz -d uniref90.fasta.dmnd
```

## Lichen reference database
Lichen reference genome database (lichendb) was generated using reference genomes sourced from NCBI and JGI.
JGI Genomes were downloaded to supplement families that were not found in NCBI. This requires a valid JGI account and log in details, but can be downloaded using the JGI API (find download options [here](https://genome.jgi.doe.gov/portal/help/download.jsf#/api))


### Accession numbers

|Reference | NCBI Accession| JGI Link | Total Size |
|---|---|---|---|
|Escherichia phage (Sinsheimervirus) phiX174, complete genome|GCA_000819615.1| --| 6 KB|
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


The final databases are available on [zenodo](https://zenodo.org/records/14192492) and can be downloaded using the file [lichen_reference_genomes.csv](https://github.com/Kamouyiaraki/DEFRALichens/blob/main/databases/ref/lichen_reference_genomes.csv). 

```
wget -i lichen_reference_genomes.csv
```

**Compiling lichendb from scratch:** 

All scripts referenced are available in `/scripts/`

```
## Extract TaxID column efficiently and remove header in one step
awk -F"	" 'NR>1 {print $4}' scaffold_reference_genomes.txt > scaffold_ref_genomes.txt

## Run taxonkit commands efficiently
TAXONKIT_DB="./apps/bin/taxonkit_db"
./apps/bin/taxonkit lineage scaffold_ref_genomes.txt --data-dir "$TAXONKIT_DB" | \
./apps/bin/taxonkit reformat --data-dir "$TAXONKIT_DB" > scaffold_ref_genomes_lineages_reformat.txt

## Create required directories using a loop
declare -A directories=(
    ["Basidiomycota"]=('Basidiomycetes' 'Urediniomycetes')
    ["Ascomycota"]=('Coniocybomycetes' 'Dothideomycetes' 'Eurotiomycetes' 'Lecanoromycetes' 'Leotiomycetes' 'Lichinomycetes' 'Sordariomycetes' 'Thelocarpaceae')
)

for phylum in "${!directories[@]}"; do
    mkdir -p "$phylum"
    for class in "${directories[$phylum][@]}"; do
        mkdir -p "$phylum/$class"
    done
done

## Run Python scripts
python3.8 lichen_groups.py
python3.8 subset_references.py

## Accession retrieval and genome download
bash get_accessions.sh
bash download_genomes.sh

## Clean up zip files and concatenate genomes
rm -r *.zip
bash cat_genomes.sh

## Move and clean genome directories using a loop
for dir in Bimnz1 Veren1 Cocba1 Parmar1 Grascr1 Atrpi1 Lopnit1_1 Bulin1 Cocst1 Pseel1 Spafl1 Themi1 Elyde1 \
            Greab1 Greabi1 Psever1 PseVKM3775_1 PseVKM4514_1 Thest1 Nieex1; do
    if [ -d "$dir" ]; then
        find "$dir/" -type f -exec mv {} ./// \;
        rm -r "$dir"
    fi
done
```


**Makeblastdb Lichen DB**

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


## JGI Terms and Conditions to be aware of:

> By accessing JGI data, you agree not to publish any articles containing analyses of genes or genomic data prior to publication by the principal investigators of its comprehensive analysis without the consent of the project's principal investigator(s). These restrictions will be lifted upon publication(s) of the dataset or two years after the public release of this data, whichever is first. Scientists are expected to contact the principal investigator about their intentions to include any data from this project in a publication prior to publication of the primary report in order to ensure that their publication does not compete directly with planned publications (e.g. reserved analyses) of the principal investigators.

> If these data are used for publication, the following acknowledgment should be included: ‘These sequence data were produced by the US Department of Energy Joint Genome Institute https://www.jgi.doe.gov/ in collaboration with the user community.’ We also request that you appropriately cite any JGI resources used for analysis (such as IMG, Phytozome or Mycocosm) and that you notify us upon publication.

