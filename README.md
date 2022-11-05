A local copy of ligand and binding site information created from mmCIF files of the PDB database.

## Installation for database update ##
```bash
cd script/
make
```
The compilation requires GCC with C++ 11 support.
The binary executable of [cd-hit](https://github.com/weizhongli/cdhit) is available at ``script/cd-hit`` for 64 bit Linux.
The binary executable of makeblastdb, blastn and blastp from the [NCBI BLAST+](ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/) are available at ``script/`` for 64 bit Linux.
Reinstall cd-hit, makeblastdb, blastn and blastp if using other operating system.

## Installation for web browsing ##

1. This repository contains a copy of [JSmol](https://wiki.jmol.org/index.php/JSmol). This is not needed for database update. It is solely for visualization through the web browser.

2. Optionally, to show directed acylic graph for Gene Ontology terms on the website, the ``dot`` program from [Graphviz](https://graphviz.org/) can be used. If your system does not have Graphviz, you can install it to ``graphviz/bin/dot`` from source code:
```bash
wget https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/6.0.2/graphviz-6.0.2.tar.gz
tar -xvf graphviz-6.0.2.tar.gz
mkdir ../graphviz
export LDFLAGS=-static
./configure --prefix=`readlink -e ../graphviz`
make
make install
rm graphviz-6.0.2.tar.gz
```

3. Follow ``output/readme.sh`` to set up for web browsing.

## Database update ##

The first time to set up the database takes at least two days. Subsequent weekly updates only take a couple hours. The database would requires ~100GB of disk space, including ~60GB to store original mmCIF files downloaded from PDB (``pdb/data/structures/divided/mmCIF/``; see Step 11 to reduce this requirement), ~20GB to store intermediate PDB files (``interim/``), and another ~20GB to store final files (``weekly/``, ``data/`` and ``download/``).

### Step 1: Download PDB entries ###
Run the following shell script the first time the database is created.
```bash
script/rsyncPDB.sh
```
This script downloads the initial set of mmCIF files for full asymetric unit to ``pdb/data/structures/divided/mmCIF``. It will also download the resolution of pdb to ``pdb/derived_data/index/resolu.idx``.

Alternatively, run the following script to download only the missing mmcif files and resolu.idx.
```bash
script/download_pdb.pl
```
Both ``script/rsyncPDB.sh`` and ``script/download_pdb.pl`` have the same purpose of downloading mmcif files and resolu.idx. For the first time the database is setup, ``script/rsyncPDB.sh`` must be used instead of ``script/download_pdb.pl`` because the later is much slower when a large number of files need be downloaded. For subsequent weekly update, either one of the script can be used. If you do not want to clean up the pdb/ folder, the first script ``script/rsyncPDB.sh`` is preferred. If you do want to clean up the pdb/ folder after every update, which can save ~60GB of disk space, you must use the second script ``script/download_pdb.pl`` to avoid re-downloading the whole pdb database every week. Hard disk space permitted, it is recommended to use ``script/rsyncPDB.sh``, which offers faster download speed and less file corruption.

### Step 2: Download SIFTS function annotation ###
This step can be performed in parallel to step 1.
```bash
./script/download_sifts.pl
```
This script downloads taxonomy, uniprot accession, EC, GO and pubmed ID to ``sifts/flatfiles/tsv`` and extract the data to ``data/*.tsv.gz``.
This script downloads gene ontology to ``obo/go/go-basic.obo``.
This script downloads swissprot to ``uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz``.

Optionally, run the following script to download csa. The manually curated dataset of csa is updated infrequently. Therefore, it is not necessary to run it every week.
```bash
./script/download_csa.pl
```
This script downloads catalytic site to ``m-csa/api/residues.json`` and extract the summary to ``data/csa.tsv.gz``.

### Step 3: Download binding affinity ###
This step must be performed after step 2 (regardless of step 1) because it requires the pdb to uniprot mapping file generated in the previous step.
```bash
./script/download_bind.pl
```
This script downloads BindingDB to ``bind/BindingDB*`` and extract the summary to ``data/BindingDB.tsv.gz``.
This script may have the warning: "gzip: bind/BindingDB_All_tsv.zip: invalid compressed data--length error", which is caused by decompressing zip with zcat. This warning can be ignored.

Optionally, run the following script to download MOAD. Since MOAD only updates every few years, it is not necessary to run it weekly.
```bash
./script/download_moad.pl
```
This script downloads MOAD to ``bind/every.csv`` and extract the summary to ``data/moad.tsv``.

Again optionally, follow instructions at [bind/README.md](bind/README.md) for how to semi-manually create PDBbind-CN summary at ``data/PDBbind.tsv``. This only need to be peformed annually.

### Step 4: download auxilary data ###
This step can be performed independent of step 1 to 8, but must be done before step 9.
```bash
./script/download_ligand.pl
```
This script downloads CCD ligand to ``pdb/data/monomers/components.cif.gz`` and extract their summary to ``data/ligand.tsv.gz``.
This script downloads enzyme to ``enzyme/enzyme.dat`` and extract their summary to ``data/enzyme.tsv.gz``.

### Step 5: convert mmCIF to PDB format ###
This step must be performed after step 1 (regardless of step 2 to 4).
```bash
./script/curate_pdb.pl
```
This script converts mmCIF files from ``pdb/data/structures/divided/mmCIF`` to ``interim/*/*.tar.gz`` and ``interim/*/*.txt``

### Step 6: download pubmed abstract ###
This step must be performed after step 2 and 5 (regardless of step 3 and 4).
```bash
./script/download_pubmed.pl
```
This script checks ``interim/*/*.txt`` for artifact ligand and download pubmed abstract to ``pubmed/*.txt``

### Step 6: remove artifact and unbound ligand ###
This step must be performed after step 6.
```bash
./script/curate_ligand.pl
```
This script check potential artifact ligand listed by ``interim/*/*.txt`` against pubmed abstract at ``pubmed/*.txt``.
It repackages receptor and biologically relevent ligand pdb files into ``interim/*/*.tar.bz2``. 
Binding sites are written to ``interim/*/*.bsr``.

### Step 7: prepare redundant dataset ###
This step must be performed after step 7.
```bash
./script/make_weekly.pl
```
This script reads ``interim/*/*.tar.bz2`` and ``interim/*/*.bsr`` and writes ``weekly/receptor_*.tar.bz2``, ``weekly/receptor1_*.tar.bz2``, ``weekly/ligand_*.tar.bz2`` and ``weekly/BioLiP_*.bsr.gz``.
FASTA sequence of protein, peptide, rna, dna are saved to ``data/*.fasta.gz``

### Step 9: prepare nonredundant dataset ###
This step must be performed after step 3, 4 and 8.
```bash
./script/make_nr.pl
```
This script converts ``weekly/BioLiP_*.bsr.gz`` to ``weekly/BioLiP_*.txt`` and ``weekly/BioLiP_*_nr.txt``.
It also creates ``weekly/receptor_*_nr.tar.bz2``, ``weekly/receptor1_*_nr.tar.bz2`` and ``weekly/ligand_*_nr.tar.bz2`` from intermediate files of the previous step.

## Step 10: curate GO anntation ##
This step must be performed after step 9.
```bash
./script/curate_GO.pl
```
This script reads GO from ``obo/go/go-basic.obo`` and ``data/pdb_all.tsv.gz``.
and extract the summary to ``data/go2name.tsv.gz``, ``data/is_a.tsv.gz`` and ``data/pdb_go.tsv.gz``.
This script reads swissprot name from ``uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz`` and extract the summary to ``data/uniprot_sprot.tsv.gz``.

### Step 11: clean up intermediate files ###
This step must be run after everything is done.
```bash
./script/clean_up.pl
```
