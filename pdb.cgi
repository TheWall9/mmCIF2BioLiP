#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import os
import gzip
import subprocess
import textwrap
import tarfile
import gzip

rootdir=os.path.dirname(os.path.abspath(__file__))

def display_ligand(pdbid,asym_id,lig3,ligIdx):
    reso  =''
    pubmed=''
    cmd="zcat %s/data/pdb_all.tsv.gz |cut -f1,3,9|uniq|grep -P '^%s\\t'"%(
        rootdir,pdbid)
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    stdout,stderr=p.communicate()
    items=stdout.decode().split('\t')
    if len(items)>=3:
        reso,pubmed=items[1:3]
    
    prefix='_'.join((pdbid,lig3,asym_id,ligIdx))
    filename="%s/output/%s.pdb.gz"%(rootdir,prefix)
    if not os.path.isfile(filename):
        divided=pdbid[-3:-1]
        tar = tarfile.open("%s/weekly/ligand_%s.tar.bz2"%(rootdir,divided))
        fin=tar.extractfile("ligand/%s.pdb"%prefix)
        fout=gzip.open(filename,'wb')
        fout.write(fin.read())
        fout.close()
        fin.close()
        tar.close()
    script=''
    if lig3 in ["peptide","rna","dna"]:
        script="cartoons; color group; spacefill off; wireframe off;"

    print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">3D structure</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr><td align=center width=10%>PDB</td><td><a href=qsearch.cgi?pdbid=$pdbid>$pdbid</a></td></tr>
    <tr BGCOLOR="#DEDEDE"><td align=center>Chain</td><td><a href=qsearch.cgi?pdbid=$pdbid&chain=$asym_id>$asym_id</a></td></tr>
    <tr><td align=center>Resolution</td><td>$reso</a></td></tr>
    <tr BGCOLOR="#DEDEDE" align=center><td align=center>3D<br>structure</td><td>
    <table><tr><td>

<script type="text/javascript"> 
$(document).ready(function()
{
    Info = {
        width: 400,
        height: 400,
        j2sPath: "jsmol/j2s",
        script: "load output/$prefix.pdb.gz; $script"
    }
    $("#mydiv").html(Jmol.getAppletHtml("jmolApplet0",Info))
});
</script>
<span id=mydiv></span>
    </td><td align=left>
[<a href="javascript:Jmol.script(jmolApplet0, 'spin on')">Spin on</a>]<br>
[<a href="javascript:Jmol.script(jmolApplet0, 'spin off')">Spin off</a>]<br>
[<a href="javascript:Jmol.script(jmolApplet0, 'Reset')">Reset orientation</a>]<p></p>
[<a href="javascript:Jmol.script(jmolApplet0, 'set antialiasDisplay true')">High quality</a>]<br>
[<a href="javascript:Jmol.script(jmolApplet0, 'set antialiasDisplay false')">Low quality</a>]<p></p>
[<a href="javascript:Jmol.script(jmolApplet0, 'color background white')">White quality</a>]<br>
[<a href="javascript:Jmol.script(jmolApplet0, 'color background black')">Black quality</a>]<br>
    </td></tr></table>


    </td></tr>
    </table>
