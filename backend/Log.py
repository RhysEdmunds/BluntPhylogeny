
""" LOGS A GIVEN STRING
TODO: Should pass the input to eel to display in one of the tabs, this should be in the front-end of thing?
"""
def log(inp):
    print(inp)


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