__doc__ = "XXXXXXXXXX"
__title__ = "Edit\nBattle Ground"
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

xamlfile = script.get_bundle_file('Edit Ship_UI.xaml')


class UI_Window(WPFWindow):
    def __init__(self):
        WPFWindow.__init__(self, xamlfile)
        self.team = "A"
        self.team_display.Text = "Team A"
        CAMERA.set_view(self.team, type = "3d")
        output= script.get_output()
        output.close_others()


    def confirm_layout(self, sender, e):
        pass
    def reset_layout(self, sender, e):
        pass


    def play(self, sender, e):
        #forms.alert("Player team {}".format(self.team))

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
