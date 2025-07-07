# SPIDER
Sliding Primer In-Silico Detection of Encoded Regions - An in-silico PCR method for detecting microbial virulence factors.

# Installation
1. Download the repository
2. Install the conda environment using the following command:
`conda env create -f environment.yml`
3. Activate the SPIDER conda environment using the command:
`conda activate spider`
4. Download VFDB using the command:
`python spider.py --download` 

# Basic Usage
SPIDER can be used on a single assembly or list of assemblies to test for one or more virulence factors.

## Testing a genome assembly for virulence factors
To test for species-wide virulence factors on a single assembly, the following command can be used.
`python spider.py -f [assembly].fasta -s "[Genus species]"`

## Testing a list of assemblies for a virulence factor
To test multiple assemblies, create a text file with a list. Each assembly should be on a new line.
```
assembly_1.fasta
assembly_2.fasta
...
```

Run SPIDER on the list using the following command.
`python spider.py -l list.txt -v [virulence_factor]`