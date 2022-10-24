A local copy of ligand and binding site information created from mmCIF files of the PDB database.

### Step 0: Initialize database ###
This step is only needed the first time the database is created. It will not be necessary for subsequent database update.
```bash
script/rsyncPDB.sh
```
This script downloads the initial set of mmCIF files for full asymetric unit to pdb/data/structures/divided/mmCIF.

### Step 1: Generate table for each type of ligand ###
```bash
script/download_ligand.pl
```
This script downloads CCD ligand to pdb/data/monomers/components.cif.gz and extract their summary to data/ligand.tsv.gz.

## Step 2: Download SIFTS function annotation ###
```bash
./script/download_sifts.pl
```
This script downloads taxonomy, uniprot accession, EC, GO and pubmed ID.

### Step 3: Download missing PDB entries ###
```bash
./script/download_pdb.pl
```
This script downloads the set of missing mmCIF files for full asymetric unit to pdb/data/structures/divided/mmCIF.

### Step 4: convert mmCIF to PDB format ###
```bash
./script/curate_pdb.pl
```
This script converts mmCIF files from pdb/data/structures/divided/ed pdb/data/structures/divided/mmCIF to interim/*/*.tar.gz and interim/*/*.txt
