"""
Rhys Edmunds

Help windows - provide instructions & helpful advice in window pop-ups as they're going through the process

Will be used by both main (during the manual parts) and by the GUI code
"""
from Log import log


"""
Opens an informational window with a locked "Done" button that is always visible

If the done button is pressed, closes the window

If encoding is true:
    Also includes information about translation & inspecting the translate
"""
# TODO
def bioedit_help(encoding = False):
    log("Opening bioedit help window")