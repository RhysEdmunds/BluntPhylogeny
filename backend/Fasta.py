import os
import csv

from Bio import Entrez
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import MutableSeq

import Log
import Utils





"""!
Takes a set of ascension numbers for the same gene, and creates an unaligned fasta of them

/param filename
    the name of the output file to be created
/param CSVfile
    Already loaded into a csv.DictReader. In the format
        taxon name , gene 1 , gene 2 , etc
        .
        .
        .
    Where the genes are ascension numbers
/param gene
    the header name for the gene to create a fasta for
/param EntrezEmail
    an email address for the NCBI, so the US government can track
/param out_directories - [fasta_directory,description_directory],
            where to move the fasta and description files respectively

The output is a set of fastas as outputted from the Bio SeqIO with the headers replaced by the taxon names
& a file in which the original headers are situated
 - called filename_data.fasta

As well as a descriptions.csv file
"""
def fastaFromAscensions(filename,CSVfile,CSVfile_linenum,gene,EntrezEmail,directories):
    Entrez.email = EntrezEmail # Telling NCBI who I am

    # Setting up checkpoints
    chk_count = 0
    chk_total = CSVfile_linenum + 3 # + 2 for the checkpoints before going into the loop, + 1 for the one afterwards
    chk_count = Log.checkpoint(gene,chk_count,chk_total)

    # The genes
    listify = []
    # The descriptions
    dscrpts_filename = gene + "_descriptions.csv"
    dscrpts_file = open(dscrpts_filename, 'w')
    dscrpts_writer = csv.writer(dscrpts_file)
    dscrpts = []
    enum_id = 0

    chk_count = Log.checkpoint(gene,chk_count,chk_total)

    for row in CSVfile:

        chk_count = Log.checkpoint(gene,chk_count,chk_total)

        if (row[gene]!='' and row[gene]!=gene):
            # Fetching the fasta from the nucleotide site, then putting it as a SeqRecord type
            handle = Entrez.efetch(db="nucleotide", id=row[gene], rettype="fasta", retmode="text")
            record_in = SeqIO.read(handle,"fasta") # Parses it, then chooses the right one
            handle.close()

            taxon_name = row["Taxon"].replace(" ","_")

            # Recording the descriptions
            dscrpts = [str(enum_id),taxon_name,record_in.id,record_in.description]
            dscrpts_writer.writerow(dscrpts)

            # Creating a clean record with an enumerated id & user-defined description
            record_out = SeqIO.SeqRecord(record_in.seq,id = str(enum_id), description = taxon_name)
            listify.append(record_out)
            
        enum_id += 1
    

    # Writing the .fasta file
    SeqIO.write(listify,filename,"fasta")

    Utils.move_file(filename,directories[0])

    # Cleaning up
    dscrpts_file.close()
    Utils.move_file(dscrpts_filename,directories[1])

    chk_count = Log.checkpoint(gene,chk_count,chk_total,remove=False)





"""
A loop going through the above function for each gene

/param ascension_filename - input ascension
/param email - Email for entrez
/param directories - [fasta_directory,description_directory,enum_directory],
            where to move the fasta, description and enum files respectively

Output - A set of gene files & a .csv for the descriptions
As well as an enum
"""

def step_1 (email, ascension_filename, directories):
    # Opening the file into a usable format
    file = open(ascension_filename, mode="r")
    CSVfile = csv.DictReader(file) # DictReader means that the first row is used as monikers for the columns

    # Creating the enum file
    enum_filename = Utils.create_enum(ascension_filename)

    # Formatting the csv file's 
    gene_list = CSVfile.fieldnames.copy()
    if gene_list[0] != "Taxon":
        gene_list[0] = "Taxon"

    # Getting the gene names
    fieldnames = gene_list.copy()

    # Getting only the genes
    gene_list.remove("Taxon")
    Log.log("GENE LIST: " + str(gene_list))

    # Getting the length of the file
    enum_file = open(enum_filename, 'r')
    file_length = len(enum_file.readlines())
    enum_file.close()
    Utils.move_file(enum_filename,directories[2])

    # Writing the four separate .fasta files in the form
    """
    ><ascension> <taxon>
    <sequence>
    .
    .
    """
    for gene in gene_list:
        # Opening a file & setting the CSV DictReader if the file isn't open already
        if file.closed:
            file = open(ascension_filename, mode="r")
            CSVfile = csv.DictReader(file)
        
        # Setting the CSVfile fieldnames
        CSVfile.fieldnames = fieldnames

        # Processing the gene
        Log.log(gene + " [PROCESSING]")
        filename = str(gene) + ".fasta"

        # TODO TEST WITH .readlines(), make sure it doesn't iterate through
        fastaFromAscensions(filename,CSVfile,file_length,gene,email)

        # Closing the file
        file.close()





"""
Formats a set of local fasta files to be in the standard formats

/param fasta - a filename to a fasta with multiple records in the form:
        >Genus_species

/return - whether successful or not

output - an enum file
       - a standard fasta file
"""
def addEnumToFasta(fasta):
    #TODO
    return False




