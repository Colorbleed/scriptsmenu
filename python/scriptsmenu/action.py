import os
from PySide import QtGui, QtCore

import utils.mayamenutoshelf as mayamenutoshelf

reload(mayamenutoshelf)


class Action(QtGui.QAction):

    def __init__(self, parent=None):
        QtGui.QAction.__init__(self, parent)
        self._taglist = None
        self._command = None
        self._commandtype = None

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
    def commandtype(self):
        return self._commandtype

    @commandtype.setter
    def commandtype(self, value):
        """
        Set the command type to get the correct execution of the command given
        :param value: the name of the command type
        :type value: str
        
        :return: None 
        """
        self._commandtype = value

    def run_command(self):
        """
        Run the command stored in the instance or copy the command to the 
        active shelf
        
        :return: None
        """

        app = QtGui.QApplication.instance()
        modifiers = app.keyboardModifiers()

        if modifiers & QtCore.Qt.ShiftModifier and modifiers & QtCore.Qt.ControlModifier:
            mayamenutoshelf.toshelf(self._process_for_button(), self._commandtype)
            return

        # run from python file
        if self._commandtype == "file":
            eval(self._process_command())
        # run as mel
        elif self._commandtype == "mel":
            exec(self._process_command())
        # run as python
        elif self._commandtype == "python":
            eval(self._command)

    def _process_command(self):
        """
        Check if the command is a file which needs to be launched and if it 
        has a relative path, if so return the full path by expanding 
        environment variables.

        :return: a clean command
        :rtype: str
        """
        if self._commandtype == "python":
            return self._command

        if self._commandtype == "mel":
            return "import maya; maya.mel.eval('{}')".format(self._command)

        if self._commandtype == "file":
            if os.path.isabs(self._command):
                string = os.path.normpath(self._command)
            else:
                string = os.path.normpath(os.path.expandvars(self._command))

            return 'execfile(r"{}")'.format(string)

    def _process_for_button(self):
        """
        Check if the command is a file which needs to be launched and if it 
        has a relative path, if so return the full path by expanding 
        environment variables.

        :return: a clean command
        :rtype: str
        """
        if self._commandtype == "python":
            return "eval({})".format(self._command)

        if self._commandtype == "mel":
            return self._command

        if self._commandtype == "file":
            if os.path.isabs(self._command):
                string = os.path.normpath(self._command)
            else:
                string = os.path.normpath(os.path.expandvars(self._command))

            return "execfile({})".format(string)