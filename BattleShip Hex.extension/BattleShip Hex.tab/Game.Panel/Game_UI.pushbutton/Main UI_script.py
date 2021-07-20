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

xamlfile = script.get_bundle_file('Main Game_UI.xaml')



class UI_Window(WPFWindow):
    def __init__(self):
        WPFWindow.__init__(self, xamlfile)

        self.team = "A" if self.is_team_A.IsChecked else "B"
        output= script.get_output()
        output.close_others()

    def play(self, sender, e):
        GAME_RULE.play(self.team)

    def reset_game(self, sender, e):
        pass

    def team_changed(self, sender, e):
        self.team = "A" if self.is_team_A.IsChecked else "B"

    def update_target_display(self):
        pass

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
