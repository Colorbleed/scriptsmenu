from .vendor.Qt import QtGui, QtCore, QtWidgets

import maya.cmds as cmds
import maya.mel as mel

import scriptsmenu


def to_shelf(action):
    """
    Copy clicked menu item to the currently active Maya shelf 

    :param action: the action instance which is clicked
    :type action: QtGui.QAction

    :return: None
    """

    shelftoplevel = mel.eval("$gShelfTopLevel = $gShelfTopLevel;")
    current_active_shelf = cmds.tabLayout(shelftoplevel,
                                          query=True,
                                          selectTab=True)

    cmds.shelfButton(command=action.process_command(),
                     sourceType="python",
                     parent=current_active_shelf,
                     image=action.iconfile or "pythonFamily.png",
                     annotation=action.statusTip(),
                     imageOverlayLabel=action.label or '')


def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


def _maya_main_menubar():
    """Retrieve the main menubar of the Maya window"""
    mayawindow = _maya_main_window()
    menubar = [i for i in mayawindow.children() if isinstance(i, QtWidgets.QMenuBar)]

    assert len(menubar) == 1, "Error, could not find menu bar!"
    return menubar[0]


def main(title="Scripts"):
    mayamainbar = _maya_main_menubar()
    menu = scriptsmenu.ScriptsMenu(title=title,
                                   parent=mayamainbar)

    # Register control + shift callback to add to shelf (maya behavior)
    modifiers = QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier
    menu.register_callback(modifiers, to_shelf)

    return menu
