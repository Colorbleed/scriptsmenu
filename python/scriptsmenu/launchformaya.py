import logging

import maya.cmds as cmds
import maya.mel as mel

import scriptsmenu
from .vendor.Qt import QtCore, QtWidgets


log = logging.getLogger(__name__)


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
    menubar = [i for i in mayawindow.children()
               if isinstance(i, QtWidgets.QMenuBar)]

    assert len(menubar) == 1, "Error, could not find menu bar!"

    return menubar[0]


def _check_title(menu):
    """Wrapped try and except to retrieve the name of the menu
    :param menu: the menu to get the title from
    :type menu: QtWidgets.QMenu instance

    :return: title
    """
    title = None
    try:
        title = menu.title()
    except Exception as e:
        log.debug(e)
        pass

    return title


def _find_scripts_menu(title, parent):
    """
    Check if the menu exists with the given title in the parent

    :param title: the title name of the scripts menu
    :type title: str

    :param parent: the menubar to check
    :type parent: QtWidgets.QMenuBar

    :return: QtWidgets.QMenu or None
    """

    menu = [i for i in parent.children() if
            isinstance(i, scriptsmenu.ScriptsMenu)
            and i.title() == title]

    assert len(menu) < 2, "Multiple instances of {} in menu bar".format(title)
    if len(menu) == 1:
        return menu[0]

    return


def main(title="Scripts", parent=None):
    """Build the main scripts menu in Maya

    :param title: name of the menu in the application
    :type title: str

    :param parent: the parent object for the menu
    :type parent: QtWidgets.QtMenuBar

    :return: scriptsmenu.ScriptsMenu instance
    """

    mayamainbar = parent or _maya_main_menubar()
    try:
        # check menu already exists
        menu = _find_scripts_menu(title, mayamainbar)
        if not menu:
            log.info("Attempting to build menu ...")
            menu = scriptsmenu.ScriptsMenu(title=title, parent=mayamainbar)
    except Exception as e:
        log.error(e)
        return

    # Register control + shift callback to add to shelf (maya behavior)
    modifiers = QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier
    menu.register_callback(modifiers, to_shelf)

    return menu
