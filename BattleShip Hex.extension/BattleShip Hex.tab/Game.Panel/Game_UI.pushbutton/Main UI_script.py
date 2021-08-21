__doc__ = "XXXXXXXXXX"
__title__ = "Play!"
# dependencies
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

# find the path of ui.xaml
from pyrevit import UI, DB
from pyrevit import script, revit, forms
from pyrevit.forms import WPFWindow
import SHIP
import GAME_RULE
import CAMERA
import BOARD


class edit_layout_window(WPFWindow):
    def __init__(self):
        xamlfile = script.get_bundle_file('ShipLayout_UI.xaml')
        WPFWindow.__init__(self, xamlfile)
        self.pick_ship_at_yard = self.pick_mode_yard.IsChecked
        self.team = "A"
        CAMERA.go_to_view_by_name("2d_A_layout")
        CAMERA.zoom_to_board(self.team)
        self.pick_index = 0

    def pick_opt_changed(self, sender,e):
        self.pick_ship_at_yard = self.pick_mode_yard.IsChecked

    def confirm_layout(self, sender, e):
        revit.get_selection().set_to([])

        layout_test_result = self.pass_layout_test()
        if layout_test_result != True:
            forms.alert(layout_test_result)
            """get failed ship and hight its zone"""
            return

        if self.team !="B":
            self.team = "B"
            CAMERA.go_to_view_by_name("deploy A ended")
            forms.alert("click ok when you are ready")
            CAMERA.go_to_view_by_name("2d_B_layout")
            CAMERA.zoom_to_board(self.team)
        else:
            self.team = "done_layout"

        if self.team == "done_layout":
            GAME_RULE.reset_map()
            CAMERA.go_to_view_by_name("ready to play")
            forms.alert("team A click ok when ready")
            CAMERA.set_view("A", type = "3d")

            self.Close()
            UI_Window().ShowDialog()

    def show_zone(self, sender, e):
        if len(revit.get_selection()) == 0:
            return
        ship = revit.get_selection()[0]
        zone_tiles = SHIP.get_tiles_in_ship_zone(ship)
        CAMERA.highlight_element(zone_tiles)

    def filter_ship(self, elements, is_single = True):
        if len(revit.get_selection()) == 0:
            return
        def filter_by_str_in_family_name(x, string):
            if not hasattr(x, 'Symbol'):
                return False
            if string not in x.Symbol.Family.Name:
                return False
            return True

        ships = filter(lambda x: filter_by_str_in_family_name(x, "ship"), revit.get_selection())
        if len(ships) == 0:
            return
        return ships[0] if is_single else ships

    def pass_layout_test(self):

        def test_ship(ship):
            #test 1, no ship over edge
            tiles = SHIP.get_tiles_below_ship(ship)
            for tile in tiles:
                if isinstance(tile, str):
                    return "ship cannot be over edge"

            #test2, no ship on land
            tiles = SHIP.get_tiles_below_ship(ship)
            for tile in tiles:
                if BOARD.is_land(tile):
                    return "ship cannot be on land"

            #3 big ship no in shallow water
            nodes = SHIP.get_ship_nodes(ship)
            if len(nodes) >= 3:
                tiles = SHIP.get_tiles_below_ship(ship)
                for tile in tiles:
                    if BOARD.is_shallow_water(tile):
                        return "big ship cannot be on shallow water"

            return True
        for ship in SHIP.get_all_ships_in_team(self.team):
            test_result = test_ship(ship)
            if isinstance(test_result,str):
                return test_result
        return True

    def sel_ship(self, next = True):
        if self.pick_ship_at_yard:
            ships = SHIP.get_all_ships_in_team("Yard")
        else:
            ships = SHIP.get_all_ships_in_team(self.team)
        try:
            ship = ships[self.pick_index]
            self.pick_index += 1 if next else -1
        except:
            self.pick_index = 0 if next else -1
            ship = ships[self.pick_index]
        CAMERA.highlight_element(ship)
        #print self.pick_index


    def sel_next_ship(self, sender, e):
        self.sel_ship(next = True)

    def sel_prev_ship(self, sender, e):
        self.sel_ship(next = False)


    def rotate_ship(self, sender, e):
        if len(revit.get_selection()) == 0:
            return
        ship = self.filter_ship(revit.get_selection())
        #print ship
        if ship:
            SHIP.rotate_orientation(ship)

    def ship_move_by_keyword(self, keyword):
        if len(revit.get_selection()) == 0:
            return
        ship = self.filter_ship(revit.get_selection())
        if ship:
            SHIP.move_ship(ship, keyword)
            self.update_ship_display(ship)

    def move_NW(self, sender, e):
        self.ship_move_by_keyword("NW")

    def move_E(self, sender, e):
        self.ship_move_by_keyword("E")

    def move_NE(self, sender, e):
        self.ship_move_by_keyword("NE")

    def move_SE(self, sender, e):
        self.ship_move_by_keyword("SE")

    def move_SW(self, sender, e):
        self.ship_move_by_keyword("SW")

    def move_W(self, sender, e):
        self.ship_move_by_keyword("W")

    def update_ship_display(self,ship):
        tile = SHIP.get_closest_tile_by_ship(ship)
        x = BOARD.get_tile_position_x(tile)
        y = int(BOARD.get_tile_position_y(tile))
        self.ship_position_display.Text = "{}-{}".format(x, y)





