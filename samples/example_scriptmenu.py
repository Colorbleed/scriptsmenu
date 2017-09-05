import os
import sys

from Qt import QtWidgets, QtGui

from scriptsmenu import ScriptsMenu
from scriptsmenu.scriptsmenu import (
    load_configuration,
    build_from_configuration
)

# set the example evironment variable
os.environ["SCRIPTMENU"] = os.path.dirname(__file__)
config = os.path.expandvars(r"$SCRIPTMENU/sample_configuration_a.json")
config = load_configuration(config)    # parse the .json file

app = QtWidgets.QApplication(sys.argv)

menu = ScriptsMenu(title="Scripts", parent=None)

# populate the menu using the configuration JSON file.
menu.build_from_configuration(menu, config)

menu.exec_(QtGui.QCursor.pos())

app.exec_()
