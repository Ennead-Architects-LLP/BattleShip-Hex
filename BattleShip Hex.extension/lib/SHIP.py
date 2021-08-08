from pyrevit import UI, DB
from pyrevit import script, revit, forms

import BOARD
import GAME_RULE
################### nodes content  ###################


def get_all_nodes():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()
    def filter_by_family_name(x, name):
        if not hasattr(x, 'Symbol'):
            return False
        if x.Symbol.Family.Name != name:
            return False
        return True

    nodes = filter(lambda x: filter_by_family_name(x, "node"), generic_models)
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

def get_node_above_tile(tile):
    nodes = get_all_nodes()
    pt_b = tile.Location.Point
    for node in nodes:
        pt_a = node.Location.Point
        dist = pt_a.DistanceTo(pt_b)
        if GAME_RULE.almost_equal(dist, 0):
            return node
    return "no node above tile"

def mark_node_as_hit(node):
    with revit.Transaction("hit node"):
        node.LookupParameter("Comments").Set("hit")

################### ship content  ###################
def get_enemy(team):
    if team == "A":
        return "B"
    return "A"

def update_ship_status(ship):
    ship_nodes = get_ship_nodes(ship)
    for node in ship_nodes:
        if node.LookupParameter("Comments").AsString() != "hit":
            return "still good"

    with revit.Transaction("ship dead"):
        ship.LookupParameter("_IS_DEAD").Set(1)

        ship.LookupParameter("ship_mat.").Set(GAME_RULE.get_material_by_name("ruin").Id)
    return "dead ship"


def get_all_ships():
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    def filter_by_str_in_family_name(x, string):
        if not hasattr(x, 'Symbol'):
            return False
        if string not in x.Symbol.Family.Name:
            return False
        return True

    ships = filter(lambda x: filter_by_str_in_family_name(x, "ship"), generic_models)

    return ships

def get_all_ships_in_team(team):
    all_ships = get_all_ships()
    team_ships = filter(lambda x: get_ship_team(x) == team, all_ships)
    return team_ships

def get_good_ship_in_team(team):
    ships = get_all_ships_in_team(team)
    for ship in ships:
        if update_ship_status(ship) == "still good":
            return ship
    return "no ship"

def get_ship_team(ship):
    return ship.LookupParameter("_TEAM").AsString()

def get_ship_id(ship):
    return ship.LookupParameter("ship_id").AsString()
"""
def get_ship_position_x(ship):
    return ship.LookupParameter("_POSITION_X").AsString()
def get_ship_position_y(ship):
    return ship.LookupParameter("_POSITION_Y").AsString()
def set_ship_position_xy(ship, x, y):
    with revit.Transaction("set ship position"):
        ship.LookupParameter("_POSITION_X").Set(str(x))
        ship.LookupParameter("_POSITION_Y").Set(str(y))
"""
def get_closest_tile_by_ship(ship):

    all_tiles = BOARD.get_all_tiles()
    pt_a = ship.Location.Point
    for tile in all_tiles:
        pt_b = tile.Location.Point
        dist = pt_a.DistanceTo(pt_b)
        if GAME_RULE.almost_equal(dist, 0):
            return tile
    return "no close tile found"

def move_ship(ship, direction):
    tile = get_closest_tile_by_ship(ship)
    x = BOARD.get_tile_position_x(tile)
    y = int(BOARD.get_tile_position_y(tile))
    team = get_ship_team(ship)
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

    new_position_tile = BOARD.get_tile_by_XY(x,y, team)

    if isinstance(new_position_tile, str) and "not" in new_position_tile:
        return
    with revit.Transaction("move ship"):
        ship.Location.Point = new_position_tile.Location.Point
        #set_ship_position_xy(ship, x, y)
        #print "updated"

def get_ship_nodes(ship):
    all_nodes = get_all_nodes()
    my_nodes = filter(lambda x: get_ship_id(x) == get_ship_id(ship), all_nodes)
    return my_nodes

def get_tiles_below_ship(ship):
    nodes = get_ship_nodes(ship)
    tiles = map(get_closest_tile_by_node, nodes)
    return tiles
def get_tiles_in_ship_zone(ship):
    zone_tiles = []
    ship_tiles = get_tiles_below_ship(ship)
    for tile in ship_tiles:
        neighbor_tiles = BOARD.get_neighbor_tiles(tile)
        zone_tiles.extend(neighbor_tiles)
    zone_tiles = list(set(zone_tiles))
    return zone_tiles


def reset_ship(ship):
    with revit.Transaction("ship reset graphic change"):
        ship.LookupParameter("_IS_DEAD").Set(0)
        team_mat = GAME_RULE.get_material_by_name("TEAM {}".format(get_ship_team(ship)))
        ship.LookupParameter("ship_mat.").Set(team_mat.Id)

        for node in get_ship_nodes(ship):
            node.LookupParameter("Comments").Set("ok")

        #to do: get nodes below and reset is_hit to no

def get_orientation(ship):
    return ship.LookupParameter("orientation_index").AsInteger()

def rotate_orientation(ship):
    with revit.Transaction("rotate_ship"):
        current_orientation = get_orientation(ship)
        new_index = current_orientation + 1 if current_orientation + 1 <=5 else 0
        ship.LookupParameter("orientation_index").Set(new_index)


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
    def filter_by_family_name(x, name):
        if not hasattr(x, 'Symbol'):
            return False
        if x.Symbol.Family.Name != name:
            return False
        return True

    bomb = filter(lambda x: filter_by_family_name(x, "bomb"), generic_models)
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
    def filter_by_family_name(x, name):
        if not hasattr(x, 'Symbol'):
            return False
        if x.Symbol.Family.Name != name:
            return False
        return True

    targets = filter(lambda x: filter_by_family_name(x, "target"), generic_models)
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

def reset_target(target):
    with revit.Transaction("reset target"):
        x, y = "J", "10"
        default_position_tile = BOARD.get_tile_by_XY(x,y, get_enemy(get_target_team(target)))
        target.Location.Point = default_position_tile.Location.Point
        set_target_position_xy(target, x, y)

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
            if BOARD.get_tile_position_x(tile) == get_target_position_x(target)\
             and BOARD.get_tile_position_y(tile) == get_target_position_y(target):
                BOARD.bomb_tile(tile, hit = True)
                node = get_node_above_tile(tile)
                mark_node_as_hit(node)
                update_ship_status(enemy_ship)
                return enemy_ship

    tile_of_target = BOARD.get_tile_by_XY(get_target_position_x(target),\
                                            get_target_position_y(target),\
                                            get_enemy(get_target_team(target)))
    BOARD.bomb_tile(tile_of_target, hit = False)
    return "no hit"
