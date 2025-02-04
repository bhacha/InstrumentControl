import pylablib as pll
pll.par["devices/dlls/andor_sdk2"] = "dependencies"
from pylablib.devices import Andor
cam = Andor.AndorSDK2Camera()