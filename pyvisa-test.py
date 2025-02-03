import clr
import sys
import time

sys.path.append(r'C:/Program Files (x86)/Newport/MotionControl/CONEX-CC/Bin')

clr.AddReference("Newport.CONEXCC.CommandInterface")

from CommandInterfaceConexCC import * 

con = ConexCC()
con2 = ConexCC()
xaxis = con.OpenInstrument('com3')
yaxis = con2.OpenInstrument('com4')


print(con.TP(1))
print(con2.TP(1))

time.sleep(1)

con2.PR_Set(1, -.25)
con.PR_Set(1, -.5)

time.sleep(1)

print(con.TP(1))
print(con2.TP(1))