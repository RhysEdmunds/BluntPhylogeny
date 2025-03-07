import csv
import os

import Log



"""
Create enumerated file

/param ascension_filename - a string of the csv input_ascensions file to open & create the enumerated file for
    in the form: | Taxon | Gene1 | Gene2 ...

Creates an enum_<input_filename>, should end with .csv
    in the form | Enum_id | Taxon |
                |   int   |  str  |
"""
def create_enum(ascension_filename):
    Log.log("Creating enumeration file for " + ascension_filename)

    ascension_file = open(ascension_filename, 'r')
    ascension_reader = csv.DictReader(ascension_file)

    # Setting the first column to be right - often excel changes this
    ascension_fieldnames = ascension_reader.fieldnames
    ascension_fieldnames[0] = "Taxon"

    enum_filename = "enum_" + ascension_filename
    enum_file = open(enum_filename, 'w')
    enum_fieldnames = ["Enum_id","Taxon"]
    enum_writer = csv.DictWriter(enum_file,fieldnames=enum_fieldnames)

    enum_writer.writeheader()

    enum = 0
    for ascension_row in ascension_reader:
        enum_row = {enum_fieldnames[0]:enum, enum_fieldnames[1]:ascension_row["Taxon"]}
        enum_writer.writerow(enum_row)
        enum+=1
    
    ascension_file.close()
    enum_file.close()

    return enum_filename





"""
A function that gets the names of all the fasta files in a given directory
"""
def get_fasta_filenames(directory):
    # Get all files in the directory
    files = os.listdir(directory)

    # Filter only fasta files
    return [file for file in files if file.endswith('.fasta')]



### TODO TODO TODO TODO

"""
Moves a file to a given directory

if there's already the file with the same name there, backs it up & replaces it

/param input_filename
/param new_directory

/return True or False depending on success
"""
def move_file(input_filename,new_directory):
    Log.log("Moving file " + input_filename + " TODO")
    return False


"""
Moves a list of files file to a given directory

if there's already the file with the same name there, backs it up & replaces it

/param input_filenames
/param new_directory

/return True or False depending on success
"""
def move_files(input_filenames,new_directory):
    Log.log("Moving file " + input_filenames + " TODO")
    return False


"""
Moves a list of files file to a given directory

if there's already the file with the same name there, backs it up & replaces it

/param input_filenames
/param new_filenames - a list of the same length as above

/return True or False depending on success
"""
def rename_files(input_filenames,new_filenames):
    Log.log("Renaming files " + input_filenames + " TODO")
    return False


"""
Deletes files, either by moving them to a .zip file, or by pernamently deleting them

/param input_filenames
/param pernament - whether or not to backup

/return True or False depending on success
"""
def delete_files(input_filenames,pernament=False):
    Log.log("Deleting files " + input_filenames + " TODO")
    return False


"""
Copy file, copies a file to a new directory

/param input_filename
/param directory

If the file already exists, appends .copy onto the end

/return True or False depending on success
"""
def copy_file(input_filename,directory = "."):
    Log.log("Copying file " + input_filename + " to " + directory)
    return False
