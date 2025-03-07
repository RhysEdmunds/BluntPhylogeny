"""
RHYS EDMUNDS

Main backend for the program
"""

from subprocess import Popen,PIPE
from io import TextIOWrapper
from os import makedirs
from os import path
import docker

from Fasta import *
from Settings import Settings
import Settings
import Utils
from Log import log
from Help import bioedit_help


#######################################
#             Preparation             #
#######################################

# --- Checking everything is present in the environment ---

# Settings
#Settings.set_defaults()
Settings.get_settings()

rough_trees_path = Settings['OUTPUT'] + "/5rough_trees"

if Settings['practical']:
    rough_trees_path = Settings['PRACTICAL_OUTPUT']

"""
Sets the environment to run the pasta docker

Checks whether Docker is present on the system
    - if not, asks whether it can install Docker (Is there a Docker lite for just one image?)

Checks whether smirarab/pasta is inlcuded as an image
    - if not, includes it
    
Checks whether Docker has its databases linked
    - if not, links it
"""
def set_pasta_env():
    pasta_sh_lines = []
    
    log("Checking docker exists")
    from shutil import which
    client_exists = (False if which("Docker") is None else True)

    if not client_exists and Settings['can_install'] > 0:
        # TODO: can_install = ask_everytime # TODO: ENUM
        
        log("\tInstalling docker")
        
        # TODO: pulling Docker Desktop installer?
        p = Popen("\"Docker Desktop Installer.exe\" install", stdout=PIPE)
        for line in TextIOWrapper(p.stdout):
            log("\t", line.rstrip())

    elif not client_exists and Settings['can_install'] == 0:
        log("Error: Cannot install Docker due to Settings")
        return False

    # Getting the docker from the environment
    client = docker.from_env()
    
    log("Checking whether smirarab/pasta exists")
    if not 'smirarab/pasta' in client.images.list():
        # Pulling pasta alignment image
        log("Pulling smirarab/pasta")
        client.images.pull("smirarab/pasta")

    # Making sure the -v works:
    # docker run -v [path to the directory with your input files]:/data smirarab/pasta run_pasta.py -i input_fasta [-t starting_tree] 
    log("Checking docker volume links correctly")
    # TODO

    return True



# --- Creating the folders if they don't exist already ---
"""
Creates a folder if a folder doesn't exist at the given path

\input folder_path - a path to the given site
"""
def create_folder_if_not_exists(folder_path):
    # Check if the folder already exists
    if not path.isdir(folder_path):
        try:
            # Create the folder if it doesn't exist
            makedirs(folder_path)
            log(f"Folder '{folder_path}' created successfully.")
        except OSError as e:
            log(f"Error creating folder '{folder_path}': {e}")

    else:
        log(f"Folder '{folder_path}' exists.")

for folder in Settings.folders:
    create_folder_if_not_exists(Settings[folder])



# --- Checking the input is all correct ---

# If doing step 5 (requiring concatenation), 
# TODO
match Settings['start']:
    case 0:
        log("Checking input ascension")
    case 1:
        #Utils.move_file(Settings.input_other_filename,Settings.STEP1)
        log("Need to make it to do")
    case _:
        log("Problem with Settings - no start value")
        exit()






#######################################
#        Creating the commands        #
#######################################

"""
Commands - take in a filepath & return a list for subprocesses to develop

/param - varies, generally the fasta file

/return - a list for subprocesses
"""


def pasta_command(fasta):
    # From Settings, a program creating the correct pasta.sh
    set_pasta_env()
    return [Settings['PASTA'] + "/pasta.sh"]

def bioedit_command(fasta):
    return [Settings['BIOEDIT'] + "/BioEdit.exe",fasta]

def gblocks_command(fasta):
    return [Settings['GBLOCKS'] + "/Gblocks.exe",fasta]

def figview_command(tre):
    return [Settings['FIGVIEW'] + "/FigTree v1.4.4.exe",tre]







#######################################
#         Running the program         #
#######################################

# --- Step 1 - getting the .fasta files from the ascension number input
if Settings['start'] < 1 and 1 <= Settings['end']:
    os.chdir(Settings['INPUT'])
    # TODO If not empty
    step_1(Settings['email'],Settings['input_ascension_filename'],[Settings['STEP1'],Settings['STEP1'],Settings['ROOT_PATH']]) # This moves the files in & of themselves to Settings['STEP1




