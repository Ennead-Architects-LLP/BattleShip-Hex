from pyrevit import UI, DB
from pyrevit import script, revit, forms
import BOARD

def get_all_tiles(team = None):
    generic_models = DB.FilteredElementCollector(revit.doc).OfCategory(DB.BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().ToElements()

    def filter_by_family_name(x, name):
        if not hasattr(x, 'Symbol'):
            return False
        if x.Symbol.Family.Name != name:
            return False
        return True

    tiles = filter(lambda x: filter_by_family_name(x, "tile"), generic_models)
    if team != None:
        tiles = filter(lambda x: get_tile_team(x) == team, tiles)


    return tiles

def get_tile_team(tile):
    return tile.LookupParameter("_TEAM").AsString()

def get_tile_position_x(tile):
    return tile.LookupParameter("_POSITION_X").AsString()

def get_tile_position_y(tile):
    return tile.LookupParameter("_POSITION_Y").AsString()

def print_tile_position(tile):
    print "{}-{}".format(get_tile_position_x(tile),get_tile_position_y(tile))

def get_tile_by_XY(x,y, team):
    tiles = get_all_tiles(team)
    for tile in tiles:
        if get_tile_position_x(tile) == str(x) and get_tile_position_y(tile) == str(y):
            return tile
    return "x,y not valid"

def set_selection_to_tiles(tiles):
    revit.get_selection().set_to(tiles)


def bomb_tile(tile, hit):
    BOARD.set_selection_to_tiles([tile])
    with revit.Transaction("tile graphic change"):
        if hit:
            tile.LookupParameter("show_skull").Set(1)
        else:
            tile.LookupParameter("show_miss symbol").Set(1)

def reset_tile(tile):
    with revit.Transaction("tile graphic change"):
        #set_selection_to_tiles(tile)
        tile.LookupParameter("show_skull").Set(0)
        tile.LookupParameter("show_miss symbol").Set(0)
