rule NAME:
    input:
      sample_ids,
      sample_ids_col_num,
      project_dir,
      delimiter,
    log:
        "logs/blastdb/ids2csv.log",
    script:
        "scripts/ids2csv.py"
