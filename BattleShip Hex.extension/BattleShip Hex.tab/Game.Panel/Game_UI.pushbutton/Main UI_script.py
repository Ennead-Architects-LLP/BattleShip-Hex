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

xamlfile = script.get_bundle_file('Main Game_UI.xaml')
class edit_layout_window(WPFWindow):
    def __init__(self):
        xamlfile = script.get_bundle_file('ShipLayout_UI.xaml')
        WPFWindow.__init__(self, xamlfile)
        self.pick_ship_at_yard = self.pick_mode_yard.IsChecked
        self.team = "A"
        CAMERA.go_to_view_by_name("2d_A_layout")
        self.pick_index = 0

    def pick_opt_changed(self, sender,e):
        self.pick_ship_at_yard = self.pick_mode_yard.IsChecked

    def confirm_layout(self, sender, e):
        if self.team !="B":
            self.team = "B"
            CAMERA.go_to_view_by_name("deploy A ended")
            forms.alert("click ok when you are ready")
            CAMERA.go_to_view_by_name("2d_B_layout")
        else:
            self.team = "done_layout"

        if self.team == "done_layout":
            GAME_RULE.reset_map()
            CAMERA.go_to_view_by_name("ready to play")
            forms.alert("team A click ok when ready")
            CAMERA.set_view("A", type = "3d")
            self.Close()
            UI_Window().ShowDialog()

    def clear_layout(self, sender, e):
        pass


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
        ship = revit.get_selection()[0]
        #print ship
        SHIP.rotate_orientation(ship)

    def move_NW(self, sender, e):
        pass
    def move_E(self, sender, e):
        pass
    def move_NE(self, sender, e):
        pass
    def move_SE(self, sender, e):
        pass
    def move_SW(self, sender, e):
        pass
    def move_W(self, sender, e):
        pass



class UI_Window(WPFWindow):
    def __init__(self):
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

UI_Window().ShowDialog()
