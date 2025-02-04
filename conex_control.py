import clr
import sys
import time


#sys.path.append(r'C:/Program Files (x86)/Newport/MotionControl/CONEX-CC/Bin')

clr.AddReference("Newport.CONEXCC.CommandInterface")

from CommandInterfaceConexCC import * 


class Actuator:

    def __init__(self, 
                 com_port: str):
        self.com_port = com_port
        self.driver = ConexCC()


    def OpenInstrument(self):
        resp = self.driver.OpenInstrument(self.com_port)
        if resp == 0:
            pass
        else:
            print(f"Error opening connection with device: {resp}")

    def PA_Get(self):
        target, resp = self.driver.PA_Get(1)
        if resp == 0:
            print(f"Current Position: {target}")
        else:
            print(f"Error returning absolution position: {resp}")

    def PA_Set(self, position):
        resp = self.driver.PA_Set(1, position)
        if resp == 0:
            pass
        else:
            print(f"Error moving absolute: {resp}")

    def PR_Get(self):
        step, resp = self.driver.PR_Get(1)
        if resp == 0:
            print(f"Current Step Size: {step}")
        else:
            print(f"Error returning relative position: {resp}")

    def PR_Set(self, step):
        resp = self.driver.PA_Set(1, step)
        if resp == 0:
            pass
        else:
            print(f"Error moving relative: {resp} ")


if __name__ == "__main__":

    actuator = Actuator("com3")