##Author: M Kamouyiaros
##Date: 2024-10-11
##R-version: R version 4.3.0 (2023-04-21 ucrt) - Already Tomorrow
##Pacakges required: NA
##README: JGI lichen metagenomes metadata were downloaded as a table from the website ("JGI.csv") and all website links were downloaded using XXX ("jgi_website_links.csv"). 
##			The 2 files are then merged to produce a single file with genome information and associated download link.
##			The aim is to then use this data to obtain any taxa (family-level) genomes that are not available through NCBI. 
##			The next steps are to then use the Genus column to obtain lineage information using taxonkit (within UNIX) and filter by family to identify which genomes to download. 

JGI <- read.csv("JGI.csv", header = T)
links <- read.csv("jgi_website_links.csv", header = T)
colnames(links)[2] <- "Name"

###Combine links with metadata from JGI
JGI_df <- merge(JGI, links ,by="Name", all.x=TRUE, sort=FALSE)

###Create a Genus column to simplify downstream taxon filtering
JGI_df$Genus <- JGI_df$Name %>% strsplit(" ") %>% sapply("[", 1)
  #write.csv(JGI_df, "JGI_all_genomes.csv", row.names = F)