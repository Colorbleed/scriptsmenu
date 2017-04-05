import shiboken
from PySide import QtGui

import maya.OpenMayaUI as omui

import scriptsmenu


def getmayawindow():

    """Retrieve the main menubar of the Maya window"""
    parent = omui.MQtUtil.mainWindow()
    if not parent:
        raise AttributeError("Could not find instance of the Maya Main window")

    shiboken_inst = shiboken.wrapInstance(long(parent), QtGui.QWidget)

    mayawindow_children = shiboken_inst.children()
    menubar = [i for i in mayawindow_children if isinstance(i, QtGui.QMenuBar)]

    assert len(menubar) == 1, "Error, could not find menu bar!"
    return menubar[0]


def main():
    mayamainbar = getmayawindow()
    scriptsmenu.main(mayamainbar)


if __name__ == '__main__':
    main()

