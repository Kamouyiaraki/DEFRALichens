rule all:
    input:
        "samples.csv"

rule ids2csv:
    input:
        project_dir=config["project_dir"],
        sample_ids=config["sample_ids"],
        column_name=config["column_name"],
        delimiter=config["delimiter"]
    output:
        "samples.csv"
    script:
        "scripts/ids2csv.py"
