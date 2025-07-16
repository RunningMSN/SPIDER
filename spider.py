import argparse
from helpers.db_functions import download_vfdb, extract_species, prepare_custom_db
from helpers.crawler import crawl
from helpers.assembly_list_funcs import parse_list, list_exists
from helpers.fasta_extract import extract_sequences
import sys
import os
import time
import pandas as pd

# Parse args
parser = argparse.ArgumentParser(description='Sliding Primer In-silico Detection of Encoded Regions (SPIDER) - Uses in-silico PCR with sequential primers to identify virulence factors')
parser.add_argument("-d", "--download", action='store_true', help='Downloads a current copy of the VFDB.')
parser.add_argument("-f", "--fasta",  type=str, required=False, help='Path to FASTA file which will be scanned for virulence factors.')
parser.add_argument("-l", "--list",  type=str, required=False, help='Path to txt file containing a list of paths to FASTA files to identify virulence factors. Each FASTA file should be on a new line.')
parser.add_argument("-s", "--species",  type=str, required=False, help='Extract a set of particular species from VFDB. Must be supplied in quotation marks such as "Staphylococcus aureus"')
parser.add_argument("-v", "--virulence_factor", type=str, required=False, help='Search for a specific virulence factor.')
parser.add_argument("-c", "--custom_db", type=str, required=False, help='Search for sequences in a custom database. Expected in fasta or fasta.gz format.')
parser.add_argument("-sl", "--slide_limit", type=float, required=False, default=5, help='Percent length of virulence factor that primers are allowed to slide. Default is 5%%.')
parser.add_argument("-lt", "--length", type=float, required=False, default=20, help='Percent length tolerance. Default: 20%% (Range of 80-120%%)')
parser.add_argument("-it", "--identity", type=float, required=False, default=0, help='Percent identity tolerance for calling true match. Anything about this threshold will be called positive hit. Default: 0%%')
parser.add_argument("-p", "--primer_size", type=int, required=False, default=20, help='Length of primer to use. Default: 20bp')
parser.add_argument("-o", "--output", type=str, required=False, help='Output file/folder. For SPIDER this will be a tab-separated values table. Default: stdout')
parser.add_argument("--pcr", type=str, required=False, help='Perform simple in-silico PCR. Assumed input as a text file in the format: target forward_primer reverse_primer')
parser.add_argument("--fasta_extract", type=str, required=False, help='Uses SPIDER output file as input to generate a FASTA file with sequences of the desired sequences.')
parser.add_argument("--translate", action='store_true', help='Translate fasta_extract to amino acid sequence rather than nucleotides. Assumes that the sequence begins with the start codon.')
args = parser.parse_args()

# Print help menu if no arguments supplied
if len(sys.argv) == 1:
    parser.print_help()

# Print error message if supplied species and virulence factor, but did not supply an assembly
if (not args.fasta and not args.list) and (args.species or args.virulence_factor or args.custom_db):
    print(f"ERROR: An assembly file (FASTA) or list of assemblies must be specified to identify virulence factors/sequences.")
    sys.exit(1)

# Run download
if args.download:
    print("Beginning to download a current version of the Virulence Factor Database (VFDB).")
    download_vfdb()
    print("Download was successfully completed.")

