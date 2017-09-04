import json
import logging
import os
from collections import OrderedDict


from .vendor.Qt import QtWidgets, QtCore
from . import action

log = logging.getLogger(__name__)


class ScriptsMenu(QtWidgets.QMenu):
    """A Qt menu that displays a list of searchable actions"""

    updated = QtCore.Signal(QtWidgets.QMenu)

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

        # Automatically add it to the parent menu
        parent = kwargs.get("parent", None)
        if parent:
            parent.addMenu(self)

        objectname = kwargs.get("objectName", "scripts")
        title = kwargs.get("title", "Scripts")
        self.setObjectName(objectname)
        self.setTitle(title)

        # add default items in the menu
        self.create_default_items()

    def on_update(self):
        self.updated.emit(self)

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
        update_action = QtWidgets.QAction(self)
        update_action.setObjectName("Update Scripts")
        update_action.setText("Update Scripts")
        update_action.setVisible(False)
        update_action.triggered.connect(self.on_update)

        # add action to menu
        self.addAction(searchbar_action)
        self.addAction(update_action)

        # add separator object
        separator = self.addSeparator()
        separator.setObjectName("separator")

    def add_menu(self, parent, title):
        """
        Create a sub menu for a parent widget
        
        :param parent: the object to parent the menu to
        :type parent: QtWidgets.QWidget
        
        :param title: the title of the menu
        :type title: str
        
        :return: QtWidget.QMenu instance
        """

        menu = QtWidgets.QMenu(parent, title)
        menu.setTitle(title)
        menu.setObjectName(title)
        menu.setTearOffEnabled(True)
        parent.addMenu(menu)

        return menu

    def add_script(self, parent, title, command, sourcetype, icon=None,
                   tags=None, label=None, tooltip=None):
        """
        Create a clickable menu item which runs a script when clicked
        
        :param parent: The widget to parent the item to
        :type parent: QtWidget.QWidget
        
        :param title: The text which will be displayed in the menu
        :type title: str
        
        :param command: The command which needs to be run when the item is 
        clicked.
        :type command: str
        
        :param sourcetype: The type of command, the way the command is 
        processed is based on the source type.
        :type sourcetype: str
        
        :param icon: The file path of an icon to display with the menu item
        :type icon: str
        
        :param tags: Keywords which describe a the actions of a scripts
        :type tags: (list, tuple)
        
        :param label: A short description of the script which will be displayed
        when hovering over the menu item
        
        :param tooltip: A tip for the user about the usage fo the tool
        :type tooltip: str
        
        :return: an instance of QtWidget.QAction
        """

        assert tags is None or isinstance(tags, (list, tuple))
        # Ensure tags is a list
        tags = list() if tags is None else list(tags)
        tags.append(title.lower())

        assert icon is None or isinstance(icon, str), (
            "Invalid data type for icon, supported : None, string")

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
            raise RuntimeError("Script action can't be "
                               "processed: {}".format(e))

        if icon:
            iconfile = os.path.expandvars(icon)
            script_action.iconfile = iconfile
            script_action_icon = QtWidgets.QIcon(iconfile)
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

    def set_update_visible(self, state):
        self.update_action.setVisible(state)

    def clear_menu(self):
        """
        Clear all menu items which are not default
        :return: None
        """

        # TODO: Set up a more robust implementation for this
        # Delete all except the first three actions
        for _action in self.actions()[3:]:
            self.removeAction(_action)

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


def create_submenu(menu, script, parent, items):

    title = script["title"]
    submenu = menu.add_menu(parent=parent, title=title)
    for item in items:
        assert isinstance(script, dict), "Configuration is wrong!"
        if item['title'] == "separator":
            submenu.addSeparator()
            continue

        menu.add_script(parent=submenu, **item)


def load_configuration(path):

    if not os.path.isfile(path):
        raise AttributeError("Given configuration is not "
                             "a file!\n'{}'".format(path))

    extension = os.path.splitext(path)[-1]
    if extension != ".json":
        raise AttributeError("Given configuration file has unsupported "
                             "file type, provide a .json file")

    # retrieve and store config
    with open(path, "r") as f:
        data = json.load(f)

    # check if configuration has an specific order
    order = data.get("order", None)
    if order is not None:
        configuration = OrderedDict()
        for key in order:
            configuration[key] = data[key]
    else:
        configuration = data

    return configuration


def load_from_configuration(menu, configuration):
    """Process the configurations and store the configuration
    
    This creates all submenus from a configuration.json file.

    When the configuration holds the key `main` all scripts under `main` will
    be added to the main menu first before adding the rest

    Args:
        menu (QtGui.QMenu): menu instance
        configuration (dict): A ScriptsMenu configuration dictionary
    """

    # todo: improve for-loop, too complex

    for section, scripts in configuration.items():

        if section == "main":
            parent_menu = menu
        else:
            parent_menu = menu.add_menu(parent=menu, title=section)

        for script in scripts:
            assert isinstance(script, dict), "Configuration is wrong!"
            # Special behavior for separators
            if script['title'] == "separator":
                menu.addSeparator()
                continue

            # items should hold a collection of submenu items (dict)
            items = script.get("items", None)
            if items:
                create_submenu(menu, script, parent_menu, items)
                continue

            menu.add_script(parent=parent_menu, **script)


def application(configuration, parent):
    import sys
    app = QtWidgets.QApplication(sys.argv)

    scriptsmenu = ScriptsMenu(configuration, parent)
    scriptsmenu.show()

    sys.exit(app.exec_())
