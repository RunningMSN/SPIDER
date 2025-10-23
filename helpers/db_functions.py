from helpers.settings import DATABASE_DESCRIPTIONS, DATABASE_FILENAMES, DATABASE_URL, SPIDER_DBS_FOLDER
import os
from urllib.request import urlretrieve
import gzip
import sys
import uuid
from Bio import SeqIO

def list_databases():
    """
    Reutrns a list of available databases. Each database is on a new line with its
    name and brief description.

    Arguments:
        none
    
    Returns:
        db_list - String containing database name - description each on a new line
    """
    
    return "\n".join([f"{key} - {value}" for key, value in DATABASE_DESCRIPTIONS.items()])

def get_database(db_name):
    """
    Returns the location of a database.

    Arguments:
        db_name -  Name of the database queried

    Returns:
        path - Path to the database
    """

    # Returns none if there is no special database with the request name
    if not db_name in DATABASE_DESCRIPTIONS.keys():
        return None
    # If database is not downloaded, then download it
    if not check_downloaded(db_name):
        print(f"The database {db_name} was not downloaded. Download will now be attempted.", file=sys.stderr)
        try:
            download_db(db_name)
            print(f"Successfully downloaded {db_name}.", file=sys.stderr)
        except:
            print(f"An error occurred while attempting to download {db_name}. Please try again later, or use a pre-downloaded fasta database.", file=sys.stderr)
            sys.exit(1)
    return f"{SPIDER_DBS_FOLDER}/{DATABASE_FILENAMES[db_name]}"

def check_downloaded(db_name):
    """
    Checks if a database with db_name is already downloaded.

    Arguments:
        db_name - Name of the requested database
    
    Return:
        True/False if the database is downloaded.
    """
    # Find the location where the DB should be 
    return os.path.exists(f"{SPIDER_DBS_FOLDER}/{DATABASE_FILENAMES[db_name]}")

def download_db(db_name):
    """
    Downloads a database with requested db_name

    Arguments:
        db_name - Name of the requested database
    """
    os.makedirs(f"{SPIDER_DBS_FOLDER}", exist_ok=True)
    
    urlretrieve(DATABASE_URL[db_name], f"{SPIDER_DBS_FOLDER}/{DATABASE_FILENAMES[db_name]}") # In future add versioning to this

def open_correct_format(file):
    """
    Opens files correctly if they are gzipped.
    """
    if file.endswith(".gz"):
        return gzip.open(file, 'rt')
    else:
        return open(file, 'r')
    
def prepare_db(database_loc, search_term):
    """
    Prepares database for SPIDER search. If a search term is specified, only
    sequences with the search term in the fasta header will be included.

    Arguments:
        search_term - String to look for in fasta headers
        database_loc - Database to search

    Returns:
        count -- Number of VFs belonging to the search_term
        tmp_db -- Location of the output database for SPIDER
    """
    # If don't have the output folder yet, create it
    os.makedirs(SPIDER_DBS_FOLDER, exist_ok=True)

    # Temporary db location
    tmp_db = f"{SPIDER_DBS_FOLDER}/spider_tmpdb_{uuid.uuid4().hex}.fasta"

    # Write to the temp db and count sequences included
    count = 0
    with open(tmp_db, "w") as out_db:
        with open_correct_format(database_loc) as handle:
            for record in SeqIO.parse(handle, "fasta"):
                if search_term:
                    if search_term.lower() in record.description.lower():
                        out_db.write(f">{record.description}\n{record.seq}\n")
                        count += 1
                else:
                    out_db.write(f">{record.description}\n{record.seq}\n")
                    count += 1

    return count, tmp_db