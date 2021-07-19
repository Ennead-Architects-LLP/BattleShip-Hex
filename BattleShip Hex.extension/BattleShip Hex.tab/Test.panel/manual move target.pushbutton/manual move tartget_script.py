__doc__ = "XXXXXXXXXX"
__title__ = "manual move target"


from pyrevit import UI, DB
from pyrevit import script, revit, forms
import BOARD, CAMERA, ANIMATION, SHIP
import random


team = "A"
all_ships = SHIP.get_all_ships_in_team(team)


target = SHIP.get_target_by_team(team)
SHIP.move_target(target, 4)


team = "B"
all_ships = SHIP.get_all_ships_in_team(team)


target = SHIP.get_target_by_team(team)
SHIP.move_target(target, 4)