# Run SPIDER
if args.fasta or args.list:
    # Check that only one was provided
    if args.fasta and args.list:
        print(f"ERROR: Both fasta and list were provided. Please only choose 1.")
        sys.exit(1)

    # Check that assembly file exists
    if args.fasta:
        if not os.path.exists(args.fasta):
            print(f"ERROR: Could not find an assembly file located at {args.fasta}")
            sys.exit(1)
    elif args.list:
        if not os.path.exists(args.list):
            print(f"ERROR: Could not find assembly list located at {args.list}")
            sys.exit(1)
    elif args.custom_db:
        if not os.path.exists(args.custom_db):
            print(f"ERROR: Could not find database located at {args.custom_db}")
            sys.exit(1)

    # Check for mode to run
    if args.species and args.virulence_factor:
        print(f"ERROR: SPIDER supports either all VFs for a species or a specific VF, but not both. Please either use the -s/--species or -v/--virulence_factor arguments, but not both.")
        sys.exit(1)

    elif (args.species or args.virulence_factor) and args.custom_db:
        print(f"ERROR: If using a custom database, do not specify a species or virulence factor.")
        sys.exit(1)

    # Grab all VFs for a particular species
    elif args.species:
        # Number of VFs for the species
        count, crawl_db_loc = extract_species(args.species)
        
        # Print output for VFs extracted
        if count == 0:
            print(f"ERROR: The species {args.species} does not have any VFs in VFDB. Please check your spelling.")
            sys.exit(1)
        else:
            print(f"{count} VFs were identified for {args.species}.")

    # Grab specific VF of interest
    elif args.virulence_factor:
        # TODO: Make this more robust, for now treat the VF like a species (lookup by string in header) and use that
        count, crawl_db_loc = extract_species(args.virulence_factor)
        
        # Print output for VFs extracted
        if count == 0:
            print(f"ERROR: The VF {args.virulence_factor} does not have any matches in VFDB. Please check your spelling.")
            sys.exit(1)
        else:
            print(f"{count} VFs were identified for {args.virulence_factor}.")

    # Grab custom database
    elif args.custom_db:
        count, crawl_db_loc = prepare_custom_db(args.custom_db)

        # Print output for custom sequences identified
        if count == 0:
            print(f"ERROR: The species {args.custom_db} does not have any VFs in VFDB. Please check your spelling.")
            sys.exit(1)
        else:
            print(f"{count} sequences were identified for {args.custom_db}.")

    # Error if nothing supplied
    else:
        print(f"ERROR: You must supply either the name of a species using -s/--species, virulence factor using -v/--virulence_factor or custom database using -c/--custom_db.")
        sys.exit(1)

    # Track run time
    start_time = time.time()
    
    # Run the crawler
    print(f"Beginning to crawl using the following settings:")
    print(f"Primer Size: {args.primer_size}bp")
    print(f"Slide Limit: {args.slide_limit}%")
    print(f"Length Limit: {args.length}%")
    print(f"Identity Limit: {args.identity}%")
    ## Individual assembly
    if args.fasta:
        results = crawl(args.fasta, crawl_db_loc, args.slide_limit, args.length, args.identity, args.primer_size)
    ## List of assemblies
    elif args.list:
        # Parse list of assemblies
        fasta_list = parse_list(args.list)
        # Check to make sure all assemblies exist, if not exit and warn user
        valid_list, errors = list_exists(fasta_list)
        if not valid_list:
            print(f"ERROR: The following assemblies in the provided list could not be found: {','.join(errors)}")
            sys.exit(1)

        # Print number of samples identified
        print(f"Identified {len(fasta_list)} assemblies to crawl.")
        # Run crawler
        all_results = []
        count = 0
        for assembly in fasta_list:
            all_results.append(crawl(assembly, crawl_db_loc, args.slide_limit, args.length, args.identity, args.primer_size))
            count +=1 
            print(f"Completed {count} of {len(fasta_list)} ({round(count/len(fasta_list)*100, 2)}%)")
        results = pd.concat(all_results, ignore_index=True)

    # Output results
    ## If no file selected, print to stdout
    if not args.output:
        print(results.to_csv(sep="\t", index=None))
    ## Print to output file
    else:
        results.to_csv(args.output, sep="\t", index=None)
    
    # Remove DB coby
    os.remove(crawl_db_loc)
    
    # Print complete message
    print(f"SPIDER has finished running in {round(time.time() - start_time, 2)} seconds.")

# Extract sequences
if args.fasta_extract:
    obtained_seqs = extract_sequences(args.fasta_extract, args.translate, args.output)

    if obtained_seqs:
        print(f"Successfully extracted sequences from {args.fasta_extract}")