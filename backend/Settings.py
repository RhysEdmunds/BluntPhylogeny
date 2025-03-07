"""
Setting defaults here
"""

import csv

SETTINGS = "C:/Users/rhyse/OneDrive/Documents/Personal/Biology/Phylogenetics/"

Settings = {'ROOT_PATH':"."}

"""
Sets the variables to default values.
They can be seen below, which also gives a list of all the standard variables in settings (defined in other documentation)
"""
def set_defaults():
    # Setting the root path if it isn't there already
    if 'ROOT_PATH' not in Settings:
        Settings['ROOT_PATH'] = "."

    # ----- Bools -----
    # A bool whether it is the Cambridge practical or not
    Settings['practical'] = False
    Settings['PRACTICAL_OUTPUT'] = "" # NOT NEEDED UNLESS PRACTICAL 

    Settings['inspect_trees'] = True

    Settings['sh_mrbayes'] = False
    Settings['MRBAYESSH'] = "" # Directs the program to the MrBayes.sh
    # < MrBayes.sh is a bash file that runs the MrBayes program, this is simplest if there is only 1 gene

    #Settings['environment_checks'] = True # FOR FUTURE: Runs without the environment checks, usually isn't used

    # ----- Ints -----
    # Int - at which step to start
    # On settings page, determines input section. Drop-down options [input - use ascension numbers,
                                                                        #1 - use local fasta data,
                                                                        #2 - Doing the pasta and moving the files,
                                                                        #3 - Trimming & inspecting the alignment,
                                                                        #4 - Preparing fastas for MrBayes & conducting MrBayes]
    Settings['start'] = 0
    Settings['end'] = 5
    
    # Level of installation - #0 - no further installation allows, terminates
                              #1 - ask everytime
                              #2 - can install willy-nilly
    Settings['can_install'] = 2
    
    # ----- Paths -----
    ### INPUTS & OUTPUTS
    Settings['INPUT'] = Settings['ROOT_PATH'] + "/0input"
    Settings['OUTPUT'] = Settings['ROOT_PATH'] + "/6output"

    # Outputs for intermediary
    # TODO in set_settings: if left blank, generates & then destroys temp files so there's only the input & output
    Settings['STEP1'] = Settings['ROOT_PATH'] + "/1unaligned"
    Settings['STEP2'] = Settings['ROOT_PATH'] + "/2aligned"
    Settings['STEP3'] = Settings['ROOT_PATH'] + "/3edited"
    Settings['STEP4'] = Settings['ROOT_PATH'] + "/4spaceless"
    Settings['STEP5'] = Settings['ROOT_PATH'] + "/5mrbayes"

    ### PATHS FOR THE PROGRAMS <- Need to make compilable for other OSs...
    Settings['PASTA'] = Settings['ROOT_PATH'] + "/libs/pasta" # TODO Just to the pasta folder, when I edit pasta this should just be imported directly into main
    Settings['BIOEDIT'] = Settings['ROOT_PATH'] + "/libs/BioEdit"
    Settings['GBLOCKS'] = Settings['ROOT_PATH'] + "/libs/Seaview5" # From SeaView
    Settings['FIGVIEW'] = Settings['ROOT_PATH'] + "/libs/FigTree v1.4.4"

    # ----- Lists -----
    Settings['encoding_genes'] = []

folders = ['INPUT','OUTPUT','STEP1','STEP2','STEP3','STEP4','STEP5']

"""
A function to check whether the gene is encoding or not
 - this changes the PASTA alignment and means that amino acids may be used to check the gene as well as the nucleotides
 - if so, a later function will deal with this TODO
"""
def is_encoding(gene):
    return (True if (('encoding_genes' in Settings) and Settings['encoding_genes'].contains(gene)) else False)




