# scriptsmenu

###  Searchable scripts menu with search field in Qt

Scriptsmenu will help you to easily organize your scripts into a
customizable menu that users can quickly browse and search.

<br>

#### Features
- Built with [Qt.py](https://github.com/mottosso/Qt.py)
- Searchable menu for your scripts and tools (using _tags_)
- Update your scripts menu without restarting application
- Supports use of [relative paths for scripts](#relative_paths)

<br>

#### Installation

To install download this package and place it on your `PYTHONPATH`.

<br>

#### Usage

To build a simple menu of searchable scripts

```python
from scriptsmenu import ScriptsMenu

menu = ScriptsMenu(title="Scripts",
                   parent=None)
menu.add_script(parent=menu,
                title="Script A",
                command="print('A')",
                tags=["foobar", "nugget"])
menu.add_script(parent=menu,
                title="Script B",
                command="print('B')",
                tags=["gold", "silver", "bronze"])
menu.show()
```

##### Example usage in Autodesk Maya

To parent the scripts menu to an application you'll need a parent Qt widget from the host application.
You can pass this parent as parent to the `ScriptMenu(parent=parent)`.

Additionally if you want to alter the behavior when clicking a menu item with specific modifier buttons held (e.g. Control + Shift) you can register a callback. See the _Register callback_ example under _Advanced_ below.

An example for Autodesk Maya can be found in `launchformaya.py`

To show the menu in Maya:

```python
import scriptsmenu.launchformaya as launchformaya

menu = launchformaya.main(title="My Scripts")

# continue to populate the menu here
```

This will automatically parent it to Maya's main menu bar.

To show the menu at Maya launch you can add code to your `userSetup.py`. This code will need to be executed deferred to ensure it runs when Maya main menu bar already exist. For example:

```python
import maya.utils
import scriptsmenu.launchformaya as launchformaya

def build_menu():
    menu = launchformaya.main(title="My Scripts")

maya.utils.executeDeferred(build_menu)
```

<br>

### Advanced


#### Relative paths<a name="relative_paths"></a>

To use relative paths in your scripts and icons you can use environment variables. Ensure the
environment variable is set correctly and use it in the paths, like `$YOUR_ENV_VARIABLE`.

A relative path for example could be set as `$SCRIPTS/relative/path/to/script.py`
An example of this can be found in the samples folder of this package.

#### Register callback

You can override the callback behavior per modifier state. For example when you want special
behavior when a menu item is clicked with _Control + Shift_ held at the same time.

```python
from Qt import QtCore
from scriptsmenu import ScriptsMenu

def callback(action):
    """This will print a message prior to running the action"""
    print("Triggered with Control + Shift")
    action.run_command()

# Control + Shift
modifier = QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier

menu = ScriptsMenu()
menu.register_callback(modifier, callback)
```

#### Update menu

The ScriptsMenu has a signal called "updated" which can be connected to a function which
rebuilds the menu

```python
# This example is tested in Autodesk Maya
import scriptsmenu.launchformaya as launchformaya

# Here we create our own menu without any scripts
menu = launchformaya.main(title="Custom Menu")

# Set the update button visible, which is hidden by default
menu.set_update_visible(True)

# Add a custom script to the menu
menu.add_script(parent=menu, title="Before", command='print("C")', sourcetype="python")

# Create update function
def update(menu):
    menu.clear_menu()
    menu.add_script(parent=menu, title="After", command='print("C")', sourcetype="python")

# Link the update function to the update signal
menu.updated.connect(update)
```