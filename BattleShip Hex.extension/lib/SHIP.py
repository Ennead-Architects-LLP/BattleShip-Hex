from pyrevit import UI, DB
from pyrevit import script, revit, forms

import BOARD
import GAME_RULE
################### nodes content  ###################


def get_all_nodes():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    nodes = filter(lambda x: x.Symbol.Family.Name == "node", generic_models)
    return nodes

def get_closest_tile_by_node(node):

    all_tiles = BOARD.get_all_tiles()
    pt_a = node.Location.Point
    for tile in all_tiles:
        pt_b = tile.Location.Point
        dist = pt_a.DistanceTo(pt_b)
        if GAME_RULE.almost_equal(dist, 0):
            return tile
    return "no close tile found"



################### ship content  ###################
def get_enemy(team):
    if team == "A":
        return "B"
    return "A"


def get_all_ships():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    ships = filter(lambda x: "ship" in x.Symbol.Family.Name, generic_models)
    return ships

def get_all_ships_in_team(team):
    all_ships = get_all_ships()
    team_ship = filter(lambda x: get_ship_team(x) == team, all_ships)
    return team_ship

def get_ship_team(ship):
    return ship.LookupParameter("_TEAM").AsString()

def get_ship_id(ship):
    return ship.LookupParameter("ship_id").AsString()

def get_ship_nodes(ship):
    all_nodes = get_all_nodes()
    my_nodes = filter(lambda x: get_ship_id(x) == get_ship_id(ship), all_nodes)
    return my_nodes

def get_tiles_below_ship(ship):
    nodes = get_ship_nodes(ship)
    tiles = map(get_closest_tile_by_node, nodes)
    return tiles

################### bomb content  ###################
def get_bomb_symbol_old():
    generic_model_types = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsElementType().ToElements()
    for x in generic_model_types:
        print x
        print x.GetType()
    print "**"
    symbol = filter(lambda x: isinstance(x, DB.FamilySymbol ) and x.Family.Name == "bomb", generic_model_types)
    print symbol
    return symbol

def get_bomb():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    bomb = filter(lambda x: x.Symbol.Family.Name == "bomb", generic_models)
    return bomb[0]

def bomb_show(bomb):
    with revit.Transaction("bomb"):
        bomb.LookupParameter("show_bomb").Set(True)

def bomb_hide(bomb):
    with revit.Transaction("bomb"):
        bomb.LookupParameter("show_bomb").Set(False)


################### target content  ###################

def get_target_by_team(team):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    targets = filter(lambda x: x.Symbol.Family.Name == "target", generic_models)
    targets = filter(lambda x: get_ship_team(x) == team, targets)
    return targets[0]

def get_target_position_x(target):
    return target.LookupParameter("_POSITION_X").AsString()

def get_target_position_y(target):
    return target.LookupParameter("_POSITION_Y").AsString()

def set_target_position_xy(target, x, y):
    with revit.Transaction("set target position"):
        target.LookupParameter("_POSITION_X").Set(str(x))
        target.LookupParameter("_POSITION_Y").Set(str(y))

def get_target_team(target):
    return target.LookupParameter("_TEAM").AsString()



def move_target(target, direction):
    x = get_target_position_x(target)
    y = int(get_target_position_y(target))
    team = get_target_team(target)
    """direction = E,NE,NW,W,SW,SE.  E = true east, then courter-clockwise"""
    if x == "A" and direction in ["NE","NW"]:
        # cannot have letter smaller than A.
        return
    if direction == "E":
        y += 1
    elif direction == "NE":
        x = chr(ord(x) - 1)
    elif direction == "NW":
        x = chr(ord(x) - 1)
        y -= 1
    elif direction == "W":
        y -= 1
    elif direction == "SW":
        x = chr(ord(x) + 1)
    elif direction == "SE":
        x = chr(ord(x) + 1)
        y += 1

    new_position_tile = BOARD.get_tile_by_XY(x,y, get_enemy(team))

    if isinstance(new_position_tile, str) and "not" in new_position_tile:
        return
    with revit.Transaction("move target"):
        target.Location.Point = new_position_tile.Location.Point
        set_target_position_xy(target, x, y)
        #print "updated"

def get_ship_at_target(target):
    enemy_ships = get_all_ships_in_team(get_enemy(get_target_team(target)))
    for enemy_ship in enemy_ships:
        for tile in get_tiles_below_ship(enemy_ship):
            if BOARD.get_tile_position_x(tile) == get_target_position_x(target) and BOARD.get_tile_position_y(tile) == get_target_position_y(target):
                BOARD.bomb_tile(tile, hit = True)
                return enemy_ship

    tile_of_target = BOARD.get_tile_by_XY(get_target_position_x(target),get_target_position_y(target),get_enemy(get_target_team(target)))
    BOARD.bomb_tile(tile_of_target, hit = False)
    return "no hit"