</div>
</td></tr>
'''.replace("$pdbid",pdbid
  ).replace("$asym_id",asym_id
  ).replace("$reso",reso
  ).replace("$prefix",prefix
  ).replace("$script",script
  ))


    cmd="zcat %s/data/lig_all.tsv.gz|grep -P '^%s\\t\w+\\tBS\d+\\t%s\\t%s\\t%s\\t'"%(
        rootdir,pdbid,lig3,asym_id,ligIdx)
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    stdout,stderr=p.communicate()
    lines=stdout.decode().splitlines()
    if len(lines):
        print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">Interaction with protein receptor</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr BGCOLOR="#DEDEDE" align=center>
        <th width=10%><strong>Receptor chain</strong></th>
        <th width=30%><strong>Binding residues on receptor<br>(original residue number in PDB)</strong></th>
        <th width=30%><strong>Binding residues on receptor<br>(residue number reindexed from 1)</strong></th>
        <th width=30%><strong>Binding affinity</strong></th>
    </tr>
''')
        for l,line in enumerate(lines):
            items    =line.split('\t')
            recCha   =items[1]
            bs       =items[2]
            resOrig  =items[6]
            resRenu  =items[7]
            manual   =items[8]
            moad     =items[9]
            pdbbind  =items[10]
            bindingdb=items[11]

            baff_list=[]
            if manual:
                baff_list.append("Manual survey: "+manual)
            if moad:
                baff_list.append("<a href=http://bindingmoad.org/pdbrecords/index/%s>MOAD</a>: %s"%(pdbid,moad))
            if pdbbind:
                baff_list.append("<a href=http://pdbbind.org.cn/quickpdb.php?quickpdb=%s>PDBbind-CN</a>: %s"%(pdbid,pdbbind))
            if bindingdb:
                baff_list.append("BindingDB: "+bindingdb)

            bgcolor=''
            if l%2==1:
                bgcolor=' BGCOLOR="#DEDEDE" '
            print('''
    <tr %s align=center>
        <td><span title="Click to view binding site"><a href="getaid.cgi?pdb=%s&chain=%s&bs=%s">%s:%s</a></span></td>
        <td><span title="Click to view binding site"><a href="getaid.cgi?pdb=%s&chain=%s&bs=%s">%s</a></span></td>
        <td><span title="Click to view binding site"><a href="getaid.cgi?pdb=%s&chain=%s&bs=%s">%s</a></span></td>
        <td>%s</td>
    </tr>
            '''%(bgcolor,
            pdbid,recCha,bs,pdbid,recCha,
            pdbid,recCha,bs,resOrig,
            pdbid,recCha,bs,resRenu,
            '<br>'.join(baff_list)))

        print('''   </table>
</div>
</td></tr>
''')

    return pubmed

    

def display_polymer_ligand(pdbid,asym_id,lig3):
    code=lig3.upper()
    if lig3=="peptide":
        code="Peptide"
    prefix="%s_%s_%s"%(pdbid,lig3,asym_id)
    cmd="zcat %s/data/%s.fasta.gz|grep -PA1 '^>%s\\t'|tail -1"%(
        rootdir,lig3,prefix)
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    stdout,stderr=p.communicate()
    sequence=stdout.decode().strip()
    seq_txt='<br>'.join(textwrap.wrap(sequence,50))

    cmd="zcat %s/data/%s_nr.fasta.clust.gz|sed 's/\\t/,/g'|grep -P '\\b%s\\b'"%(
        rootdir,lig3,prefix)
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    stdout,stderr=p.communicate()
    homolog_link=''
    for homolog in stdout.decode().strip().split(','):
        if homolog==prefix or not homolog.strip():
            continue
        homo_pdbid,homo_asym_id=homolog.split('_'+lig3+'_')
        homolog_link+=", <a href=pdb.cgi?pdb=%s&chain=%s&lig3=%s&idx=0>%s:%s</a>"%(
            homo_pdbid,homo_asym_id,lig3,homo_pdbid,homo_asym_id)
    if homolog_link:
        homolog_link='<tr BGCOLOR="#DEDEDE"><td>(Identical to '+ \
        homolog_link[1:]+")</td></tr>"

    print('''
<tr><td><h1 align=center>Structure of PDB $pdbid Chain $asym_id</h1></td></tr>
<tr><td>
<div id="headerDiv">
    <div id="titleText">Sequence</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr><td>&gt;$prefix (length=$L) [<a href=ssearch.cgi?seq_type=$lig3&sequence=$sequence>Search sequence</a>]</td></tr>
    <tr><td><span title="Only residues with experimentally determined coordinates are included. Residues unobserved in the structure are excluded.">$seq_txt</span></td></tr>
    $homolog_link
    </table>
</div>
</td></tr>
'''.replace("$pdbid",pdbid
  ).replace("$asym_id",asym_id
  ).replace("$prefix",prefix
  ).replace("$L",str(len(sequence))
  ).replace("$lig3",lig3
  ).replace("$sequence",sequence
  ).replace("$seq_txt",seq_txt
  ).replace("$homolog_link",homolog_link
  ))
    return display_ligand(pdbid,asym_id,lig3,'0')

