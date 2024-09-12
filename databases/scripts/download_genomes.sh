#!/bin/bash

#SBATCH --job-name=Download_genomes
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=m.kamouyiaros@nhm.ac.uk
#SBATCH --output=downloads_%j_%a.out
#SBATCH --error=downloads_%j_%a.err
#SBATCH --mem-per-cpu=120G
#SBATCH --cpus-per-task=24
#SBATCH -p day

for f in $(find . -name *genome_accessions.txt)
do
	../../../../../users/marik2/apps/bin/datasets download genome accession --inputfile "$f" --filename "{$f%%}_outgroup_genomes.zip"
done
