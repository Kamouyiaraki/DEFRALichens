##Author: M Kamouyiaros
##Date: 2024-10-11
##R-version: R version 4.3.0 (2023-04-21 ucrt) - Already Tomorrow
##Pacakges required: dplyr
##README: The aim is to then use this data to download any family-level genomes that are not available through NCBI. 
##			Available taxa are filtered based on lineages obtained using taxonkit 
##			This script merges lineage data with JGI genome and metadata file generated in "JGI_metadata.R". 
##			The final output is a dataframe of genomes to download that can be parsed through and downloaded using `wget` (within UNIX) 

###load dplyr and data
library(dplyr)

JGI_df <- read.csv("JGI_all_genomes.csv", header = T, fill = T)
taxids <- read.table("jgi_out1.txt", header = T, fill = T)
lineages <- read.table("jgi_lineages_rfmt.txt", header = F, fill = T, sep="\t")

###rename colnames for merge 
colnames(taxids) <- c("Genus", "Taxids")
colnames(lineages) <- c("Taxids", "Lineage_full", "Lineage_rfmt")
lineages2 <- distinct(lineages)


###merge dataframes and pull out Family for each
taxid_lin <- merge(taxids, lineages2, by="Taxids", all.x = T, sort = F)
taxid_lin2 <- distinct(taxid_lin)
JGI_df2 <- merge(JGI_df, taxid_lin2, by = "Genus", all.x = T, sort = F)
JGI_df2$Family <- JGI_df2$Lineage_rfmt %>% strsplit(";") %>% sapply("[", 5)

### load in missing groups
df <- read.csv("Lichen_groups_refseq_missing.csv", header = T, fill = T)

missing <- merge(df, JGI_df2, by = "Family")
missing_fin <- missing[missing$Family != "",]
  #write.csv(missing_fin, "JGI_genomes_to_download.csv", row.names = F)