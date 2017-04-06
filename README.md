### Configurable scripts menu with search field in Qt
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

To ensure the menu is complete with the correct submenus and actions you will need to set up a configuration 
in a .json file ( example : samples/sample_configuration.json ) The key is the department name, the value is 
a list of dictionaries which are the actions linked to the department.

<br>

##### Relative paths

Please check the samples folder of this package for an example python file which can be run.

To ensure the scripts and icons are relative to an environment variable make sure the paths of the scripts
and icons are led by the $YOUR_ENV_VARIABLE and ensure that environment variable is set to the  path in 
which the scripts and icons are located.

To show menu in Maya:

```python
import os
import scriptsmenu.launchformaya as launchformaya

configuration = os.path.expandvars('path_to_configuration\\configuration.json')
launchformaya.main(configuration, "My Scripts")
```

<br>

#### Advanced

To ensure the menu can be used in other packages besides Maya it recommended to create a separate launcher file (py)
which checks for the parent to hook the menu to.
The action which is triggered when clicked in the menu will also need to adjusted in order to process the commands
to match the package