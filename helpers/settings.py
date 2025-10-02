# Settings
VFDB_NT_URL = "https://www.mgc.ac.cn/VFs/Down/VFDB_setA_nt.fas.gz"
VFDB_FOLDER_NAME = "VFDB"
VFDB_DATABASE_FILE_NAME = "VFDB_setA_nt.fas.gz"


# Helpers
VFDB_LOC = VFDB_FOLDER_NAME + "/" + VFDB_DATABASE_FILE_NAME

BLAST_COLUMNS_FMT_6 = (
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
)

SPIDER_RESULTS_COLUMNS = (
	"Query",                # Name of query assembly
	"Name",                 # Name of search sequences/VF
	"Valid",                # SPIDER call of present/absent
	"Contig",               # SPIDER identified contig
	"Start",                # SPIDER identified start site
	"F_Slide",              # Forward slide in SPIDER
	"End",                  # SPIDER identified end site
	"R_Slide",              # Reverse slide in SPIDER
	"Strand",               # Strand SPIDER detected VF on
	"Identity",             # Identity between SPIDER sequence detected and reference
	"VF_length",            # Length of SPIDER detected sequence
	"Ref_Length",           # Length of reference seqeunce
	"Coverage_Perc_Len",    # Percentage length difference between SPIDER and reference sequence
	"Coverage_Perc_Align",  # Percentage coverage based on alignment between SPIDER and reference sequence
	"Message"               # SPIDER message for failures/warnings
	)
