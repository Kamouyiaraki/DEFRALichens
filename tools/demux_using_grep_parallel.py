#!/usr/bin/env python3
import sys
import gzip
import csv

def open_fastq(filename):
    if filename.endswith('.gz'):
        return gzip.open(filename, 'rt')
    else:
        return open(filename, 'r')

def main(fastq_file, patterns_csv):
    # Read patterns and output filenames
    patterns = []
    out_files = []
    with open(patterns_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 2 or not row[0] or not row[1]:
                continue
            patterns.append(row[0])
            out_files.append(row[1])

    # Open all output files in write mode
    out_handles = [open(f, 'w') for f in out_files]

    try:
        with open_fastq(fastq_file) as fq:
            while True:
                # Read 4 lines = 1 FASTQ read
                lines = [fq.readline() for _ in range(4)]
                if lines[0] == '':
                    # EOF
                    break
                if any(line == '' for line in lines):
                    sys.stderr.write("Warning: Incomplete FASTQ record detected.\n")
                    break
                header = lines[0].strip()
                # Check if any pattern matches header line
                for pat, handle in zip(patterns, out_handles):
                    if pat in header:
                        handle.writelines(lines)
    finally:
        for handle in out_handles:
            handle.close()

    print("All matching reads have been extracted.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: demux_using_grep_parallel.py input.fastq[.gz] patterns.csv", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
