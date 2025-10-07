import argparse
from helpers.db_functions import prepare_db, list_databases, get_database
from helpers.crawler import crawl
from helpers.assembly_list_funcs import parse_list, list_exists, parse_directory
from helpers.fasta_extract import extract_sequences
from helpers.settings import DATABASE_DESCRIPTIONS
import sys
import os
import time
import pandas as pd
import re
import shutil

# Parse args
parser = argparse.ArgumentParser(description='Sliding Primer In-silico Detection of Encoded Regions (SPIDER) - Uses in-silico PCR with sequential primers to identify virulence factors')
# Query options
parser.add_argument("-f", "--fasta",  type=str, required=False, help='Path to FASTA file which will be scanned for virulence factors.')
parser.add_argument("-l", "--list",  type=str, required=False, help='Path to txt file containing a list of paths to FASTA files to identify virulence factors. Each FASTA file should be on a new line.')
parser.add_argument("-d", "--directory",  type=str, required=False, help='Path to directory containing assemblies in FASTA format (.fasta/.fna)')
# Database options
parser.add_argument("-db", "--database", type=str, required=False, help='Specifies the reference database to use. Database is expected in fasta or fasta.gz format. Special databases can be called using their name. For a list of available special databases, use the command --list_dbs.')
parser.add_argument( "--list_dbs", action='store_true', required=False, help='Lists available special databases.')
parser.add_argument("-s", "--search",  type=str, required=False, help='Extract a set of VFs from VFDB based on a search term. Terms with spaces must be in quotations "Staphylococcus aureus". This is HIGHLY RECOMMENDED if using any non-custom databases.')
# Crawl options
parser.add_argument("-sl", "--slide_limit", type=float, required=False, default=5, help='Percent length of virulence factor that primers are allowed to slide. Default is 5%%.')
parser.add_argument("-lt", "--length", type=float, required=False, default=20, help='Percent length tolerance. Default: 20%% (Range of 80-120%%)')
parser.add_argument("-it", "--identity", type=float, required=False, default=0, help='Percent identity tolerance for calling true match. Anything about this threshold will be called positive hit. Default: 0%%')
parser.add_argument("-p", "--primer_size", type=int, required=False, default=20, help='Length of primer to use. Default: 20bp')
parser.add_argument("--overlaps", action='store_true', required=False, help='Search results for overlapping in silico amplicons. Default: False')
# Output options
parser.add_argument("-o", "--output", type=str, required=False, help='Output file/folder. For search this will be a tab-separated values table. For extract, this will be FASTA formatted. Default: stdout')
# Extract options
parser.add_argument("-e", "--extract", type=str, required=False, help='Uses SPIDER output file as input to generate a FASTA file with sequences of the desired sequences.')
parser.add_argument("--translate", action='store_true', required=False, help='Translate extract to amino acid sequence rather than nucleotides. Assumes that the sequence begins with the start codon. Default: False')
parser.add_argument("--separate", action='store_true', required=False, help='Separate extracted sequences into separate files for each target. Default: False')
parser.add_argument("--overwrite", action='store_true', required=False, help='Separate extracted sequences into separate files for each target. Default: False')
args = parser.parse_args()

# Print help menu if no arguments supplied
if len(sys.argv) == 1:
    parser.print_help()


# Run SPIDER search
## Print available databases
if args.list_dbs:
    print(list_databases())
