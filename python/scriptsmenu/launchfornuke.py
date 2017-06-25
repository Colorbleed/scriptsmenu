import scriptsmenu
from dependencies.Qt import QtCore, QtWidgets


def _nuke_main_window():
    """Return Nuke's main window"""
    return QtWidgets.QApplication.activeWindow()


def _nuke_main_menubar():
    """Retrieve the main menubar of the Nuke window"""
    nuke_window = QtWidgets.QApplication.activeWindow()
    menubar = [i for i in nuke_window.children() if isinstance(i, QtWidgets.QMenuBar)]

    assert len(menubar) == 1, "Error, could not find menu bar!"
    return menubar[0]


def main(title="Scripts"):
    nuke_main_bar = _nuke_main_menubar()
    menu = scriptsmenu.ScriptsMenu(title=title,
                                   parent=nuke_main_bar)

    # Register control + shift callback to add to shelf (Nuke behavior)
    modifiers = QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier
    # menu.register_callback(modifiers, to_shelf)

    return menu