# --- Step 2 - running the pasta program
if Settings['start'] < 2 and 2 <= Settings['end']:
    os.chdir(Settings['STEP1']) # Input is the output of the step before

    # EXAMPLE CHANGES OF FILENAME
    #pastajob.marker001.16S.aln -> 16S.aln
    #pastajob.tre -> 16S.tre

    fastas = Utils.get_fasta_filenames(Settings['STEP1'])

    for fasta in fastas:
        log("\n\n\nRunning pasta alignment on " + fasta + ":")

        # Running the pasta
        p = Popen(pasta_command(fasta),stdout=PIPE)

        # Logs the output 
        for line in TextIOWrapper(p.stdout):
            log("\t", line.rstrip())
        
        # Moving & renaming fasta files as appropriate
        log("Moving & renaming output to " + Settings['STEP2'])

        aln_filename = "pastajob.marker001."+fasta[:-6]+".aln"
        aln_filename_new = Settings['STEP2'] + "/" + fasta
        Utils.rename_file([aln_filename],[aln_filename_new])
        
        # Moving & renaming NJ trees to the output
        log("Moving & renaming rough trees to " + rough_trees_path)

        tre_filename = "pastajob.tre"
        tre_filename_new = rough_trees_path + fasta[:-6]+".tre"
        Utils.rename_file(tre_filename,tre_filename_new)
        
        # Opening trees for inspection
        if Settings['inspect_trees']:
            log("\nOpening tree for inspection")

            p = Popen(figview_command(tre_filename_new), stdout=PIPE)
            for line in TextIOWrapper(p.stdout):
                log("\t", line.rstrip())




# --- Step 3 - editing the files
if Settings['start'] < 3 and 3 <= Settings['end']:
    os.chdir(Settings['STEP2']) # Input is the output of the step before
    
    fastas = Utils.get_fasta_filenames(".")

    for fasta in fastas:
        log("\n\n\nRunning manual edit & inspection on " + fasta + ":")

        # If not too large
        Utils.copy_file(fasta)

        # Running the bioedit
        p = Popen(bioedit_command(fasta), stdout=PIPE)

        # Creating the help window
        bioedit_help(encoding = True) if Settings.is_encoding(fasta[:-6]) else bioedit_help() # is_encoding from Settings

        # Logs the output
        for line in TextIOWrapper(p.stdout):
            log("\t", line.rstrip())

        # Waiting until the bioedit has finished
        p.communicate()

        # TODO If not empty
        Utils.move_file(fasta,Settings['STEP3'])




# --- Step 4 - Making the files spaceless
if Settings['start'] < 4 and 4 <= Settings['end']:
    os.chdir(Settings['STEP3']) # Input is the output of the step before
    
    fastas = Utils.get_fasta_filenames(".")

    for fasta in fastas:
        if Settings.is_encoding(fasta[:-6]):
            Utils.move_file(fasta,Settings['STEP4'])
            continue
        
        log("\n\n\nRunning GBlocks on " + fasta + ":")

        # If not too large
        Utils.copy_file(fasta)

        # Running the bioedit
        p = Popen(gblocks_command(fasta), stdout=PIPE)

        # Logs the output
        for line in TextIOWrapper(p.stdout):
            log("\t", line.rstrip())
        
        Utils.move_file(fasta,Settings['STEP4'])




# --- Step 5 - running MrBayes
if Settings['start'] < 5 and 5 <= Settings['end']:
    os.chdir(Settings['STEP4']) # Input is the output of the step before
    #### PREPARING FOR MR BAYES
    # Gets current list of fastas in a given file
    fasta_list = Utils.get_fasta_filenames(".")

    ### CONCATENATING
    if len(fasta_list) > 1:
        # Gets the enum file
        enum_filename = Settings['SETTINGS'] + "enum_" + Settings['input_ascension_filename']

        # Concatenating
        concatenated_filename = generateConcatenateName(fasta_list) # The filename for the concatenation
                                            # important in identifying which files are concatenated
                                            # & what the name of the gene files is for MrBayes later
        fasta_filename = concatenateFastas(fasta_list,enum_filename,concatenated_filename)

        # Creating tree
        tre_filename = rough_tree(fasta_filename)

        # Checking concatenated tree looks alright
        log("Moving & renaming rough tree to " + rough_trees_path)

        tre_filename_new = rough_trees_path + tre_filename
        Utils.rename_file(tre_filename,tre_filename_new)
        
        # Opening trees for inspection
        if Settings['inspect_trees']:
            log("\nOpening tree for inspection")
            p = Popen(figview_command(tre_filename_new), stdout=PIPE)
            for line in TextIOWrapper(p.stdout):
                log("\t", line.rstrip())

    ### CONVERTING TO NEXUS FOR MR BAYES
    # Getting the current list of fastas, with the concatenated set
    gene_list = Utils.get_fasta_filenames(".")

    # Removing the file endings ".fasta", the last 6 characters
    gene_list = [g[:-6] for g in gene_list]
    for gene in gene_list:
        fasta_to_nexus(gene,gene)
    

    ### APPENDING THE MR BAYES TRANSCRIPT
    # Opening the class (why did I do this object-orientated)
    mbs = MrBayesSettings()

    for gene in gene_list:
        # It matters what the first 12 characters of the filename is, which is in "GenerateConcatenateName"
        
        # TODO CHECK 11 IS RIGHT WHILST TESTING
        # Generating the transcript, providing the gene length file path for the concatenated gene
        mb_transcript_lines = mbs.generate_transcript(True, concatenated_filename + "_gene_lengths.csv") if (gene[:11]=="concatenate") else mbs.generate_transcript(False)

        # Appending the transcript onto the .nexus file
        # TODO
    

    ### RUNNING MR BAYES # TODO
    # TODO Option to do so manually







#######################################
#              Clean up               #
#######################################

# TODO: remove the settings enum file
# TODO: If intermediaries are empty, remove the temp files