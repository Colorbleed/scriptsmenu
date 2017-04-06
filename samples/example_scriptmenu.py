# example to intergrate in maya main menubar
import os
import site

# set example evironment variable
os.environ["SCRIPTMENU"] = os.path.dirname(__file__)
config = os.path.expandvars(r"$SCRIPTMENU\\sample_configuration_a.json")

# add scriptmenu python folder
python_folder = os.path.join(os.path.dirname(__file__), '..', 'python')
site.addsitedir(os.path.abspath(python_folder))


def example_maya_intergration():
    import scriptsmenu.launchformaya as launchformaya
    reload(launchformaya)
    launchformaya.main(config, "Example Scripts")


# example of custom intergration
def launchforother():
    import scriptsmenu.scriptsmenu as scriptsmenu
    parent = None
    scriptsmenu.main(config, parent)
