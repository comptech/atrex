import myPeakTable
import numpy as np
import os
from PyQt4 import QtGui
import pickle 

class tester:
    print 'hello here'
    a=myPeakTable.myPeakTable()
    b=myPeakTable.myPeakTable()
    a.setpeakno(114)
    a.selectPeaks([1,2,3])
    a.write_to_file("save.p")
    b.read_from_file("save.p")
    print b.getpeakno()
