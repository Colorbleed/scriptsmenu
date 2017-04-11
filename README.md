# scriptsmenu

###  Configurable scripts menu with search field in Qt

A simple menu which is generate based on a configuration file.
The user can search for the actions based on keywords.

<br>

#### Features
- Vast implementation possibilities through the use of Qt
- Easily maintain a collection of scripts within a studio
- Update menu without restarting application
- Supports use of relative paths

<br>

#### Installation

To install download this package and place it on your `PYTHONPATH`.

<br>

#### Usage

To build a menu you'll need to set up a configuration `.json` file that houses the menu structure
and links the menu items to specific scripts.

An example can be found in `samples/sample_configuration_a.json`

```python
configuration = "path/to/configuration.json"
script_menu = ScriptsMenu(configuration,
                          title="Scripts",
                          parent=None)
scripts_menu.show()
```

##### Example usage in Autodesk Maya

To parent the scripts menu to an application you'll need a parent Qt widget from the host application.
You can pass this parent as parent to the `ScriptMenu(parent=parent)`.

Additionally if you want to alter the behavior when clicking a menu item with specific modifier buttons held (e.g. Control + Shift) you can register a callback. See the _Register callback_ example under _Advanced_ below.

An example for Autodesk Maya can be found in `launchformaya.py`

To show the menu in Maya:

```python
import scriptsmenu.launchformaya as launchformaya

configuration = "path/to/configuration.json"
launchformaya.main(configuration,
                   title="My Scripts")
```

This will automatically parent it to Maya's main menu bar.

To show the menu at Maya launch you can add code to your `userSetup.py`. This code will need to be executed deferred to ensure it runs when Maya main menu bar already exist. For example:

```python
import maya.utils
import scriptsmenu.launchformaya as launchformaya

def build_menu():
    configuration = "path/to/configuration.json"
    launchformaya.main(configuration,
                       title="My Scripts")

maya.utils.executeDeferred(build_menu)
```

<br>

### Advanced


#### Relative paths

To use relative paths in your scripts and icons you can use environment variables. Ensure the
environment variable is set correctly and use it in the paths, like `$YOUR_ENV_VARIABLE`.

A relative path for example could be set as `$SCRIPTS/relative/path/to/script.py`
An example of this can be found in the samples folder of this package.

#### Register callback

You can override the callback behavior per modifier state. For example when you want special
behavior when a menu item is clicked with _Control + Shift_ held at the same time.

```python
from Qt import QtCore
from scriptsmenu.scriptsmenu import ScriptsMenu

def callback(action):
    """This will print a message prior to running the action"""
    print("Triggered with Control + Shift")
    action.run_command()

# Control + Shift
modifier = QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier

menu = ScriptsMenu()
menu.register_callback(modifier, callback)
```