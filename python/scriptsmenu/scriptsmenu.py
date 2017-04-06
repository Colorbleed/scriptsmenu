import os
import json
from collections import OrderedDict

from PySide import QtGui

import action
reload(action)


class ScriptsMenu(QtGui.QMenu):

    def __init__(self, configuration, title, parent=None):
        """
        
        :param configuration: the path to the configuration file which dictates
        the which buttons get created with which command
        :type configuration: str
        
        :param title: the name of the root menu which will be created
        :type title: str
        
        :param parent: the QObject to parent the menu to
        :type parent: QtGui.QObject
        
        :returns: None
        """
        QtGui.QMenu.__init__(self)

        self.searchbar = None
        self.script_configurations = None
        self._script_actions = []
        self._callbacks = {}

        self._parent = parent
        # normalize path to match the OS
        self._configuration = os.path.normpath(configuration)
        self._default_items = ["Searchbar", "Update Scripts"]

        self._process_configuration()

        self.setTitle(title)

        # add default items in the menu
        self.create_default_items()

        # add items from configuration
        self.update_menu()

        if self._parent:
            self._parent.addMenu(self)

    @property
    def registered_callbacks(self):
        return self._callbacks.copy()

    def _process_configuration(self):
        """Process the configurations and store the configuration"""

        if not os.path.isfile(self._configuration):
            raise AttributeError("Given configuration is not "
                                 "a file!\n'{}'".format(self._configuration))

        extension = os.path.splitext(self._configuration)[-1]
        if extension != ".json":
            raise AttributeError("Given configuration file has unsupported "
                                 "file type, provide a .json file")

        # retrieve and store config
        with open(self._configuration, "r") as f:
            self.script_configurations = OrderedDict(json.load(f))

    def create_default_items(self):
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

        # add update button
        update_action = QtGui.QAction(self)
        update_action.setObjectName("Update Scripts")
        update_action.setText("Update Scripts")
        update_action.triggered.connect(self.update_menu)

        # add action to menu
        self.addAction(searchbar_action)
        self.addAction(update_action)

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
            self.create_menu_entries(menu, configs)

        # remove left overs if there are any while keep the default
        if len(departments) != len(self._default_items):
            for department in departments:
                if department.text() not in self._default_items:
                    self.removeAction(department)

    def create_department_menu(self, department):
        """
        Create the department menu which acts as a parent for the script menu 
        items

        :param department: The parent to add the new menu under
        :type department: QtGui.QWidget object

        :param department: the name of the department which will be the title
        :type department: str

        :return: QtGui.QMenu instance
        """

        department_menu = QtGui.QMenu()
        department_menu.setTitle(department)
        department_menu.setObjectName(department)

        self.addMenu(department_menu)

        return department_menu

    def create_menu_entries(self, parent, configurations):
        """
        Create all sub menu items which launch the samples

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

            script_action = self._create_script_action(name, config,
                                                       self, parent)
            parent.addAction(script_action)

            # add item instance to tool for quick search
            self._script_actions.append(script_action)

    def _create_script_action(self, name, configuration, root, parent):
        """
        Create a custom action instance which can be added to the menu
        
        :param name: the display name of the action
        :type name: str
        
        :param configuration: the settings for action such as command, 
        command type, taglist
        :type configuration: dict
        
        :param root: the parent widget to which it will be linked
        :type root: QtGui.QMenu
        
        :param parent: the parent widget to which it will be linked
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

        # link action to root for callback library
        script_action.root = root

        # apply icon if found
        if "icon" in configuration:
            iconfile = os.path.expandvars(configuration["icon"])
            script_action.iconfile = iconfile
            script_action_icon = QtGui.QIcon(iconfile)
            script_action.setIcon(script_action_icon)

        if 'label' in configuration:
            script_action.label = configuration['label']

        # add information to the action
        script_action.setStatusTip(configuration["tooltip"])
        script_action.taglist = configuration["taglist"]

        # connect to internal command
        script_action.sourcetype = configuration["type"]

        # get correct path if the command is a file
        script_action.command = self._process_command(configuration["command"],
                                                      configuration["type"])

        script_action.triggered.connect(script_action.run_command)

        return script_action

    def _process_command(self, command, sourcetype=None):
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
        if sourcetype != "file":
            return command

        if os.path.isabs(command):
            return os.path.normpath(command)
        else:
            return os.path.normpath(os.path.expandvars(command))

    def _search_for_script(self):
        """
        Hide all he samples which do not match the user's import
        
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

    def register_callback(self, modifiers, callback):
        self._callbacks[int(modifiers)] = callback


def application(configuration, parent):
    import sys
    app = QtGui.QApplication(sys.argv)

    scriptsmenu = ScriptsMenu(configuration, parent)
    scriptsmenu.show()

    sys.exit(app.exec_())


def main(configuration, title, parent=None):
    global script_menu
    script_menu = ScriptsMenu(configuration, title, parent)
    return script_menu
