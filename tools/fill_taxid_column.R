## Author: Maria Kamouyiaros
## Date: 2025-03-14
## Purpose: fill taxid column in master tracking sheet (i.e., master sheet with sample ID, sequencing name (novogene name), sample metadata and taxonomic name used with TaxIDs sourced from: 
##     (1) checking GBIF and IF for other names used 
##     (2) novel TaxIDs registered
## Important information to consider: column names for each of the spreadsheets. See example usage below. 

# Load required packages
library(dplyr)
library(readr)

fill_taxid_column <- function(main_file, registered_file, gbif_file, output_file) {

# Read the input files
main_df <- read.csv(main_file, header = T )
registered_df <- read.csv(registered_file, header = T)
gbif_df <- read.csv(gbif_file, header = T)

registered_df <- unique(registered_df)
gbif_df <- unique(gbif_df)

# Step 1: Match TaxIDs from 'Taxids_registered_unique.csv'
main_df <- main_df %>%
  left_join(registered_df %>% select(Taxonomic_name, TaxID), by = "Taxonomic_name") %>%
  mutate(TaxID = coalesce(TaxID.x, TaxID.y)) %>%
  select(-TaxID.x) %>%
  select(-TaxID.y)

# Step 2: Match TaxIDs from 'Batch_3_Lichen_Tracking_sheet_null_taxid_gbif_checked.csv'
main_df <- main_df %>%
  left_join(gbif_df %>% select(taxa, TaxID), by = c("Taxonomic_name" = "taxa")) %>%
  mutate(TaxID = coalesce(TaxID.x, TaxID.y)) %>%
  select(-TaxID.x) %>%
  select(-TaxID.y)

# Step 3: Add 'accepted_name_IF' as a fallback column
main_df <- main_df %>%
  left_join(gbif_df %>% select(taxa, accepted_name_IF), by = c("Taxonomic_name" = "taxa"))

# Step 4: Match TaxIDs from 'Taxids_registered_unique.csv' using 'accepted_nameIF'
main_df <- main_df %>%
  left_join(registered_df %>% select(Taxonomic_name, TaxID), by = c("accepted_name_IF" = "Taxonomic_name")) %>%
  mutate(TaxID = coalesce(TaxID.x, TaxID.y)) %>%
  select(-TaxID.x) %>%
  select(-TaxID.y) 

# Step 5: Match missing TaxIDs by trimming whitespaces from 'Taxonomic_name'
main_df <- main_df %>%
  mutate(Taxonomic_name = str_trim(Taxonomic_name)) 

main_df <- main_df %>%
  left_join(gbif_df %>% select(taxa, accepted_name_IF), by = c("Taxonomic_name" = "taxa")) %>%
  mutate(accepted_name_IF = coalesce(accepted_name_IF.x, accepted_name_IF.y)) %>%
  select(-accepted_name_IF.x) %>%
  select(-accepted_name_IF.y) 

main_df <- main_df %>%
  left_join(registered_df %>% select(Taxonomic_name, TaxID), by = c("accepted_name_IF" = "Taxonomic_name")) %>%
  mutate(TaxID = coalesce(TaxID.x, TaxID.y)) %>%
  select(-TaxID.x) %>%
  select(-TaxID.y)

# Write the updated data to a new CSV file
write.csv(main_df, output_file, row.names = F)

message("TaxID column filled successfully and saved to: ", output_file)
}


## Example usage:
#fill_taxid_column("Batch_1_Lichen_Tracking_Sheet_default.csv", "Taxids_registered.csv", "Taxids_existing.csv", "Batch_1_Lichen_Tracking_Sheet_filled.csv")
#"Batch_1_Lichen_Tracking_Sheet_default.csv" - column names: Taxonomic_name, TaxID, 
#"Taxids_existing.csv" - column names: taxa, TaxID, accepted_name_IF
#"Taxids_registered.csv" - column names: Taxonomic_name, TaxID
