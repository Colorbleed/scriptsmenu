import maya.cmds as cmds
import maya.mel as mel


def toshelf(command, sourcetype):
    """
    Copy clicked menu item to the currently active Maya shelf 
    
    :param command: the command to run when clicked
    :type command: str
    
    :param sourcetype: the command type in which the button needs to be set
    :type sourcetype: str
    
    :return: None
    """

    shelftoplevel = mel.eval("$nul = $gShelfTopLevel;")
    current_active_shelf = cmds.tabLayout(shelftoplevel,
                                          query=True,
                                          selectTab=True)
    if sourcetype == "file":
        sourcetype = "python"

    cmds.shelfButton(command=command,
                     image="pythonFamily.png",
                     sourceType=sourcetype,
                     parent=current_active_shelf)
