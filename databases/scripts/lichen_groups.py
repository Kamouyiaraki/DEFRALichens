import pandas as pd
import os

# Merge dataframes (Genbank accession table download + taxIDs from taxonkit with reformatted lineage)
df1 = pd.read_csv('scaffold_reference_genomes.txt', sep='\t')
df2 = pd.read_csv('scaffold_ref_genomes_lineages_reformat.txt', sep='\t', names=["Organism Taxonomic ID", "Lineage", "Rfmt_Lineage"])

df2[["Family_only"]] = df2["Rfmt_Lineage"].str.split(";", expand=True)[[4]].astype(object)


# Merge dataframes
merged_df = pd.merge(df1, df2, on='Organism Taxonomic ID')
merged_df.to_csv("scaffold_reference_genomes_lineages.csv", sep=",", index=False) 

class_list = ["Coniocybomycetes", "Dothideomycetes", "Eurotiomycetes", "Lecanoromycetes", "Leotiomycetes", "Lichinomycetes", "Sordariomycetes", "Thelocarpaceae"]

for x in class_list:
    # Assuming you want to filter rows where the 'Lineage' column contains the class name
    subset_df = merged_df[merged_df['Lineage'].str.contains(x, na=False)]
    
    # Define the output file path
    file_path = f"Ascomycota/{x}/{x}.csv"
    
    # Write the subset dataframe to a CSV file
    subset_df.to_csv(file_path, sep=',', header=True, index=False)


class_list2 = ["Hygrophoraceae", "Tricholomataceae", "Atheliaceae", "Coniophoraceae", "Jaapiaceae", "Tremellaceae"]

for y in class_list2:
    # Assuming you want to filter rows where the 'Lineage' column contains the class name
    subset_df2 = merged_df[merged_df['Lineage'].str.contains(y, na=False)]
    
    # Define the output file path
    file_path2 = f"Basidiomycota/Basidiomycetes/{y}.csv"
    
    # Write the subset dataframe to a CSV file
    subset_df2.to_csv(file_path2, sep=',', header=True, index=False)

#check - not run:
#print(merged_df[merged_df['Lineage'].str.contains('Tremellaceae', case=False, na=False)])

class_list3 = ["Chionosphaeraceae", "Pucciniaceae"]

for z in class_list3:
    # Assuming you want to filter rows where the 'Lineage' column contains the class name
    subset_df3 = merged_df[merged_df['Lineage'].str.contains(z, na=False)]
    
    # Define the output file path
    file_path3 = f"Basidiomycota/Urediniomycetes/{z}.csv"
    
    # Write the subset dataframe to a CSV file
    subset_df3.to_csv(file_path3, sep=',', header=True, index=False)
