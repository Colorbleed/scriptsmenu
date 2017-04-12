import os
import json
from collections import OrderedDict

from Qt import QtGui, QtWidgets

from . import action


class ScriptsMenu(QtWidgets.QMenu):
    """A Qt menu that displays a list of searchable actions"""

    def __init__(self, *args, **kwargs):
        """
        
        :param title: the name of the root menu which will be created
        :type title: str
        
        :param parent: the QObject to parent the menu to
        :type parent: QtWidgets.QObject
        
        :returns: None
        """
        QtWidgets.QMenu.__init__(self, *args, **kwargs)

        self.searchbar = None
        self._script_actions = []
        self._callbacks = {}

        # add default items in the menu
        self.create_default_items()
        
        # Automatically add it to the parent menu
        parent = kwargs.get("parent", None)
        if parent:
            parent.addMenu(self)

    @property
    def registered_callbacks(self):
        return self._callbacks.copy()

    def create_default_items(self):
        """Add a search bar to the top of the menu given"""

        # create widget and link function
        self.searchbar = QtWidgets.QLineEdit()
        self.searchbar.setFixedWidth(120)
        self.searchbar.setPlaceholderText("Search ...")
        self.searchbar.textChanged.connect(self._update_search)

        # create widget holder
        searchbar_action = QtWidgets.QWidgetAction(self)

        # add widget to widget holder
        searchbar_action.setDefaultWidget(self.searchbar)
        searchbar_action.setObjectName("Searchbar")

        # add update button and link function
        # update_action = QtWidgets.QAction(self)
        # update_action.setObjectName("Update Scripts")
        # update_action.setText("Update Scripts")
        # update_action.triggered.connect(self.update_menu)

        # add action to menu
        self.addAction(searchbar_action)
        # self.addAction(update_action)

        # add separator object
        separator = self.addSeparator()
        separator.setObjectName("separator")

    def add_menu(self, parent, title):

        menu = QtWidgets.QMenu(parent, title)
        menu.setTitle(title)
        menu.setObjectName(title)
        parent.addMenu(menu)

        return menu

    def add_script(self, parent, title, command, sourcetype,
                   icon=None, tags=None, label=None, tooltip=None):

        assert tags is None or isinstance(tags, (list, tuple))
        tags = list() if tags is None else list(tags)
        tags.append(title)

        assert icon is None or isinstance(icon, basestring)

        # create new action
        script_action = action.Action(parent)
        script_action.setText(title)
        script_action.setObjectName(title)
        script_action.tags = tags

        # link action to root for callback library
        script_action.root = self

        # Set up the command
        script_action.sourcetype = sourcetype
        script_action.command = command

        try:
            script_action.process_command()
        except RuntimeError as e:
            raise RuntimeError("Script action can't be validly processed: {0}".format(e))

        if icon:
            iconfile = os.path.expandvars(icon)
            script_action.iconfile = iconfile
            script_action_icon = QtGui.QIcon(iconfile)
            script_action.setIcon(script_action_icon)

        if label:
            script_action.label = label

        if tooltip:
            script_action.setStatusTip(tooltip)

        script_action.triggered.connect(script_action.run_command)
        parent.addAction(script_action)

        # Add to our searchable actions
        self._script_actions.append(script_action)

        return script_action

    def register_callback(self, modifiers, callback):
        self._callbacks[int(modifiers)] = callback

    def _update_search(self, search):
        """Hide all the samples which do not match the user's import
        
        :return: None
        """

        if not search:
            for action in self._script_actions:
                action.setVisible(True)
        else:
            for action in self._script_actions:
                if not action.has_tag(search.lower()):
                    action.setVisible(False)

        # Set visibility for all submenus
        for action in self.actions():
            if not action.menu():
                continue

            menu = action.menu()
            visible = any(action.isVisible() for action in menu.actions())
            action.setVisible(visible)


def _load_configuration(path):

    if not os.path.isfile(path):
        raise AttributeError("Given configuration is not "
                             "a file!\n'{}'".format(path))

    extension = os.path.splitext(path)[-1]
    if extension != ".json":
        raise AttributeError("Given configuration file has unsupported "
                             "file type, provide a .json file")

    # retrieve and store config
    with open(path, "r") as f:
        configuration = OrderedDict(json.load(f))
        return configuration


def load_from_configuration(scriptsmenu, configuration):
    """Process the configurations and store the configuration
    
    This creates all submenus from a configuration.json file.

    :param configuration: A ScriptsMenu configuration dictionary
    :type configuration: dict
        
    """

    for menu_name, scripts in configuration.items():

        parent_menu = scriptsmenu.add_menu(parent=scriptsmenu, title=menu_name)

        for script in scripts:
            assert isinstance(script, dict)

            # Special behavior for separators
            if script['title'] == "separator":
                scriptsmenu.addSeparator()
                continue

            scriptsmenu.add_script(parent=parent_menu, **script)


def application(configuration, parent):
    import sys
    app = QtWidgets.QApplication(sys.argv)

    scriptsmenu = ScriptsMenu(configuration, parent)
    scriptsmenu.show()

    sys.exit(app.exec_())
