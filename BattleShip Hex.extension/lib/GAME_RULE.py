from pyrevit import UI, DB
from pyrevit import script, revit, forms
import BOARD, CAMERA, ANIMATION, SHIP
import random

def almost_equal(a,b):
    if abs(a - b) < 0.00001:
        return True
    return False

def is_team_lost(team):
    if SHIP.get_good_ship_in_team(team) == "no ship":
        return True
    #print "{} is still ok".format(team)
    return False

def get_material_by_name(name):
    all_materials = DB.FilteredElementCollector(revit.doc).OfClass(DB.Material).WhereElementIsNotElementType().ToElements()
    return filter(lambda x: x.Name == name, all_materials)[0]

def change_to_player_view_OLD():
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
        ship = SHIP.get_good_ship_in_team(team)
        """#check enegy team after each fire, so green code below is useless
        if isinstance(ship, str):
            forms.alert("Team {} has lost!".format(team))
            CAMERA.go_to_god_view()
            return
        """
        ANIMATION.fly_bomb(ship, target)
        enemy_team = SHIP.get_enemy(team)
        if is_team_lost(enemy_team):

            CAMERA.go_to_game_over_view()
            forms.alert("Team {} has lost!".format(enemy_team))
            CAMERA.go_to_god_view()
            return
        result = SHIP.get_ship_at_target(target)
    if result == "no hit":
        return "turn ended"

    #record deamged ship
    return "continue"

def reset_map():
    map(lambda x: BOARD.reset_tile(x), BOARD.get_all_tiles())
    targets = [SHIP.get_target_by_team(x) for x in ["A", "B"]]
    map(lambda x: SHIP.reset_target(x), targets)
    map(lambda x: SHIP.reset_ship(x), SHIP.get_all_ships())
    revit.get_selection().set_to([])

    # to do: change to this to title screen or a view that akllow player to deploy ship, maybe plan?