def display_regular_ligand(pdbid,asym_id,lig3,ligIdx):
    if not ligIdx:
        ligIdx='1'
    lig3=lig3.upper()

    formula=''
    InChI=''
    InChIKey=''
    SMILES=''
    name=''
    cmd="zcat %s/data/ligand.tsv.gz|grep -P '^%s\\t'"%(rootdir,lig3)
    p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    stdout,stderr=p.communicate()
    items=stdout.decode().split('\t')
    if len(items)>=6:
        formula,InChI,InChIKey,SMILES,name=items[1:6]
    svg="https://cdn.rcsb.org/images/ccd/labeled/%s/%s.svg"%(lig3[0],lig3)
    print('''
<tr><td><h1 align=center>Structure of PDB $pdbid Chain $asym_id ligand $lig3</h1></td></tr>
<tr><td>
<div id="headerDiv">
    <div id="titleText">Chemical information</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr align=center><td width=10%>2D<br>diagram</td><td><a href=$svg target=_blank><img src=$svg width=400></a></td></tr>
    <tr BGCOLOR="#DEDEDE"><td align=center><a href=https://wwpdb.org/data/ccd target=_blank>ID</a></td><td><span title="The ligand ID follows the
Chemical Component Dictionary (CCD)
used by the PDB database."><a href=https://rcsb.org/ligand/$lig3>$lig3</a></span></td></tr>
    <tr><td align=center><a href=https://inchi-trust.org target=_blank>InChI</a></td><td>$InChI</td></tr>
    <tr BGCOLOR="#DEDEDE"><td align=center><a href=https://inchi-trust.org target=_blank>InChIKey</a></td><td>$InChIKey</td></tr>
    <tr><td align=center>SMILES</td><td>$SMILES</td></tr>
    <tr BGCOLOR="#DEDEDE"><td align=center>Formula</td><td>$formula</td></tr>
    <tr><td align=center>Name</td><td>$name</td></tr>
    </table>
</div>
</td></tr>
'''.replace("$pdbid",pdbid
  ).replace("$asym_id",asym_id
  ).replace("$lig3",lig3
  ).replace("$svg",svg
  ).replace("$InChIKey",InChIKey
  ).replace("$InChI",InChI
  ).replace("$SMILES",SMILES.replace(';',';<br>')
  ).replace("$formula",formula
  ).replace("$name",name.replace(';',';<br>')
  ))
    return display_ligand(pdbid,asym_id,lig3,ligIdx)


if __name__=="__main__":
    form   =cgi.FieldStorage()
    pdbid  =form.getfirst("pdb",'').lower()
    asym_id=form.getfirst("chain",'')
    ligIdx =form.getfirst("idx",'')
    lig3   =form.getfirst("lig3",'')

    print("Content-type: text/html\n")
    print('''<html>
<head>
<link rel="stylesheet" type="text/css" href="page.css" />
<title>BioLiP</title>
</head>
<body bgcolor="#F0FFF0">
<img src=images/BioLiP1.png ></br>

<script type="text/javascript" src="jsmol/JSmol.min.js"></script>
<table style="table-layout:fixed;" width="100%" cellpadding="2" cellspacing="0">
<table>
''')
    pubmed=''
    uniprot=''
    if lig3:
        if lig3 in ["rna","dna","peptide"]:
            pubmed=display_polymer_ligand(pdbid,asym_id,lig3)
        else:
            pubmed=display_regular_ligand(pdbid,asym_id,lig3,ligIdx)
    else:
        pubmed,uniprot=display_protein_receptor(pdbid,asym_id)
    
    uniprot_line=''
    if uniprot:
        uniprot_line='''    <tr><td align=center>UniProt</td>
        <td><a href=https://uniprot.org/uniprot/%s target=_blank>%s</tr>'''%(
        uniprot,uniprot)
        
    print('''
<tr><td>
<div id="headerDiv">
    <div id="titleText">External link</div>
</div>
<div style="clear:both;"></div>
<div id="contentDiv">
    <div id="RContent" style="display: block;">
    <table width=100% border="0" style="font-family:Monospace;font-size:14px;background:#F2F2F2;" >
    <tr><td align=center width=10%>PDB</td>
        <td width=90%><a href=https://rcsb.org/structure/$pdbid target=_blank>RCSB: $pdbid</a>,
            <a href=https://ebi.ac.uk/pdbe/entry/pdb/$pdbid target=_blank>PDBe: $pdbid</a>,
            <a href=https://pdbj.org/mine/summary/$pdbid target=_blank>PDBj: $pdbid</a></td> </tr>
    <tr BGCOLOR="#DEDEDE"> <td align=center>PDBsum</td><td><a href=http://ebi.ac.uk/pdbsum/$pdbid target=_blank>$pdbid</a></td></tr>
    <tr> <td align=center>PubMed</td><td><a href=https://pubmed.ncbi.nlm.nih.gov/$pubmed target=_blank>$pubmed</a></td></tr>
    $uniprot_line
    </tr>
'''.replace("$pdbid",pdbid
  ).replace("$pubmed",pubmed
  ).replace("$uniprot_line",uniprot_line
  ))
    
    print('''</table>
<p></p>
[<a href=.>Back to BioLiP</a>]
</body> </html>''')
