# Settings
VFDB_NT_URL = "https://www.mgc.ac.cn/VFs/Down/VFDB_setA_nt.fas.gz"
VFDB_FOLDER_NAME = "VFDB"
VFDB_DATABASE_FILE_NAME = "VFDB_setA_nt.fas.gz"


# Helpers
VFDB_LOC = VFDB_FOLDER_NAME + "/" + VFDB_DATABASE_FILE_NAME

blast_columns_fmt_6 = [
    "qseqid",    # Query sequence ID
    "sseqid",    # Subject (database) sequence ID
    "pident",    # Percentage of identical matches
    "length",    # Alignment length
    "mismatch",  # Number of mismatches
    "gapopen",   # Number of gap openings
    "qstart",    # Start of alignment in query
    "qend",      # End of alignment in query
    "sstart",    # Start of alignment in subject
    "send",      # End of alignment in subject
    "evalue",    # Expectation value (E-value)
    "bitscore"   # Bit score
]