from pyrevit import UI, DB
from pyrevit import script, revit, forms
import SHIP
from time import sleep

def fly_bomb(my_ship, target):
    initial_pt = my_ship.Location.Point
    final_pt = target.Location.Point

    try:
        line = DB.Line.CreateBound(initial_pt, final_pt)
        mid_pt = line.Evaluate(0.5, True)
        mid_pt_new = DB.XYZ(mid_pt.X, mid_pt.Y, mid_pt.Z + line.Length/3.0)
        arc = DB.Arc.Create(initial_pt, final_pt, mid_pt_new)
    except:#line too short, just update data and leave
        return

    bomb = SHIP.get_bomb()
    SHIP.bomb_show(bomb)
    step = 50 if True else 200 # later update this to make bigger bomb fly in more framethus slower?
    for i in range(step + 1):
        pt_para = float(i)/step
        temp_location = arc.Evaluate(pt_para, True)
        with revit.Transaction("frame update"):
            bomb.Location.Point = temp_location

        safety = 0.01#so there is never division by zero
        speed = -pt_para * (pt_para - 1) + safety#faster in middle
        pause_time = 0.25 + safety - speed# 1/4 is the peak value in normalised condition

        revit.uidoc.RefreshActiveView()

    SHIP.bomb_hide(bomb)


    target_ship = SHIP.get_ship_at_target(target)
    if not isinstance(target_ship, str):
        SHIP.update_ship_status(target_ship)
