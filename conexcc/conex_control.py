import clr
import sys
import time
import numpy as np



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

class FiberControl():

    def __init__(self, xcom_port, ycom_port):
        self.xact = Actuator(xcom_port)
        self.yact = Actuator(ycom_port)

        self.x_hardlims = [0, 10] #hardware limits in X
        self.y_hardlims = [0, 10] #hardware limits in Y

        self.is_error = False

    def raster(self, xlims, ylims, step_size, mode='serpentine'):
        """
        Raster a rectangular area with width from xlims[0] to xlims[1] and height ylims[0] to ylims[1] in steps of step_size[0] and [1] respectively
        
        Parameters
        -----------
        xlims : length-2 tuple of floats
            start and end points of horizontal raster

        ylims : length-2 tuple of floats
            start and end points of vertical raster

        step_size : float or length-2 tuple of floats
            size of step. If single float, x and y have same step size.

        mode : str
            "serpentine" or "serial", where serpentine continues from the x position at the end of the previous line and goes in the opposite direction. Serial always starts from the same x position, so the actuators must be driven all the way back at the beginning of each row. This is not recommended!!!
        """
        try:
            xstep = float(step_size[0])
            ystep = float(step_size[1])
        except TypeError:
            xstep = float(step_size)
            ystep = float(step_size)
        except:
            print("Error setting step size!")

        if (self._check_raster_settings(xlims, xstep)) and (self._check_raster_settings(ylims, ystep)):
            xrange = np.arange(xlims[0], xlims[1]+xstep, xstep)
            yrange = np.arange(ylims[0], ylims[1]+ystep, ystep)
        else:
            print("Error setting limits!")

        if mode == 'serpentine':
            positions = self._serpentine_raster(xrange, yrange)
        elif mode == 'serial':
            positions = self._serial_raster(xrange, yrange)

        return positions

    def move_to(self, position):
        xpos, ypos = self._format_position(position)
        self.xact.PA_Set(xpos)
        self.yact.PA_Set(ypos)

    def move_by(self, step):
        self.xact.PR_Set(step[0])
        self.yact.PR_Set(step[1])

    def _raster_move(self, positions):
        for position in positions:
            if self.is_error == False:
                self.move_to(position)

    def get_pos(self):
        xpos = self.xact.PA_Get()
        ypos = self.yact.PA_Get()
        return [xpos, ypos]

    def _serial_raster(self, xrange, yrange):
        confirm = input("WARNING: THIS WILL CAUSE THE STAGE TO MOVE HUGE DISTANCES!! TYPE 'yes' TO CONTINUE \n")
        if confirm != 'yes':
            self.is_error = True

        positions = []
        while self.is_error == False:   
            for y_pos in yrange:
                for x_pos in xrange:
                    positions.append([float(x_pos), float(y_pos)])
            break
        return positions

    def _serpentine_raster(self, xrange, yrange):
        positions = []
        while self.is_error == False:
            k = 0    
            for y_pos in yrange:
                if k != 0:
                    for x_pos in xrange:
                        positions.append([float(x_pos), float(y_pos)])
                    k=0
                else:
                    for x_pos in xrange[::-1]:
                        positions.append([float(x_pos), float(y_pos)])
                    k=1
            break
        return positions

    def _check_raster_settings(self, lims, step_size):
        try:
            float(step_size)
            float(lims[0])
            float(lims[1])
            return True
        except:
            print("Error: Make sure limits and step size can be converted to floats")
        
    def _format_position(self, position):
        """
        make sure position is a float and that it lies within the bounds of the actuator's limits
        """
        xpos = float(position[0])
        ypos = float(position[1])
  
        if (ypos <= self.y_hardlims[1]) and (ypos >= self.y_hardlims[0]) and (xpos <= self.x_hardlims[1]) and (xpos >= self.x_hardlims[0]):
            return [xpos, ypos]
        else:
            print("Error: Position beyond limits")



    

if __name__ == "__main__":
    pass