## Run SPIDER crawler
elif args.fasta or args.list or args.directory:
    # Check that only one input format was provided
    num_assembly_format_provided = 0
    if args.fasta: num_assembly_format_provided += 1
    if args.list: num_assembly_format_provided += 1
    if args.directory: num_assembly_format_provided += 1

    # Check for input errors
    input_errors = 0
    ## Too many inputs
    if num_assembly_format_provided > 1:
        print(f"ERROR: Multiple inputs were provided (single fasta/list/directory). Please only select one.",  file=sys.stderr)
        input_errors += 1
    ## Too few inputs
    if num_assembly_format_provided == 0:
        print(f"ERROR: An assembly file (FASTA), list of assemblies, or directory contain assemblies must be specified to identify virulence factors/sequences.",  file=sys.stderr)
        input_errors +=1

    ## No database specified
    if not args.database:
        print(f"ERROR: You must provide a reference database. This can be in FASTA (or gzipped FASTA) format. For a list of special databases you can choose from, use the --list_dbs command.",  file=sys.stderr)
        input_errors += 1
    ## Check that the database exists
    elif not args.database in DATABASE_DESCRIPTIONS.keys():
        if not os.path.exists(args.database):
            print(f"ERROR: The database {args.database} could not be found. Please check that this file exists.", file=sys.stderr)

    ## FASTA specified, but could not locate
    if args.fasta:
        if not os.path.exists(args.fasta):
            print(f"ERROR: Could not find an assembly file located at {args.fasta}", file=sys.stderr)
            input_errors += 1
    ## List specified, but could not locate
    elif args.list:
        if not os.path.exists(args.list):
            print(f"ERROR: Could not find assembly list located at {args.list}", file=sys.stderr)
            input_errors += 1
    ## Directory specified, but doesn't exist
    elif args.directory:
        if not os.path.exists(args.directory):
            print(f"ERROR: Could not find directory located at {args.directory}", file=sys.stderr)
            input_errors += 1

    # If input errors exist, end the program.
    if input_errors > 0:
        sys.exit(1)

    # Set the database for the run, and download if needed
    if args.database in DATABASE_DESCRIPTIONS.keys():
        database_loc = get_database(args.database)
    else:
        database_loc = args.database

    # Prepare the reference database
    search_term = None
    if args.search:
        search_term = args.search
    count, temp_crawl_db = prepare_db(database_loc, search_term)

    # Check that the database is not empty
    if count == 0:
        if args.search:
            print(f"ERROR: No sequences for {args.search} were found in {args.database}.", file=sys.stderr)
        else:
            print(f"ERROR: The database {args.database} was empty.", file=sys.stderr)
        os.remove(temp_crawl_db)
        sys.exit(1)

    # Track run time
    start_time = time.time()
    
    # Run the crawler
    print(f"Beginning to crawl using the following settings:", file=sys.stderr)
    print(f"Primer Size: {args.primer_size}bp", file=sys.stderr)
    print(f"Slide Limit: {args.slide_limit}%", file=sys.stderr)
    print(f"Length Limit: {args.length}%", file=sys.stderr)
    print(f"Identity Limit: {args.identity}%", file=sys.stderr)
    ## Individual assembly
    if args.fasta:
        results = crawl(args.fasta, temp_crawl_db, args.slide_limit, args.length, args.identity, args.primer_size, args.overlaps)
    ## List of assemblies
    elif args.list or args.directory:
        # Parse list of assemblies
        if args.list:
            fasta_list = parse_list(args.list)
            # Check to make sure all assemblies exist, if not exit and warn user
            valid_list, errors = list_exists(fasta_list)
            if not valid_list:
                print(f"ERROR: The following assemblies in the provided list could not be found: {','.join(errors)}", file=sys.stderr)
                sys.exit(1)
        elif args.directory:
            fasta_list = parse_directory(args.directory)
            if len(fasta_list) == 0:
                print(f"ERROR: The directory {args.directory} did not contain any fasta files. Check that files exist that end in .fasta or .fna.", file=sys.stderr)
                sys.exit(1)

        # Print number of samples identified
        print(f"Identified {len(fasta_list)} assemblies to crawl.", file=sys.stderr)
        # Run crawler
        all_results = []
        count = 0
        for assembly in fasta_list:
            all_results.append(crawl(assembly, temp_crawl_db, args.slide_limit, args.length, args.identity, args.primer_size))
            count +=1 
            print(f"Completed {count} of {len(fasta_list)} ({round(count/len(fasta_list)*100, 2)}%)", file=sys.stderr)
        results = pd.concat(all_results, ignore_index=True)

    # Output results
    ## If no file selected, print to stdout
    if not args.output:
        print(results.to_csv(sep="\t", index=None))
    ## Print to output file
    else:
        results.to_csv(args.output, sep="\t", index=None)
    
    # Remove DB coby
    os.remove(temp_crawl_db)
    
    # Print complete message
    end_time = time.time()
    if end_time - start_time <= 60:
        print(f"SPIDER has finished running in {round(end_time - start_time, 2)} seconds.", file=sys.stderr)
    else:
        print(f"SPIDER has finished running in {round((end_time - start_time)/60, 2)} minutes.", file=sys.stderr)

# Run SPIDER extract
if args.extract:
    # Validate the extraction arguments
    error = False
    illegal_folder_characters = re.compile(r"[<>/{}[\]~`.]")
    if args.separate and not args.output:
        print("ERROR: If using --separate, you must specify the name of an output folder using the -o/--output argument.", file=sys.stderr)
        error = True
    elif args.separate and illegal_folder_characters.search(args.output):
        print("ERROR: If using --separate, the output is a folder. Your folder name contains illegal characters, please remove them.", file=sys.stderr)
        error = True
    elif args.output:
        if os.path.exists(args.output):
            if args.overwrite and os.path.isdir(args.output):
                shutil.rmtree(args.output)
            elif args.overwrite and os.path.isfile(args.output):
                os.remove(args.output)
            else:
                print("ERROR: The output location already exists. If you would like to overwrite it, please use the --overwrite argument.", file=sys.stderr)
                error = True

    # If error in arguments, exit the program
    if error: sys.exit(1)

    # Extract sequences
    obtained_seqs = extract_sequences(args.extract, args.translate, args.output, args.separate)

    # Print success message
    if obtained_seqs:
        print(f"Successfully extracted sequences from {args.extract}", file=sys.stderr)
    else:
        print(f"Could not extract sequences from {args.extract} due to an error.", file=sys.stderr)