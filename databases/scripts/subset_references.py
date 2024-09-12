import pandas as pd
import os

# Define the list of CSV files
list_csvs = [
    "Ascomycota/Dothideomycetes/Dothideomycetes.csv",
    "Ascomycota/Eurotiomycetes/Eurotiomycetes.csv",
    "Ascomycota/Lecanoromycetes/Lecanoromycetes.csv",
    "Ascomycota/Leotiomycetes/Leotiomycetes.csv",
    "Ascomycota/Sordariomycetes/Sordariomycetes.csv",
    "Basidiomycota/Basidiomycetes/Tricholomataceae.csv"
]

# Loop through each CSV file
for x in list_csvs:
    df = pd.read_csv(x, sep=',')

    # Extract unique families
    unique_families = df['Family_only'].unique()
    print(f"{unique_families} in {x}")

    dfs = []

    for y in unique_families:
        dfsub = df[df['Family_only'] == y]
        print(y)

        # Case 1: Only one entry for this family
        if dfsub.shape[0] == 1:
            dfs.append(dfsub)
            print(f"There is only one available reference genome for {y}")

        # Case 2: Multiple entries for this family
        else:
            # Subset where 'Assembly Level' is 'Complete Genome' or 'Chromosome'
            dfsub2 = dfsub[(dfsub['Assembly Level'] == 'Complete Genome') | (dfsub['Assembly Level'] == 'Chromosome')]

            # If we have 'Chromosome' entries, prefer them
            if (dfsub2['Assembly Level'] == 'Complete Genome').any():
                dfs.append(dfsub2[dfsub2['Assembly Level'] == 'Complete Genome'])
                print(f"Appending 'Complete Genome' assembly level for {y}")

            # If no 'Chromosome' entries but we have 'Complete Genome', append them
            elif dfsub2.shape[0] > 0:
                dfsub3 = dfsub2[dfsub2['Assembly Level'] == 'Chromosome']
                dfs.append(dfsub3)
                print(f"Appending 'Chromosome' assembly level for {y}")
                
            # If no high-level assemblies, append whatever we have for this family
            else:
                dfs.append(dfsub)
                print(f"No high-level assemblies; appending all data for {y}")

            # Check if there are more than 10 entries for a family
            if dfsub2.shape[0] > 10:
                print(f"Lots of genome hits; manually curate {y} in {x}")

    # Concatenate all dataframes only if there are entries in dfs
    if len(dfs) > 0:
        final = pd.concat(dfs, ignore_index=True)

        # Extract unique families from the concatenated DataFrame
        unique_families_new = final['Family_only'].unique()

        if len(unique_families) == len(unique_families_new):
            print(f"All good here for {x}")
        else:
            print(f"Warning: Number of families differ after processing {x}")

        filename = os.path.basename(x)
        filepath = os.path.dirname(x)
        file_path = os.path.join(filepath, "Reduced_" + filename)
        final.to_csv(file_path, sep=',', index=False)
        print(f"Saved reduced file to: {file_path}")
    else:
        print(f"No data to save for {x}")
