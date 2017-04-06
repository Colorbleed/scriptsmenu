import shiboken
from PySide import QtGui, QtCore

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

import scriptsmenu


def toshelf(action):
    """
    Copy clicked menu item to the currently active Maya shelf 

    :param action: the action instance which is clicked
    :type action: QtGui.QAction

    :return: None
    """

    sourcetype = action.sourcetype

    shelftoplevel = mel.eval("$gShelfTopLevel = $gShelfTopLevel;")
    current_active_shelf = cmds.tabLayout(shelftoplevel,
                                          query=True,
                                          selectTab=True)
    if sourcetype == "file":
        sourcetype = "python"

    cmds.shelfButton(command=action.command,
                     image="pythonFamily.png",
                     sourceType=sourcetype,
                     parent=current_active_shelf)


def _getmayawindow():
    """Retrieve the main menubar of the Maya window"""
    parent = omui.MQtUtil.mainWindow()
    if not parent:
        raise AttributeError("Could not find instance of the Maya Main window")

    shiboken_inst = shiboken.wrapInstance(long(parent), QtGui.QWidget)

    mayawindow_children = shiboken_inst.children()
    menubar = [i for i in mayawindow_children if isinstance(i, QtGui.QMenuBar)]

    assert len(menubar) == 1, "Error, could not find menu bar!"
    return menubar[0]


def main(configuration, title):
    mayamainbar = _getmayawindow()
    menu = scriptsmenu.main(configuration,
                            title=title,
                            parent=mayamainbar)

    # Register control + shift callback to add to shelf (maya behavior)
    modifiers = QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier
    menu.register_callback(modifiers, toshelf)
