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
To install download this package and place it in a directory where Maya can find it.

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

To show the menu in Maya:

```python
import scriptsmenu.launchformaya as launchformaya

configuration = "path/to/configuration.json"
launchformaya.main(configuration,
                   title="My Scripts")
```

To show at Maya launch you can paste the above code in your `userSetup.py`

<br>

### Advanced

To ensure the menu can be used in other packages besides Maya it recommended to create a separate launcher file (py)
which checks for the parent to hook the menu to.
The action which is triggered when clicked in the menu will also need to adjusted in order to process the commands
to match the package

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