# ----- MrBayes -----
# TODO
"""
ONLY RELEVANT IF A MrBayes.sh ISN'T DEFINED

Works from a Settings_MrBayes.csv
            As well as a Genes_MrBayes.csv file for a concatenated fasta

Settings_MrBayes will have a given number of variables as defined in external documentation [TODO, and link]
"""
class MrBayesSettings():
    Settings['MRBAYES'] = Settings['ROOT_PATH'] + "/libs/mrbayes"
    manual = False

    # Returns the path to the MrBayes program
    def get_path(self):
        return self.MRBAYES
    


    # ----- HELPER FUNCTIONS -----
    """
    Gets the rates for a concatenated gene file

    input - Genes_MrBayes.csv
    
    /return rates - a dictionary in the format
                        [<gene number>:<NST number>,...]
    """
    def get_rates():
        rates = []
        # TODO
        return rates
    

    """
    Generating the transcript for the bottom of the .nexus file for a non-concatenated gene

    This puts all of the MrBayes settings together

    /param concatenated - whether the gene is concatenated or not, for usability only

    /return - a list of all the lines to add to the bottom
    """
    def generate_transcript(self,concatenated=False):
        # Generates the bit at the bottom given mr bayes, writes it to a file line by line
        lines = []
        
        # --- For a single gene - should be fairly straight forward, just gets the MrBayes settings
        if concatenated: return 0

        # These should eventually be set by the settings TODO
        lines = ["BEGIN MRBAYES;","set autoclose=yes;","LSET NST=2 RATES=INVGAMMA;",
            "MCMC NGEN=10000000 PRINTFREQ=2000 SAMPLEFREQ=2000 NCHAINS=4 SAVEBRLENS=YES APPEND=NO CHECKPOINT=YES;",
            "sumt  contype=halfcompat relburnin=yes burninfrac=0.1;","END;"]
        
        return lines
    
    """
    Generating the transcript for the bottom of the .nexus file for a concatenated gene

    This puts all of the MrBayes settings together

    /param concatenated - whether the gene is concatenated or not, for usability only
    /param gene_filename - if it is, the filename of the gene file to determine the lengths of the gene

    /return - a list of all the lines to add to the bottom
    """
    def generate_transcript(self,concatenated=True,gene_filename=""):
        # Generates the bit at the bottom given mr bayes, writes it to a file line by line
        lines = []
        
        # --- For a single gene - should be fairly straight forward, just gets the MrBayes settings
        if not concatenated: return 0
        
        # --- For a concatenated gene - requires some specific lines for each gene
        # Adding the initial two lines
        lines.append("BEGIN MRBAYES;","set autoclose=yes nowarn=yes;")

        # Getting the gene file
        gene_file = open(gene_filename, 'r')
        gene_reader = csv.reader(gene_file)
        gene_reader_list = list(gene_reader)

        # Adding the lines refering to the length of the genes within the concatenation
        position = 1
        for gene_row in gene_reader_list:
            # Adding the section as it's needed
            lines.append("charset " + gene_row[0] + " = " + str(position) + "-" + str( position + gene_row[1] ) + ";")
            position = position + gene_row[1] + 1

        
        # Appending the line specifying the genes
        line = ""
        line.append("partition by_gene = " + str(len(gene_reader_list)) + ": ")
        line.append([(gene[0] + ", ") for gene in gene_reader_list])

        lines.append(line, "set partition = by_gene;")

        # and the rates
        rates_dict = self.get_rates()
        for gene_num in rates_dict:
            lines.append("LSET applyto=" + str(gene_num), + " NST=" + str(rates_dict[gene_num]) + " RATES=INVGAMMA;")

        # prset ratepr=variable; # Not including this line - can lead to divergence

        # then the rest
        lines.append( "unlink revmat=(all)  statefreq=(all)  shape=(all) pinvar=(all);",
            "MCMC NGEN=20000000 PRINTFREQ=1000 SAMPLEFREQ=3000 NCHAINS=4 SAVEBRLENS=YES APPEND=NO CHECKPOINT=YES;",
            "sumt  contype=allcompat relburnin=yes burninfrac=0.1;", "END;" )
        
        return lines



    """
    Appends the transcript generated above to a nexus file

    /param nexus_filename - the filename of the nexus

    /return - success
    """
    def append_transcript(nexus_filename):
        # TODO
        return False



# ----- The main shebang -----
# Interacting with the .csv to get the settings

"""
Reads from the settings file, updates Settings dict
"""
def get_settings():
    set_defaults()
    # Gets the settings from the settings.csv file
    file = open(SETTINGS + "/bluntphy_settings.csv",'r')
    file_reader = csv.reader(file)

    for row in file_reader:
        if len(row) == 1:
            Settings[row[0]] = row[1]

    file.close()
    return True


"""
Writes the current settings to settings file
"""
def record_settings():
    file = open(SETTINGS + "/bluntphy_settings.csv",'w')
    file_writer = csv.writer(file)

    for key in Settings:
        file_writer.writerow([key,Settings[key]])
    
    file.close()
    return True


if __name__ == "__main__":
    set_defaults()
    record_settings()
    get_settings()
    print(Settings)