class UI_Window(WPFWindow):
    def __init__(self):
        xamlfile = script.get_bundle_file('Main Game_UI.xaml')
        WPFWindow.__init__(self, xamlfile)
        self.team = "A"
        self.team_display.Text = "Team A"
        GAME_RULE.reset_map()
        #CAMERA.return_to_title_screen()
        CAMERA.close_other_view()
        output= script.get_output()
        output.close_others()

    def edit_map(self, sender, e):
        self.Close()
        UI = edit_layout_window()
        UI.ShowDialog()

    def play(self, sender, e):
        #forms.alert("Player team {}".format(self.team))
        """
        if revit.uidoc.ActiveView.Name == "Title Screen":
            CAMERA.set_view("A", type = "3d")
            forms.alert("Player A get ready!")
        """
        if GAME_RULE.play(self.team) == "turn ended":
            CAMERA.pause_view(1)
            revit.uidoc.ActiveView = CAMERA.get_view_by_name("turn ended_{}".format(SHIP.get_enemy(self.team)))
            revit.uidoc.RefreshActiveView()
            CAMERA.pause_view(1)
            forms.alert("Click 'ok' when you are ready!")
            self.team_changed()


    def reset_game(self, sender, e):
        GAME_RULE.reset_map()
        CAMERA.return_to_title_screen()
        CAMERA.close_other_view()
        self.Close()

    def team_changed(self):
        self.team = "A" if self.team == "B" else "B"
        self.team_display.Text = "Team {}".format(self.team)
        CAMERA.set_view(self.team, type = "3d")
        CAMERA.close_other_view()

    def update_target_display(self):
        team = self.team
        target = SHIP.get_target_by_team(team)
        x = SHIP.get_target_position_x(target)
        y = SHIP.get_target_position_y(target)
        self.target_position_display.Text = "{}-{}".format(x, y)


    def target_move_keyword(self, keyword):
        team = self.team
        target = SHIP.get_target_by_team(team)
        SHIP.move_target(target, keyword)
        self.update_target_display()

    def target_move_NW(self, sender, e):
        self.target_move_keyword("NW")

    def target_move_NE(self, sender, e):
        self.target_move_keyword("NE")

    def target_move_SW(self, sender, e):
        self.target_move_keyword("SW")

    def target_move_SE(self, sender, e):
        self.target_move_keyword("SE")

    def target_move_W(self, sender, e):
        self.target_move_keyword("W")

    def target_move_E(self, sender, e):
        self.target_move_keyword("E")


if __name__ == "__main__":
    #UI_Window().ShowDialog()
    edit_layout_window().ShowDialog()
