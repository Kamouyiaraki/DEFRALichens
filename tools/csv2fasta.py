import csv
import argparse
import os
import textwrap

def process_csv(input_file, name_col, seq_col, output_dir, wrap, fwd_col=None, rev_col=None):
    """
    Process a CSV file and generate FASTA files.
    Handles both single FASTA and dual FASTA modes.
    """
    try:
        with open(input_file, "r", encoding="ascii") as csvfile:
            reader = csv.DictReader(csvfile)
            detected_columns = reader.fieldnames
            
            # Check if the required columns exist
            if name_col not in detected_columns:
                raise KeyError(f"Column '{name_col}' not found in the CSV. Detected columns: {detected_columns}")
            
            if seq_col and seq_col not in detected_columns:
                raise KeyError(f"Column '{seq_col}' not found in the CSV. Detected columns: {detected_columns}")
            
            if fwd_col and fwd_col not in detected_columns:
                raise KeyError(f"Column '{fwd_col}' not found in the CSV. Detected columns: {detected_columns}")
            
            if rev_col and rev_col not in detected_columns:
                raise KeyError(f"Column '{rev_col}' not found in the CSV. Detected columns: {detected_columns}")
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            if fwd_col and rev_col:
                # Dual FASTA mode
                fwd_file = os.path.join(output_dir, "forward_sequences.fasta")
                rev_file = os.path.join(output_dir, "reverse_sequences.fasta")
                
                with open(fwd_file, "w") as fwd_fasta, open(rev_file, "w") as rev_fasta:
                    for row in reader:
                        fwd_fasta.write(f">{row[name_col]}\n")
                        fwd_fasta.write(textwrap.fill(row[fwd_col], 100) if wrap else row[fwd_col] + "\n")
                        
                        rev_fasta.write(f">{row[name_col]}\n")
                        rev_fasta.write(textwrap.fill(row[rev_col], 100) if wrap else row[rev_col] + "\n")
                print(f"Dual FASTA files created: {fwd_file}, {rev_file}")
            
            else:
                # Single FASTA mode
                fasta_file = os.path.join(output_dir, "sequences.fasta")
                with open(fasta_file, "w") as fasta:
                    for row in reader:
                        fasta.write(f">{row[name_col]}\n")
                        fasta.write(textwrap.fill(row[seq_col], 100) if wrap else row[seq_col] + "\n")
                print(f"Single FASTA file created: {fasta_file}")
    
    except Exception as e:
        print(f"Error: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(
        description="Converts CSV files into FASTA files. Handles both single FASTA and dual FASTA modes."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to the input CSV file.")
    parser.add_argument("-n", "--name_column", required=True, help="Column name for sequence IDs.")
    parser.add_argument("-s", "--sequence_column", help="Column name for sequences (single FASTA mode).")
    parser.add_argument("-f", "--forward_column", help="Column name for forward sequences (dual FASTA mode).")
    parser.add_argument("-r", "--reverse_column", help="Column name for reverse sequences (dual FASTA mode).")
    parser.add_argument("-o", "--output_dir", required=True, help="Output directory for FASTA files.")
    parser.add_argument("-w", "--wrap", action="store_true", help="Wrap sequences to 100 characters per line.")
    
    args = parser.parse_args()

    # Determine FASTA mode
    dual = bool(args.forward_column and args.reverse_column)
    single = bool(args.sequence_column)

    if not dual and not single:
        parser.error("Either --sequence_column (single FASTA mode) or both --forward_column and --reverse_column (dual FASTA mode) must be specified.")
    
    try:
        process_csv(
            input_file=args.input,
            name_col=args.name_column,
            seq_col=args.sequence_column,
            output_dir=args.output_dir,
            wrap=args.wrap,
            fwd_col=args.forward_column,
            rev_col=args.reverse_column,
        )
    except Exception as e:
        print(f"Failed to process the CSV: {e}")

if __name__ == "__main__":
    main()


#single fasta usage:
#python csv2fasta.py -i input.csv -n Name -s Sequence -o /path/to/output
#forward and reverse fasta usage:
#python csv2fasta.py -i input.csv -n ID -f Forward -r Reverse -o /path/to/output
#-w to wrap fasta instead of single line fasta
