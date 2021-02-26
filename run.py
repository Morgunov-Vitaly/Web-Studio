from App.Controller.ScriptController import ScriptController
from App.Services.LoggerService import Log


# Di
mylog = Log()
script_controller = ScriptController(mylog)