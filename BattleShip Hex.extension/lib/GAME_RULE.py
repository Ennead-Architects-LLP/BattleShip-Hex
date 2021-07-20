from pyrevit import UI, DB
from pyrevit import script, revit, forms
import BOARD, CAMERA, ANIMATION, SHIP
import random

def almost_equal(a,b):
    if abs(a - b) < 0.00001:
        return True
    return False


def change_to_player_view():
    """active view as player view so two player can be on same machine!!!. use plan for target, use 3d for battle"""
    pass

def play(team):
    """
    tiles = BOARD.get_all_tiles()
    for tile in tiles:
        BOARD.print_tile_position(tile)
    """

    """
    print "*"*10
    temp_tile = BOARD.get_tile_by_XY("D","7")
    BOARD.print_tile_position(temp_tile)
    print "*"*10
    """

    """
    all_ships = SHIP.get_all_ships_in_team(team)

    team_tiles = []
    for ship in all_ships:
        #print SHIP.get_ship_team(ship)
        ship_tiles = SHIP.get_tiles_below_ship(ship)
        team_tiles.extend(ship_tiles)

    BOARD.set_selection_to_tiles(team_tiles)
    """



    with revit.TransactionGroup("Play"):
        target = SHIP.get_target_by_team(team)
        SHIP.move_target(target, random.randint(0,5))
        ANIMATION.fly_bomb(SHIP.get_all_ships_in_team(team)[0], target)
        SHIP.get_ship_at_target(target)
