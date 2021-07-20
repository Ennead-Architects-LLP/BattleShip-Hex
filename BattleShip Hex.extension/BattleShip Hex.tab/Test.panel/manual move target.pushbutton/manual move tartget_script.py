__doc__ = "XXXXXXXXXX"
__title__ = "manual move target"


from pyrevit import UI, DB
from pyrevit import script, revit, forms
import BOARD, CAMERA, ANIMATION, SHIP
import random

def move(team):
    target = SHIP.get_target_by_team(team)
    SHIP.move_target(target, 4)

for i in range(5):
    team = "A"
    move(team)
    team = "B"
    move(team)
