import os
import sys
import time
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from functools import partial
from ctypes import (c_int32, c_bool, byref, create_string_buffer, Structure, POINTER, oledll)
from enum import Enum
from ecc100_control import ECC100Control
ecc = ECC100Control()

# current considerations:
#  - the method of rastering in a snake pattern will have the starting x position flip each layer if the number of rows is odd
#  - if the frequency is set higher than 100 Hz, there is potential for the target (range) to be missed and then it will continue forever


x = 2       # defining the axes, throughout the axes are refered to by 'x' not '2'
y = 0
z = 1

xstepsize = 1   # these are just needed variables and get changed in the GUI
ystepsize = 1
zstepsize = 1

class Connection:
    def __init__(self,ecc):
        super().__init__()
        self.ecc = ecc # connect to the ecc100 control

    def setupUI (self,AttocubeControl):

        AttocubeControl.resize(800,300)
        self.centralwidget = QWidget(AttocubeControl)
        self.centralwidget.resize(800,300)
        self.layout = QGridLayout(self.centralwidget)

        self.GUI = GUI()
        self.layout.addWidget(self.GUI)

        # all of the connections between buttons and values to functions
        self.GUI.raster.clicked.connect(partial(self.Raster))
        # self.position(axis=x)     # have been replaced by initialVals which does this already
        # self.position(axis=y)
        # self.position(axis=z)
        self.getStepVoltage(axis=x)
        self.getStepVoltage(axis=y)
        self.getStepVoltage(axis=z)
        self.getStepFreq(axis=x)
        self.getStepFreq(axis=y)
        self.getStepFreq(axis=z)
        self.initialVals(axis=x)
        self.initialVals(axis=y)
        self.initialVals(axis=z)
        self.GUI.xamp.valueChanged.connect(partial(self.setStepVoltage, axis=x))
        self.GUI.xfreq.valueChanged.connect(partial(self.setStepFreq, axis=x))
        self.GUI.yamp.valueChanged.connect(partial(self.setStepVoltage, axis=y))
        self.GUI.yfreq.valueChanged.connect(partial(self.setStepFreq, axis=y))
        self.GUI.zamp.valueChanged.connect(partial(self.setStepVoltage, axis=z))
        self.GUI.zfreq.valueChanged.connect(partial(self.setStepFreq, axis=z))

        self.GUI.xforward.clicked.connect(partial(self.takeSingleStep, axis=x, backwards=True))
        self.GUI.xback.clicked.connect(partial(self.takeSingleStep, axis=x, backwards=False))
        self.GUI.xcontback.pressed.connect(partial(self.stepContF,axis=x))
        self.GUI.xcontforward.pressed.connect(partial(self.stepContB,axis=x))
        self.GUI.xcontforward.released.connect(partial(self.stopmoving,axis=x))
        self.GUI.xcontback.released.connect(partial(self.stopmoving,axis=x))
        self.GUI.xstep.editingFinished.connect(self.GUI.xstepchanged)
        self.GUI.xmovebybutton.clicked.connect(partial(self.moveBy,axis=x))
        self.GUI.xmovetobutton.clicked.connect(partial(self.moveTo,axis=x))
        self.GUI.xscan.clicked.connect(partial(self.Scan,axis=x))

        self.GUI.yforward.clicked.connect(partial(self.takeSingleStep, axis=y, backwards=False))
        self.GUI.yback.clicked.connect(partial(self.takeSingleStep, axis=y, backwards=True))
        self.GUI.ycontback.pressed.connect(partial(self.stepContB,axis=y))
        self.GUI.ycontforward.pressed.connect(partial(self.stepContF,axis=y))
        self.GUI.ycontforward.released.connect(partial(self.stopmoving,axis=y))
        self.GUI.ycontback.released.connect(partial(self.stopmoving,axis=y))
        self.GUI.ystep.editingFinished.connect(self.GUI.ystepchanged)
        self.GUI.ymovebybutton.clicked.connect(partial(self.moveBy,axis=y))
        self.GUI.ymovetobutton.clicked.connect(partial(self.moveTo,axis=y))
        self.GUI.yscan.clicked.connect(partial(self.Scan,axis=y))

        self.GUI.zforward.clicked.connect(partial(self.takeSingleStep, axis=z, backwards=True))
        self.GUI.zback.clicked.connect(partial(self.takeSingleStep, axis=z, backwards=False))
        self.GUI.zcontback.pressed.connect(partial(self.stepContF,axis=z))
        self.GUI.zcontforward.pressed.connect(partial(self.stepContB,axis=z))
        self.GUI.zcontforward.released.connect(partial(self.stopmoving,axis=z))
        self.GUI.zcontback.released.connect(partial(self.stopmoving,axis=z))
        self.GUI.zstep.editingFinished.connect(self.GUI.zstepchanged)
        self.GUI.zmovebybutton.clicked.connect(partial(self.moveBy,axis=z))
        self.GUI.zmovetobutton.clicked.connect(partial(self.moveTo,axis=z))
        self.GUI.zscan.clicked.connect(partial(self.Scan,axis=z))

        
    # the functions used, most call functions in the ecc100_control file
    def position(self,axis):
        try:
            self._pos = self.ecc.get_position(axis)/1000
            if axis == x:
                self.GUI.xposition.setText(str(self._pos))
            elif axis == y:
                self.GUI.yposition.setText(str(self._pos))
            else:
                self.GUI.zposition.setText(str(self._pos))
        except:
            print ('Could not get current position')

    def initialVals(self,axis):     # put the current position into position as well as move to and end
        try:
            self._pos = self.ecc.get_position(axis)/1000
            if axis == x:
                self.GUI.xposition.setText(str(self._pos))
                self.GUI.xmoveto.setValue(self._pos)
                self.GUI.xend.setValue(self._pos)
            elif axis == y:
                self.GUI.yposition.setText(str(self._pos))
                self.GUI.ymoveto.setValue(self._pos)
                self.GUI.yend.setValue(self._pos)
            else:
                self.GUI.zposition.setText(str(self._pos))
                self.GUI.zmoveto.setValue(self._pos)
                self.GUI.zend.setValue(self._pos)
        except:
            print ('Could not load positions')

    def getStepVoltage(self,axis):
        try:
            self._amp = self.ecc.get_amplitude(axis)/1000
            if axis == x:
                self.GUI.xamp.setValue(float(self._amp))
            elif axis == y:
                self.GUI.yamp.setValue(float(self._amp))
            else:
                self.GUI.zamp.setValue(float(self._amp))
        except:
            print('Could not get voltage')
    
    def setStepVoltage(self,val,axis):
        try:
            self.ecc.set_amplitude(axis,val*1000)
        except:
            print('Could not change voltage')

    def getStepFreq(self,axis):
        try:
            self._freq = self.ecc.get_frequency(axis)/1000
            if axis == x:
                self.GUI.xfreq.setValue(float(self._freq))
            elif axis == y:
                self.GUI.yfreq.setValue(float(self._freq))
            else:
                self.GUI.zfreq.setValue(float(self._freq))
        except:
            print('Could not get voltage')

    def setStepFreq(self,val,axis):
        try:
             self.ecc.set_frequency(axis,val*1000)
        except:
             print ('Could not change frequency')

    def takeSingleStep (self,axis,backwards=False):
        try:
            self.ecc.set_single_step(axis,backwards)
            time.sleep(0.2)
            self.position(axis)
        except:
             print ('Could not move stepwise')

    def stepContF (self,axis,enable=True,set=True):     # while the button is pressed it will continuously step
        start = time.time()
        try:
            self.ecc.control_continuous_forward(axis,enable,set)
            # if self.ecc.is_moving_forward(axis):      # this causes some issues and I don't have a solution at the moment
            #     print('test')
            #     self.position(axis)
            #     self.stepContF(axis=0)
            # while self.ecc.is_moving_forward(axis):   # this is also bad
            #     current_time = time.time()
            #     if current_time - start >= 0.5:
            #         self.GUI.repaint()
            #         start = current_time
            self.position(axis)
        except:
             print ('Could not move continiously forward')

    def stepContB (self, axis,enable=True,set=True):
        try:
              self.ecc.control_continuous_backward(axis, enable, set)
              self.position(axis)
        except:
             print ('Could not move continiously backward')

    def stopmoving (self,axis):
         try:
              self.ecc.stop_stepping(axis)
              time.sleep(0)
              self.position(axis)
         except:
              print('didnt stop')

    def moveBy (self,axis,target=None,targetRange=1000):    # move by the value given, if at 30 and given 10 it will go to 40
        try:
            if axis == x:
                target = int(self.GUI.xmoveby.value()*1000)
            elif axis == y:
                target = int(self.GUI.ymoveby.value()*1000)
            else:
                target = int(self.GUI.zmoveby.value()*1000)
            self.move_by(axis,target,targetRange)
            time.sleep(0.2)
            self.position(axis)
        except:
            print('Could not move')

    def moveTo (self,axis,target=None,targetRange=1000):    # move to the value given, if at 30 and given 10 it will go to 10
        try:
            if axis == x:
                target = int(self.GUI.xmoveto.value()*1000)
            elif axis == y:
                target = int(self.GUI.ymoveto.value()*1000)
            else:
                target = int(self.GUI.zmoveto.value()*1000)
            self.move_to(axis,target,targetRange)
            time.sleep(0.2)
            self.position(axis)
        except:
            print('Could not move')

    def move_by(self,axis,target=None,targetRange=1000):
        if target == None:
            raise ValueError("Must enter a value to move to a targeted position")
        self.ecc.move_enabled_feedback(axis)
        initialPosition = self.ecc.get_position(axis)
        targetPosition = self.ecc.get_target(axis)
        self.ecc.set_target(axis,target+initialPosition) # makes the target relative to the current position for easier use
        targetPosition = self.ecc.get_target(axis)
        if self.ecc.wait_until_position(axis):
            return
        if initialPosition < targetPosition:
            self.ecc.control_continuous_forward(axis,enable=True,set=True)
        elif initialPosition > targetPosition:
            self.ecc.control_continuous_backward(axis,enable=True,set=True)
        self.ecc.enable_output(axis)
        while not self.ecc.wait_until_position(axis,targetRange=targetRange):
            pass
        self.ecc.stop_stepping(axis)

    def move_to(self,axis,target=None,targetRange=1000):
        if target == None:
            raise ValueError("Must enter a value to move to a targeted position")
        self.ecc.move_enabled_feedback(axis)
        initialPosition = self.ecc.get_position(axis)
        targetPosition = self.ecc.get_target(axis)
        self.ecc.set_target(axis,target)
        targetPosition = self.ecc.get_target(axis)
        if self.ecc.wait_until_position(axis):
            return
        if initialPosition < targetPosition:
            self.ecc.control_continuous_forward(axis,enable=True,set=True)
        elif initialPosition > targetPosition:
            self.ecc.control_continuous_backward(axis,enable=True,set=True)
        self.ecc.enable_output(axis)
        while not self.ecc.wait_until_position(axis,targetRange=targetRange):
            pass
        self.ecc.stop_stepping(axis)

    def Scan(self,axis):    # move from current position to end in the number of steps given
        if axis == x:
            start = float(self.GUI.xposition.displayText())
            stop = float(self.GUI.xend.value())
            number = int(self.GUI.xnumstep.value())
        elif axis == y:
            start = float(self.GUI.yposition.displayText())
            stop = float(self.GUI.yend.value())
            number = int(self.GUI.ynumstep.value())
        else:
            start = float(self.GUI.zposition.displayText())
            stop = float(self.GUI.zend.value())
            number = int(self.GUI.znumstep.value())
        
        values = np.linspace(start,stop,number)   

        for i in values:
            if axis == x:
                self.GUI.xmoveto.setValue(i)
            elif axis == y:
                self.GUI.ymoveto.setValue(i)
            else:
                self.GUI.zmoveto.setValue(i)
            self.moveTo(axis)
            # self.GUI.repaint()
            # self.GUI.xposition.setText(str(self.ecc.get_position(axis)/1000))
            self.position(axis)
            print(self.ecc.get_position(axis)/1000)
            time.sleep(0.5)

    def Raster(self):   # similar to scan but using more than one axis
        xstart = float(self.GUI.xend.value())       # x is backwards so that the first flip of the array actually gets back to the positions we want to start
        xstop = float(self.GUI.xposition.displayText())
        xnumber = int(self.GUI.xnumstep.value())
        ystart = float(self.GUI.yposition.displayText())
        ystop = float(self.GUI.yend.value())
        ynumber = int(self.GUI.ynumstep.value())
        zstart = float(self.GUI.zposition.displayText())
        zstop = float(self.GUI.zend.value())
        znumber = int(self.GUI.znumstep.value())      
        xvalues = np.linspace(xstart,xstop,xnumber)
        yvalues = np.linspace(ystart,ystop,ynumber)
        zvalues = np.linspace(zstart,zstop,znumber)

        for i in zvalues:
            self.GUI.zmoveto.setValue(i)
            self.moveTo(axis=z)
            for j in yvalues:
                self.GUI.ymoveto.setValue(j)
                self.moveTo(axis=y)
                xvalues = np.flipud(xvalues)        # this is to make it snake rather than reset to the initial x each row
                for k in xvalues:
                    self.GUI.xmoveto.setValue(k)
                    self.moveTo(axis=x)
                    # self.GUI.repaint()      # this is successful at updating the widget to see the positions and move to values
                    # print(self.ecc.get_position(axis=x)/1000,self.ecc.get_position(axis=y)/1000,self.ecc.get_position(axis=z)/1000)
                    print(k, j, i)
                    time.sleep(1)


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ecc = ecc # connect to the ecc100 control

        # all the GUI labels
        xlabel = QLabel('X',alignment=Qt.AlignCenter)
        ylabel = QLabel('Y',alignment=Qt.AlignCenter)
        zlabel = QLabel('Z',alignment=Qt.AlignCenter)
        positionlabel = QLabel('Current Position (um)',alignment=Qt.AlignCenter)
        sizelabel = QLabel('Step Voltage and Freq',alignment=Qt.AlignCenter)
        singlelabel = QLabel('Single Step',alignment=Qt.AlignCenter)
        continuouslabel = QLabel('Continuous',alignment=Qt.AlignCenter)
        movetolabel = QLabel('Move to (um)',alignment=Qt.AlignCenter)
        movebylabel = QLabel('Move by (um)',alignment=Qt.AlignCenter)
        steplabel = QLabel('Step Size (um)',alignment=Qt.AlignCenter)
        endlabel = QLabel('End of Scan',alignment=Qt.AlignCenter)
        numberlabel = QLabel('Number of Steps',alignment=Qt.AlignCenter)
        self.raster = QPushButton('Raster')

        # all of the GUI buttons and boxes
        self.xposition = QLineEdit(readOnly=True,alignment=Qt.AlignCenter)
        self.xamp = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.xamp.setRange(0,45)
        self.xamp.setSuffix('V')
        self.xfreq = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.xfreq.setRange(0,1000)
        self.xfreq.setSingleStep(100)
        self.xfreq.setSuffix('Hz')
        self.xback = QPushButton('\u2190')
        self.xforward = QPushButton('\u2192')
        self.xcontforward = QPushButton('\u2192\u2192')
        self.xcontback = QPushButton('\u2190\u2190')
        self.xstep = QLineEdit(alignment=Qt.AlignCenter)
        self.xstep.setText(str(xstepsize))
        self.xmoveby = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.xmoveby.setDecimals(3)
        self.xmoveby.setRange(-100000,100000)
        self.xmoveby.setSingleStep(xstepsize)
        self.xmovebybutton = QPushButton("GO")
        self.xmoveto = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.xmoveto.setDecimals(3)
        self.xmoveto.setRange(-100000,100000)
        self.xmoveto.setSingleStep(xstepsize)
        self.xmovetobutton = QPushButton("GO")
        self.xend = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.xend.setDecimals(3)
        self.xend.setRange(-100000,100000)
        self.xend.setSingleStep(xstepsize)
        self.xnumstep = QSpinBox(alignment=Qt.AlignCenter)
        self.xnumstep.setRange(0,100)
        self.xscan = QPushButton('Scan')    

        self.yposition = QLineEdit(readOnly=True,alignment=Qt.AlignCenter)
        self.yamp = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.yamp.setRange(0,45)
        self.yamp.setSuffix('V')
        self.yfreq = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.yfreq.setRange(0,1000)
        self.yfreq.setSingleStep(100)
        self.yfreq.setSuffix('Hz')
        self.yback = QPushButton('\u2190')
        self.yforward = QPushButton('\u2192')
        self.ycontforward = QPushButton('\u2192\u2192')
        self.ycontback = QPushButton('\u2190\u2190')
        self.ystep = QLineEdit(alignment=Qt.AlignCenter)
        self.ystep.setText(str(ystepsize))
        self.ymoveby = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.ymoveby.setDecimals(3)
        self.ymoveby.setRange(-100000,100000)
        self.ymoveby.setSingleStep(ystepsize)
        self.ymovebybutton = QPushButton("GO")
        self.ymoveto = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.ymoveto.setDecimals(3)
        self.ymoveto.setRange(-100000,100000)
        self.ymoveto.setSingleStep(ystepsize)
        self.ymovetobutton = QPushButton("GO")
        self.yend = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.yend.setDecimals(3)
        self.yend.setRange(-100000,100000)
        self.yend.setSingleStep(ystepsize)
        self.ynumstep = QSpinBox(alignment=Qt.AlignCenter)
        self.ynumstep.setRange(0,100)
        self.yscan = QPushButton('Scan')

        self.zposition = QLineEdit(readOnly=True,alignment=Qt.AlignCenter)
        self.zamp = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.zamp.setRange(0,45)
        self.zamp.setSuffix('V')
        self.zfreq = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.zfreq.setRange(0,1000)
        self.zfreq.setSingleStep(100)
        self.zfreq.setSuffix('Hz')
        self.zback = QPushButton('\u2190')
        self.zforward = QPushButton('\u2192')
        self.zcontforward = QPushButton('\u2192\u2192')
        self.zcontback = QPushButton('\u2190\u2190')
        self.zstep = QLineEdit(alignment=Qt.AlignCenter)
        self.zstep.setText(str(zstepsize))
        self.zmoveby = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.zmoveby.setDecimals(3)
        self.zmoveby.setRange(-100000,100000)
        self.zmoveby.setSingleStep(zstepsize)
        self.zmovebybutton = QPushButton("GO")
        self.zmoveto = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.zmoveto.setDecimals(3)
        self.zmoveto.setRange(-100000,100000)
        self.zmoveto.setSingleStep(zstepsize)
        self.zmovetobutton = QPushButton("GO")
        self.zend = QDoubleSpinBox(alignment=Qt.AlignCenter)
        self.zend.setDecimals(3)
        self.zend.setRange(-100000,100000)
        self.zend.setSingleStep(zstepsize)
        self.znumstep = QSpinBox(alignment=Qt.AlignCenter)
        self.znumstep.setRange(0,100)
        self.zscan = QPushButton('Scan')
        
        
        layout = QGridLayout()
        layout.addWidget(xlabel,0,1,1,2)
        layout.addWidget(ylabel,0,3,1,2)
        layout.addWidget(zlabel,0,5,1,2)
        layout.addWidget(positionlabel,1,0,1,1)
        layout.addWidget(sizelabel,2,0,1,1)
        layout.addWidget(singlelabel,3,0,1,1)
        layout.addWidget(continuouslabel,4,0,1,1)
        layout.addWidget(steplabel,5,0,1,1)
        layout.addWidget(movebylabel,6,0,1,1)
        layout.addWidget(movetolabel,7,0,1,1)
        layout.addWidget(endlabel,8,0,1,1)
        layout.addWidget(numberlabel,9,0,1,1)
        layout.addWidget(self.raster,0,0,1,1)

        layout.addWidget(self.xposition,1,1,1,2)
        layout.addWidget(self.xamp,2,1,1,1)
        layout.addWidget(self.xfreq,2,2,1,1)
        layout.addWidget(self.xback,3,1,1,1)
        layout.addWidget(self.xforward,3,2,1,1)
        layout.addWidget(self.xcontback,4,1,1,1)
        layout.addWidget(self.xcontforward,4,2,1,1)
        layout.addWidget(self.xstep,5,1,1,2)
        layout.addWidget(self.xmoveby,6,1,1,1)
        layout.addWidget(self.xmovebybutton,6,2,1,1)
        layout.addWidget(self.xmoveto,7,1,1,1)
        layout.addWidget(self.xmovetobutton,7,2,1,1)
        layout.addWidget(self.xend,8,1,1,2)
        layout.addWidget(self.xnumstep,9,1,1,1)
        layout.addWidget(self.xscan,9,2,1,1)

        layout.addWidget(self.yposition,1,3,1,2)
        layout.addWidget(self.yamp,2,3,1,1)
        layout.addWidget(self.yfreq,2,4,1,1)
        layout.addWidget(self.yback,3,3,1,1)
        layout.addWidget(self.yforward,3,4,1,1)
        layout.addWidget(self.ycontback,4,3,1,1)
        layout.addWidget(self.ycontforward,4,4,1,1)
        layout.addWidget(self.ystep,5,3,1,2)
        layout.addWidget(self.ymoveby,6,3,1,1)
        layout.addWidget(self.ymovebybutton,6,4,1,1)
        layout.addWidget(self.ymoveto,7,3,1,1)
        layout.addWidget(self.ymovetobutton,7,4,1,1)
        layout.addWidget(self.yend,8,3,1,2)
        layout.addWidget(self.ynumstep,9,3,1,1)
        layout.addWidget(self.yscan,9,4,1,1)
        
        layout.addWidget(self.zposition,1,5,1,2)
        layout.addWidget(self.zamp,2,5,1,1)
        layout.addWidget(self.zfreq,2,6,1,1)
        layout.addWidget(self.zback,3,5,1,1)
        layout.addWidget(self.zforward,3,6,1,1)
        layout.addWidget(self.zcontback,4,5,1,1)
        layout.addWidget(self.zcontforward,4,6,1,1)
        layout.addWidget(self.zstep,5,5,1,2)
        layout.addWidget(self.zmoveby,6,5,1,1)
        layout.addWidget(self.zmovebybutton,6,6,1,1)
        layout.addWidget(self.zmoveto,7,5,1,1)
        layout.addWidget(self.zmovetobutton,7,6,1,1)
        layout.addWidget(self.zend,8,5,1,2)
        layout.addWidget(self.znumstep,9,5,1,1)
        layout.addWidget(self.zscan,9,6,1,1)
        

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # these are used to set the step size based on input
    def xstepchanged(self):
        xstepsize = float(self.xstep.displayText())
        self.xmoveby.setSingleStep(xstepsize)
        self.xmoveto.setSingleStep(xstepsize)
        self.xend.setSingleStep(xstepsize)
    
    def ystepchanged(self):
        ystepsize = float(self.ystep.displayText())
        self.ymoveby.setSingleStep(ystepsize)
        self.ymoveto.setSingleStep(ystepsize)
        self.yend.setSingleStep(ystepsize)

    def zstepchanged(self):
        zstepsize = float(self.zstep.displayText())
        self.zmoveby.setSingleStep(zstepsize)
        self.zmoveto.setSingleStep(zstepsize)
        self.zend.setSingleStep(zstepsize)


app = QApplication(sys.argv)

AttocubeControl = QMainWindow() # create main window 

try: ecc = ECC100Control()
except: print ('Connect ECC Controller')
try: ecc.connect()
except: print ('Could not connect to controller' )

window = Connection(ecc=ecc)
window.setupUI(AttocubeControl) # runs the main set of definitions
AttocubeControl.show() # show qmainwindow

app.exec_()
