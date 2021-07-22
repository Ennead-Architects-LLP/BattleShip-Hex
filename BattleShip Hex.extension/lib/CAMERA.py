from pyrevit import UI, DB
from pyrevit import script, revit, forms
from time import sleep

def pause_view(seconds = 2):
    sleep(int(seconds))

def set_view(team, type = "3d"):
    """type = 3d, 2d plan, draft view for transition"""

    view_name = "{}_main_{}".format(type, team)
    view = get_view_by_name(view_name)
    revit.uidoc.ActiveView = view
    revit.uidoc.RefreshActiveView()
    #sleep(3)

def return_to_title_screen():
    view = get_view_by_name("Title Screen")
    revit.uidoc.ActiveView = view
    revit.uidoc.RefreshActiveView()

def go_to_god_view():
    view = get_view_by_name("god view")
    revit.uidoc.ActiveView = view
    revit.uidoc.RefreshActiveView()

def close_other_view():
    return
    from Autodesk.Revit.UI import RevitCommandId
    import clr
    clr.AddReference('RevitServices')
    from RevitServices.Persistence import DocumentManager
    uiapp = DocumentManager.Instance.CurrentUIApplication
    print uiapp
    cmd = Autodesk.Revit.UI.RevitCommandId.LookupPostableCommandId(PostableCommand.CloseInactiveViews)
    #cmdId = cmd.Id
    uiapp.PostCommand(cmd)


def get_view_by_name(name):
    views = DB.FilteredElementCollector(revit.doc).OfClass(DB.View).WhereElementIsNotElementType().ToElements()
    for view in views:
        if view.Name == name:
            return view

def zoom_to_player(player):
    #with revit.Transaction("redraw views"):
    revit.uidoc.ShowElements(player)
    revit.uidoc.RefreshActiveView()