"""
Creates a neighbour joining .tre file
/param fasta - a filename to a standard fasta file

/return - filename of the new .tre

output - a .tre file, a neighbour joined rough tree to inspect
"""
def rough_tree(fasta):
    # TODO
    return fasta


"""
A function that concatenates two genes
Genes should have an enumerated id, 0-number of taxa at the beginning
& a taxon name
e.g.
    >12 Siratus_pliciferoides
        TCGAGA...

CURRENTLY RELIES ON 1 HAVING ALL GENES TODO

/param ins - a list of filenames for the relevant fastas
/param enum_filename - a filename for the enumerated file for the genes
/param out - name of the fasta file to concatenate to, WITHOUT fasta ending

writes a fasta file with the enumerated ids, the taxon names & the concatenated genes named
writes a gene length file for the genes
"""
def concatenateFastas(ins,enum_filename,out):
    Log.log("Concatenating to " + out + ".fasta:")

    # Setting up checkpoints
    chk_count = 0
    chk_total = 3
    
    chk_count = Log.checkpoint(out,chk_count,chk_total)
    
    # Getting the enum file
    enum_file = open(enum_filename, 'r')
    enum_reader = csv.DictReader(enum_file)

    # List to write out the sequences
    out_list = []

    # File that writes the gene length file
    gene_len_filename = out[:-6] + "_gene_lengths.csv" # filename without the fasta
    gene_len_file = open(gene_len_filename,'w')
    gene_len_fieldnames = ["Gene","Length"]
    gene_len_writer = csv.DictWriter(gene_len_file,fieldnames=gene_len_fieldnames)
    # For iterating through the genes
    gene_num = 0

    chk_count = Log.checkpoint(out,chk_count,chk_total)
    
    for enum_row in enum_reader:
        # Creating a sequence & appending the right sequences upon them - the first of a given record only

        # Variables for the enum id, in integer & string forms
        enum_id = int(enum_row["Enum_id"])
        enum_id_str = str(enum_row["Enum_id"])
        # log(str_enum_id)
        
        # The sequence to be appended
        temp_sequence = MutableSeq("")

        for fasta_name in ins:
            if enum_id == 0:
                continue
            
            fasta = SeqIO.index(fasta_name,'fasta')
            # for k in fasta.keys():
            #     log(k + ": " + fasta[k].description)

            # Getting the genes and their lengths, creating the gene length file
            if enum_id == 1:
                gene_len_row = {gene_len_fieldnames[0]:fasta_name[:-6],gene_len_fieldnames[1]:len(fasta[enum_id_str].seq)}
                gene_num += 1
                gene_len_writer.writerow(gene_len_row)
            
            if enum_id_str in fasta.keys():
                # Appending the sequence
                temp_sequence = temp_sequence + fasta[enum_id_str].seq
            # Adding a None sequence to maintain the correct length if the append wasn't the correct length
            else:
                zero_sequence = "-" * len(fasta['1'].seq)
                temp_sequence = temp_sequence + zero_sequence # ASSUMING fasta[0] HAS THE GENE
            
            fasta.close()
            
            # Adding to the list for the file to be put out
            if (fasta_name == ins[-1]):
                out_list.append(SeqRecord(temp_sequence,enum_row["Taxon"]))

        #out_list.append(SeqRecord(temp_sequence,enum_row["Taxon"]))

    chk_count = Log.checkpoint(out,chk_count,chk_total)
    
    # Writing the file
    SeqIO.write(out_list, (out + '.aln'), 'fasta')

    # Closing all the files
    gene_len_file.close()
    enum_file.close()

    chk_count = Log.checkpoint(out,chk_count,chk_total)
    


"""
Runs the above code using all the fastas in the current folder as the input
"""
"""
Creates a filename for the concatenate, in the form
    concatenated<GENE1><GENE2>...<GENEX>
WITHOUT ".fasta"
"""
def generateConcatenateName(fasta_list):
    all_fastas = ""
    for f in fasta_list:
        all_fastas += f[:-6]
    filename = "concatenated" + all_fastas
    return filename





"""
Function that changes fasta to nexus

/param - input_handle: an open file for the fasta that's being read WITHOUT '.fasta'
/param - filename: a filename for the given file to be created
- Writes a nexus file
/return - nexus file of the input file
"""
def fasta_to_nexus (fasta_filename, nexus_filename,ambiguous=True):
    with open(fasta_filename + '.fasta', "rU") as input_handle:
        with open(nexus_filename+".nexus", "w") as output_handle:
            records = SeqIO.parse(input_handle, "fasta")
            records_out = []
            for record in records:
                if (record.description[-1]=='>'): # Removing ' <unknown description>' occurring on concatenated
                    record.description = record.description[:-22]
                records_out.append(SeqRecord(seq=record.seq,id=record.description,annotations={"molecule_type": "DNA"}))
            
            SeqIO.write(records_out, output_handle, "nexus")






