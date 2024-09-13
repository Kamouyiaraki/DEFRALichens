find ./ncbi_dataset/ -type f -exec mv {} ./// \;
rm -r ./ncbi_dataset/
rm -r *json*

gunzip *.fasta.gz
cat *.f*a > concatenated_genomes.fa
rm -r *.fna
rm -r *.fasta
rm -r *.zip
