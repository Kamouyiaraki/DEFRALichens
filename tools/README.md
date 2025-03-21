## Extra tools used

### Java code for extracting all URLs from a website

- Open the console by pressing `F12`
- In console paste the javascript `get_urls.js` (found at: https://www.datablist.com/learn/scraping/extract-urls-from-webpage)
- Copy and paste the output into a `.csv` file
  
### R scripts used to filter which JGI genomes to download
- JGI_genomes_to_download.R
- JGI_metadata.R
- files_used/JGI.csv
- files_used/jgi_website_links.csv

### Python script for pulling NCBI taxIDs 
- get_taxids_per_batch.py
- Relies on [taxonkit](https://bioinf.shenwei.me/taxonkit/)
- Retrieves taxids and appends to master input spreadsheet (output = `.csv`)
- Also outputs `.csv` of taxonomic names with null taxids


### R script for pulling GBIF metadata based on taxonomic name 
- Source function `get_gbifid_out()` in check_gbif_ids.R
- Relies on [taxize](https://cran.r-project.org/package=taxize)
- Run on a csv file of taxonomic names (column 1 = Taxonomic_name)
- Output is in the format of: `*_Lichen_Tracking_Sheet_null_taxids_gbif.csv`

```
#get all files with taxids in directory
filelist <- list.files(pattern = "_Lichen_Tracking_Sheet_null_taxids.csv")

#initiate loop
f<-1

#for each file run get_gbifid_out() 
for(f in 1:length(filelist)){
  fbase <- tools::file_path_sans_ext(filelist[f])
  fout <- paste0(fbase, "_gbif.xlsx")
  
  get_gbifid_out(csv_file = filelist[f], out_file=fout)
}
```


### R function for populating TaxIDs into metadata sheets
- Source function `fill_taxid_column()` in fill_taxid_column.R
- Fill taxid column in master tracking sheet (i.e., master sheet with sample ID, sequencing name (novogene name), sample metadata and taxonomic name used with TaxIDs from 2 other spreadsheets of newly registered TaxIDs & TaxIDs that already existed for each taxonomic name.

    **Important information to consider is column names for each of the spreadsheets:**
1. Metadata spreadsheet requires the columns: `Taxonomic_name`, `TaxID`
2. Existing TaxID spreadhseet requires the columns: `taxa`, `TaxID`, `accepted_name_IF`
3. Registered TaxID spreadhseet requires the columns: `Taxonomic_name`, `TaxID`


### Get Illumina indexes from spreadsheet using CSV2FASTA
- csv2fasta.py
- single index: `python csv2fasta.py -i input.csv -n Name -s Sequence -o /path/to/output`
- forward and reverse fasta usage: `python csv2fasta.py -i input.csv -n ID -f Forward -r Reverse -o /path/to/output`
- `-w` flag is available for both to wrap FASTA output instead of produce single line FASTA
