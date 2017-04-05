import os
import json
from collections import OrderedDict

from PySide import QtGui

import configuration
import action


class ScriptsMenu(QtGui.QMenu):

    def __init__(self):
        QtGui.QMenu.__init__(self)

        self.searchbar = None
        self.script_configurations = None
        self._script_actions = []
        self._default_items = ["Searchbar", "Update Scripts"]

        self._process_configuration()

    def _process_configuration(self):
        """Process the configurations"""

        if os.path.isfile(configuration.scriptspath):
            configfile = configuration.scriptspath
        else:
            configfile = os.path.join(os.path.dirname(__file__),
                                      'scripts.json')

        # get settings
        with open(configfile, "r") as f:
            self.script_configurations = OrderedDict(json.load(f))

    def create_menu(self, parent):
        """Create the main menu which holds all the scripts"""

        self.setTitle(configuration.menutitle)

        # add search bar
        self.create_searchbar()

        # add update button
        update_action = QtGui.QAction(self)
        update_action.setObjectName("Update Scripts")
        update_action.setText("Update Scripts")
        self.addAction(update_action)

        # iter over department configurations
        for department, configurations in self.script_configurations.items():
            menu = self.create_department_menu(department)
            self.create_script_entries(menu, configurations)

        # link function to search bar
        self.searchbar.textChanged.connect(self._search_for_script)
        update_action.triggered.connect(self.update_menu)

        if parent:
            parent.addMenu(self)

    def create_searchbar(self):
        """
        Add a searchbar to the top of the menu given
        
        :param parent: a menu instance
        :type parent: QtGui.QMenu
        
        :return: None 
        """

        # create widget
        self.searchbar = QtGui.QLineEdit()
        self.searchbar.setFixedWidth(120)
        self.searchbar.setPlaceholderText("Search ...")

        # create widget holder
        searchbar_action = QtGui.QWidgetAction(self)
        # add widget to widget holder
        searchbar_action.setDefaultWidget(self.searchbar)
        searchbar_action.setObjectName("Searchbar")

        # link widget holder to parent
        self.addAction(searchbar_action)

    def update_menu(self):
        """Update the menu items without destroying the existing menu"""

        self._process_configuration()

        departments = self.actions()
        for department, configs in self.script_configurations.items():
            # check if department menu exists
            actions = [d for d in departments if d.text() == department]
            if actions:
                # remove found department menu
                script_action = actions[0]
                self.removeAction(script_action)
                departments.remove(script_action)

            # create new menu item
            menu = self.create_department_menu(department)
            self.create_script_entries(menu, configs)

        # remove left overs if there are any while keep the default
        if len(departments) != len(self._default_items):
            for department in departments:
                if department.text() not in self._default_items:
                    self.removeAction(department)

    def create_department_menu(self, department):
        """
        Create the department menu which acts as a parent for the script menu 
        items

        :param parent: The parent to add the new menu under
        :type parent: QtGui.QWidget object

        :param department: the name of the department which will be the title
        :type department: str

        :return: QtGui.QMenu instance
        """

        department_menu = QtGui.QMenu()
        department_menu.setTitle(department)
        department_menu.setObjectName(department)

        self.addMenu(department_menu)

        return department_menu

    def create_script_entries(self, parent, configurations):
        """
        Create all sub menu items which launch the scripts

        :param parent: the parent widget to add the new menu to
        :type parent: QtGui.QMenu

        :param configurations: a collection of action configurations
        :type configurations: list

        :return: None
        """

        for config in configurations:
            name = config["title"]

            if name == "separator":
                parent.addSeparator()
                continue

            script_action = self._create_script_action(name, config, parent)
            parent.addAction(script_action)

            # add item instance to tool for quick search
            self._script_actions.append(script_action)

    def _create_script_action(self, name, configuration, parent):
        """
        Create a custom action instance which can be added to the menu
        
        :param name: the display name of the action
        :type name: str
        
        :param configuration: the settings for action such as command, 
        command type, taglist
        :type configuration: dict
        
        :param parent: the parent widget to wich it will be linked
        :type parent: QtGui.QWidget        
                
        :return: an action instance
        :rtype QtGui.QAction
        """

        # add name to tag
        configuration["taglist"].append(name)

        # create new action
        script_action = action.Action(parent)
        script_action.setText(name)
        script_action.setObjectName(name)

        # add information to the action
        script_action.setStatusTip(configuration["tooltip"])
        script_action.taglist = configuration["taglist"]

        # connect to internal command
        script_action.commandtype = configuration["type"]

        # get correct path if the command is a file
        script_action.command = self._process_command(configuration["command"],
                                                      configuration["type"])
        script_action.triggered.connect(script_action.run_command)

        return script_action

    def _process_command(self, command, commandtype=None):
        """
        Check if the command is a file which needs to be launched and if it 
        has a relative path, if so return the full path by expanding 
        environment variables.
        
        :param command: the path to the command to 
        :type command: str
        
        :param commandtype: set the type of command which the action will 
        trigger when pressed. Currently supported : "file", "mel", "python"
        :type commandtype: str
        
        :return: a clean command
        :rtype: str
        """
        if commandtype != "file":
            return command

        if os.path.isabs(command):
            return os.path.normpath(command)
        else:
            return os.path.normpath(os.path.expandvars(command))

    def _search_for_script(self):
        """
        Hide all he scripts which do not match the user's import
        
        :return: None
        """

        current_text = self.searchbar.text()
        if current_text == '':
            for action in self._script_actions:
                action.setVisible(True)

        for action in self._script_actions:
            if not self._get_match(action, current_text):
                action.setVisible(False)

    def _get_match(self, action, tag):
        """Check of action has tags have a match with given tag"""

        has_match = False
        for tagitem in action.taglist:
            if tag not in tagitem:
                continue
            has_match = True

        return has_match

    def _is_department_live(self, parent, department):
        """
        Check of the CB Scripts root menu is already in the menubar
        
        :param menubar: the menubar of the Maya main window
        :type menubar: QtGui.QMenu
        
        :param department: the title of the menu item
        :type department: str
        
        :return: the CB Script instance or None
        :rtype: QtGui.QMenu
        """
        child = [ch for ch in parent.children() if isinstance(ch, QtGui.QMenu)
                 and ch.title() == department]

        if child:
            child = child[0]

        return child


def application(parent=None):
    import sys
    app = QtGui.QApplication(sys.argv)

    scriptsmenu = ScriptsMenu()
    scriptsmenu.create_menu(parent)
    scriptsmenu.show()

    sys.exit(app.exec_())


def main(parent=None):
    global script_menu
    script_menu = ScriptsMenu()
    script_menu.create_menu(parent)


if __name__ == '__main__':
    main()
