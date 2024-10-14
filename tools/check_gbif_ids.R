library(stringr)
library(dplyr)
library(taxize)
library(tools)

#Function to pull gbif metadata from taxonomic name

get_gbifid_out <- function(csv_file, out_file){

  df<- read.csv(csv_file, header = T)
  taxa <- as.vector(df$Taxonomic_name)

  gbiftaxID <- data.frame(taxa=taxa, gbif_id=rep(NA,length(taxa)))
  i<-1
  for(i in 1:length(taxa)){
  
    if(length(gbif_name_usage(name = gbiftaxID$taxa[i])$results) >0) {
      gbiftaxID$gbif_id[i] <- gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$taxonID
      gbiftaxID$authorship[i] <- gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$authorship
      gbiftaxID$lineage[i] <- paste(gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$kingdom,
                              gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$phylum,
                              gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$order,
                              gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$family,
                              gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$genus,
                              gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$species,
                              sep = ";")
      }else{
      gbiftaxID$gbif_id[i] <- NA
      }
    if(length(gbif_name_usage(name = gbiftaxID$taxa[i])$results) >0 && length(gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$publishedIn)>0) {
      gbiftaxID$reference[i] <- gbif_name_usage(name = gbiftaxID$taxa[i])$results[[1]]$publishedIn
    }
    
    
  }

  write.csv(gbiftaxID, out_file, row.names = F)
}

### Usage across files
#filelist <- list.files(pattern = "_Lichen_Tracking_Sheet_null_taxids.csv")
#f<-1
#for(f in 1:length(filelist)){
#  fbase <- tools::file_path_sans_ext(filelist[f])
#  fout <- paste0(fbase, "_gbif.csv")
#  
#  get_gbifid_out(csv_file = filelist[f], out_file=fout)
#}
