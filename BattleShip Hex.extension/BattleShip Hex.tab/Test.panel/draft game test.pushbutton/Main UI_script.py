__doc__ = "XXXXXXXXXX"
__title__ = "test 01"



from pyrevit import UI, DB
from pyrevit import script, revit, forms
import GAME_RULE
output= script.get_output()
output.close_others()


GAME_RULE.play("A")
GAME_RULE.play("B")
