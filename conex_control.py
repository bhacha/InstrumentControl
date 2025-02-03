import clr
import sys
import time


sys.path.append(r'C:/Program Files (x86)/Newport/MotionControl/CONEX-CC/Bin')

clr.AddReference("Newport.CONEXCC.CommandInterface")

from CommandInterfaceConexCC import * 


class Actuator:

    def __init__(self, 
                 com_port: str):
        
        self.driver = ConexCC()
        self.driver.OpenInstrument(com_port)

        print(self.driver.TP(1))

if __name__ == "__main__":

    actuator = Actuator("com3")