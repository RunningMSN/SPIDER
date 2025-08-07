from helpers.settings import VFDB_NT_URL, VFDB_FOLDER_NAME, VFDB_LOC
import os
from urllib.request import urlretrieve
import gzip
import sys
import uuid

def download_vfdb():
    """
    Downloads the current version of the VFDB.
    """
    # Make folder for output
    os.makedirs(f"{VFDB_FOLDER_NAME}", exist_ok=True)
    urlretrieve(VFDB_NT_URL, f"{VFDB_LOC}") # In future add versioning to this


def check_downloaded():
    """
    Checks if the VFDB has been downloaded.
    
    returns: True if VFDB has been downloaded.
    """

    if os.path.exists(VFDB_LOC):
        return True
    else:
        return False


def extract_vfs(search_term):
    """
    Creates a limited database of VFs unique to a specific search. 
    If exists, will overwrite the previous database. Database is written
    in fasta format, however, the sequence is output in a single line to
    facilitate easier parsing later.

    Returns:
        count -- Number of VFs belonging to the search_term
        db_loc -- Location of the output database
    """
    # Make sure the base database exists first
    if not check_downloaded():
        print(f"ERROR: VFDB has not been downloaded. Please download the base database using the --download flag first.")
        sys.exit(1)

    # Output file name
    output_file = "VFDB_" + search_term.replace(" ", "_") + ".fasta"
    output_loc = f"{VFDB_FOLDER_NAME}/{output_file}"

    # Store VF count
    count = 0

    # Iterate through the base database and only store sequences with header that contains species of interest
    with open(output_loc, "w") as output:
        with gzip.open(f"{VFDB_LOC}", 'rt') as VFDB_file:
            correct_search = False
            for line in VFDB_file.readlines():
                # Checks headers
                if line.startswith(">"):
                    if search_term in line:
                        # If not first VF, add newline to separate from last VF
                        if count > 0:
                            output.write("\n")
                        output.write(line.strip() + "\n")
                        correct_search = True
                        count +=1 # Add to count
                    else:
                        correct_search = False
                # Print sequences if current header is correct search
                else:
                    if correct_search:
                        output.write(line.strip())

    return count, output_loc

def open_correct_format(file):
    if file.endswith(".gz"):
        return gzip.open(file, 'rt')
    else:
        return open(file, 'r')

def prepare_custom_db(custom_db_loc):
    """
    Prepares a custom database for SPIDER crawling. Expected that custom database
    is in fasta format.

    Arguments:
        custom_db_loc -- Path to the custom database
    
    Returns:
        count -- Number of sequences in the database
        db_loc -- Location of prepared database
    """

    count = 0
    temp_db_out = f"spider_tmp_customdb_{uuid.uuid4().hex}.fasta"

    with open_correct_format(custom_db_loc) as database:
        with open(temp_db_out, "w") as output:
            for line in database.readlines():
                # Checks headers
                if line.startswith(">"):
                    # If not first sequence, add newline to separate sequence
                    if count > 0:
                        output.write("\n")
                    output.write(line.strip() + "\n")
                    count +=1 # Add to count
                # Print sequences if current header is correct species
                else:
                    output.write(line.strip())

    return count, temp_db_out