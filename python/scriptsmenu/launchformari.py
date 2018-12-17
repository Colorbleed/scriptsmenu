
# Import third-party modules
from vendor.Qt import QtWidgets

# Import local modules
import scriptsmenu


def _mari_main_window():
    """Get mari main window.

    Returns:
        MriMainWindow: Mari's main window.

    """
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.metaObject().className() == 'MriMainWindow':
            return obj
    raise RuntimeError('Could not find Nuke MainWindow instance')


def _nuke_main_menubar():
    """Retrieve the main menubar of the Nuke window"""
    nuke_window = _mari_main_window()
    menubar = [
        i for i in nuke_window.children() if isinstance(i, QtWidgets.QMenuBar)
    ]
    assert len(menubar) == 1, "Error, could not find menu bar!"
    return menubar[0]


def main(title="Scripts"):
    """Build the main scripts menu in Maya

    Args:
        title (str): name of the menu in the application

        parent (QtWidgets.QtMenuBar): the parent object for the menu

        objectName (str): custom objectName for scripts menu

    Returns:
        scriptsmenu.ScriptsMenu instance

    """
    mari_main_bar = _mari_main_window()
    for mari_bar in mari_main_bar.children():
        if isinstance(mari_bar, scriptsmenu.ScriptsMenu):
            if mari_bar.title() == title:
                print mari_bar.title()
                menu = mari_bar
                return menu
    menu = scriptsmenu.ScriptsMenu(title=title, parent=mari_main_bar)
    return menu