# Sliding Primer *In Silico* Detection of Encoded Regions (SPIDER)
SPIDER is a reference based *in silico* PCR based tool for detecting microbial sequences 
of interest for genome assemblies. It features two key functions. First, it will search 
for sequences of interest inside of your whole genome assembly. Second, it can extract
those sequences of interest into a FASTA file for quickly analyzing genomic epidemiology.

# Installation
1. Download or clone this GitHub repository
2. SPIDER uses a conda environment to handle dependencies. Install the conda environment 
from the provided environment.yml file using `conda env create -f environment.yml`
3. Activate the SPIDER conda environment using the command `conda activate spider`

# SPIDER Search
To search for sequences of interest, SPIDER requires one or more query sequences and a 
database to search. The query sequences may be specified as either a single FASTA file,
list of paths to multiple FASTA files or a folder containing multiple sequences (.fasta or .fna).
You can either search a pre-compiled database using a keyword, or provide a custom database
in FASTA format. The full list of parameters is available in a table below. If you want to 
just get going, see the example commands below.

## Examples
Searching a whole-genome assembly for virulence factors in the VFDB belonging to Staphylococcus aureus:

`python spider.py -f assembly.fasta -db vfdb -s "Staphylococcus aureus"`

Search a list of genome assemblies for a sequence in the database `custom_db.fasta` and save the output to the file `out.txt`:

`python spider.py -l genome_list.txt -db custom_db.fasta -o out.txt`

## Full SPIDER Search Parameters
| Parameter | Description | Required |
| - | - | - |
| Input Options |
| -f, --fasta | Path to a single genome sequence | Yes, only one of these options at a time |
| -l, --list | Path to a list of genome sequences. This file is expected to contain paths to genome sequences, each on a newline. |
| -d, --directory | Path to a directory. SPIDER will look for any files that end in .fasta or .fna inside of this directory |
| Database Options |
| -db, --database | Either a keyword for a pre-compiled database, or path to a custom database in FASTA format.| Yes |
| --list_dbs | Provides a list of pre-compiled databases that can be searched. This is a stand-alone command that can be run without specifying a query and database. | No |
| Output Options |
| -o, --output | Output file that will be generated.  For SPIDER search, this will be a tab-separated-values file. If no output is specified, SPIDER will print to stdout. | No |
| Additional Search options |
| -sl, --slide_limit         | Percent length of a reference sequence that primers are allowed to slide.Default is 5 (5%). | No |
| -lt, --length              | Percent length tolerance between an extracted amplicon and the reference sequence. Default is 20 (20%). This allows matches of 80-100% of the reference sequence. | No |
| -it, --identity            | Percent identity tolerance between an extracted amplicon and the reference sequence. Anything above this threshold will be called positive. Default is 0 (0%). | No |
| -p, --primer_size | Length of primers for SPIDER to use. Default is 20 (20nt). | No |

# SPIDER Extract
SPIDER can quickly extract the sequences of amplicons identified by the program. 
To run this command, it is requited that a SPIDER search is run first, and the output is
saved to a file. SPIDER will parse the output of the search, and extract all sequences
that were flagged as valid by the search.

## Examples

Extract the nucleotide sequence of search using the custom database `custom_db.fasta` in 
the genome of `assembly.fasta`.

```
python spider.py -f assembly.fasta -c custom_db.fasta -o search_custom_db.txt
python spider.py -e search_custom_db.txt -o assembly_custom_db.fasta
```

Extract the amino acid sequences of the coagulase gene from all assemblies in the directory 
`assemblies` using the reference sequence from VFDB.

```
python spider.py -d assemblies -db vfdb -s "Staphylococcus aureus" -o coagulase_search.txt
python spider.py -e coagulase_search.txt --translate -o coagulase.fasta
```

## Full SPIDER Extract Parameters
| Parameter | Description | Required |
| - | - | - |
| -e, --extract | Output of a SPIDER search for sequence(s) of interest in tab-separated-values format. | Yes |
| --translate | Translates the extracted nucleotide sequences to amino acid sequences. Note that this function assumes that the extracted sequence is in the desired reading frame. | No |
| -o, --output | Output file that will be generated. For SPIDER extract, this will be in FASTA format. Default: stdout | No |
