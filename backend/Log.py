"""
Log.py CLI
Developer: Rhys Edmunds
Created: 

This logging file is designed to interact with a command line interface
It should be a viable version in and of itself
Another Log.py will be created to interact via eel with a html GUI, where there is also a logging section to the program
"""


""" LOGS A GIVEN STRING """
def log(inp):
    print(inp) # For a CLI, this is just printing it


""" Forms a checkpoint
Prints the checkpoint position out of a total number
*TODO MAY CHANGE TO PERCENTAGE*
TODO Clears the string buffer beforehand

returns the next checkpoint number
"""
def checkpoint(head,count,tot = 0,remove=True):
    # If previous line includes 'checkpoint', clear it

    to_log = ""
    to_log += "\t" + head + ": checkpoint " + str(count)
    if (tot != 0):
        to_log += "/" + str(tot)
    log(to_log)

    return count+1


""" Queries the user for input
TODO: Becomes part of Settings
"""
def ask(message):
    print("Doing: " + message)