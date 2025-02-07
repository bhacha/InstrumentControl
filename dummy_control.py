import sys
import time

class Dummy:
    
    def __init__(self,
                 dummy_position = 50.0):

        self.dummy_position = dummy_position

    def TP(self):
        """
        Get current position
        It's probably better to use one of the "Get" methods because this does not seem to update as frequently. 

        Returns
        --------
        position : float
            current stage position
        """
        print(f"Position: {self.dummy_position}")
        return self.dummy_position

    def PA_Get(self):
        """
        Redundant for TP, as far as I can tell.

        Returns
        --------
        target : float
            current stage position
        
        """
        print(f"Position: {self.dummy_position}")
        return self.dummy_position

    def PA_Set(self, position):
        """
        Move the stage to position.

        Parameters
        ----------
        step : float
            position to move to    
        
        """
        print("Moved")
        self.dummy_position = position


    def PR_Get(self):
        """
        Retrieve the current position after relative move

        Returns
        --------
        position : float
            current position after relative move
        
        """
        return self.dummy_pos

    def PR_Set(self, step):
        """
        Move the stage by step.

        Parameters
        ----------
        step : float
            distance to move stage       
        """
        print(f"Moved approx. {step}")
        self.dummy_position += step

    def CloseInstrument(self):
        print("Connection Closed")


if __name__ == "__main__":
    pass