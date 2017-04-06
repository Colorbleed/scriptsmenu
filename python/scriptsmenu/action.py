import os
from PySide import QtGui


class Action(QtGui.QAction):
    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, parent)
        self._root = None
        self._taglist = None
        self._command = None
        self._sourcetype = None
        self._iconfile = None
        self._label = None

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    @property
    def taglist(self):
        return self._taglist

    @taglist.setter
    def taglist(self, value):
        """Add the value to the list"""
        self._taglist = value

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def sourcetype(self):
        return self._sourcetype

    @sourcetype.setter
    def sourcetype(self, value):
        """
        Set the command type to get the correct execution of the command given
        :param value: the name of the command type
        :type value: str
        
        :return: None 
        """
        self._sourcetype = value

    @property
    def iconfile(self):
        return self._iconfile

    @iconfile.setter
    def iconfile(self, value):
        self._iconfile = value

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    def run_command(self):
        """
        Run the command stored in the instance or copy the command to the 
        active shelf
        
        :return: None
        """

        # get the current application and its linked keyboard modifiers
        app = QtGui.QApplication.instance()
        modifiers = app.keyboardModifiers()

        # If the menu has a callback registered for the current modifier
        # we run the callback instead of the action itself.
        callbacks = self._root.registered_callbacks
        callback = callbacks.get(int(modifiers), None)
        if callback:
            callback(self)
            return

        exec(self.process_command())

    def process_command(self):
        """
        Check if the command is a file which needs to be launched and if it 
        has a relative path, if so return the full path by expanding 
        environment variables.
        
        Add your own source type and required action to ensure callback
        is stored correctly

        :return: a clean command
        :rtype: str
        """
        if self._sourcetype == "python":
            return self._command

        if self._sourcetype == "mel":
            # Escape single quotes
            conversion = self._command.replace("'", "\\'")
            return "import maya; maya.mel.eval('{}')".format(conversion)

        if self._sourcetype == "file":
            if os.path.isabs(self._command):
                string = os.path.normpath(self._command)
            else:
                string = os.path.normpath(os.path.expandvars(self._command))

            return 'execfile("{}")'.format(string)
