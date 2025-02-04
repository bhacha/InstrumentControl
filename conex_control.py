import clr
import sys
import time


sys.path.append(r'C:/Program Files (x86)/Newport/MotionControl/CONEX-CC/Bin')

clr.AddReference("Newport.CONEXCC.CommandInterface")

from CommandInterfaceConexCC import * 


class Actuator:

    def __init__(self, 
                 com_port: str):
        self.com_port = com_port
        self.driver = ConexCC()
        self.OpenInstrument()

    def TP(self):
        """
        Get current position
        It's probably better to use one of the "Get" methods because this does not seem to update as frequently. 

        Returns
        --------
        position : float
            current stage position
        """
        resp, position, err = self.driver.TP(1) 
        if resp == 0:
            print(f"Position: {position}")
            return position
        else:
            print(f"Error getting status of device: {err}")

    def OpenInstrument(self):
        """
        Establish connection to instrument
        """

        resp = self.driver.OpenInstrument(self.com_port)
        if resp == 0:
            print("Connection established")
            pass
        else:
            print(f"Error opening connection with device: {resp}")

    def PA_Get(self):
        """
        Redundant for TP, as far as I can tell.

        Returns
        --------
        target : float
            current stage position
        
        """
        resp, target, err = self.driver.PA_Get(1)
        if resp == 0:
            print(f"Current Position: {target}")
        else:
            print(f"Error returning absolute position: {err}")

    def PA_Set(self, position):
        """
        Move the stage to position.

        Parameters
        ----------
        step : float
            position to move to    
        
        """
        resp, err = self.driver.PA_Set(1, position)
        if resp == 0:
            print("Moved")
            pass
        else:
            print(f"Error moving absolute: {err}")

    def PR_Get(self):
        """
        Retrieve the current position after relative move

        Returns
        --------
        position : float
            current position after relative move
        
        """
        resp, position, err = self.driver.PR_Get(1)
        if resp == 0:
            print(f"Current Position: {position}")
        else:
            print(f"Error returning relative position: {err}")

    def PR_Set(self, step):
        """
        Move the stage by step.

        Parameters
        ----------
        step : float
            distance to move stage       
        """
        resp, err = self.driver.PR_Set(1, step)
        if resp == 0:
            print(f"Moved approx. {step}")
            pass
        else:
            print(f"Error moving relative: {err} ")

    def CloseInstrument(self):
        resp = self.driver.CloseInstrument()
        if resp == 0:
            print("Connection Closed")
            pass
        else:
            print(f"Error closing connection with device: {resp}")


if __name__ == "__main__":
    pass