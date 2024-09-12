dbcsvs=(
"Ascomycota/Coniocybomycetes/Coniocybomycetes.csv"
"Ascomycota/Dothideomycetes/Reduced_Dothideomycetes.csv"
"Ascomycota/Eurotiomycetes/Reduced_Eurotiomycetes.csv"
"Ascomycota/Lecanoromycetes/Reduced_Lecanoromycetes.csv"
"Ascomycota/Leotiomycetes/Reduced_Leotiomycetes.csv"
"Ascomycota/Lichinomycetes/Lichinomycetes.csv"
"Ascomycota/Sordariomycetes/Reduced_Sordariomycetes.csv"
"Ascomycota/Thelocarpaceae/Thelocarpaceae.csv"
"Basidiomycota/Basidiomycetes/Atheliaceae.csv"
"Basidiomycota/Basidiomycetes/Coniophoraceae.csv"
"Basidiomycota/Basidiomycetes/Hygrophoraceae.csv"
"Basidiomycota/Basidiomycetes/Jaapiaceae.csv"
"Basidiomycota/Basidiomycetes/Tremellaceae.csv"
"Basidiomycota/Basidiomycetes/Reduced_Tricholomataceae.csv"
"Basidiomycota/Urediniomycetes/Chionosphaeraceae.csv"
"Basidiomycota/Urediniomycetes/Pucciniaceae.csv"
)


for f in "${dbcsvs[@]}"
do
	awk -F"," '{print $1}' "$f" | tail -n +2 > "${f%%.*}_genome_accessions.txt"
done

cat Basidiomycota/Basidiomycetes/*_genome_accessions.txt > Basidiomycota/Basidiomycetes/Basidiomycetes_genome_accessions.txt
cat Basidiomycota/Urediniomycetes/*_genome_accessions.txt > Basidiomycota/Urediniomycetes/Urediniomycetes_genome_accessions.txt
