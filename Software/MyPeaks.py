from PyQt4 import QtCore

import math
from PeakObject import *

class MyPeaks (QtCore.QObject) :

    peaks_0 =[]
    peaks_1 =[]
    count =[0,0]

    def __init__(self) :

    def addPeak (self, listnum, x, y ) :
        count[listnum] += 1
        if (listnum ==0) :
            peaks_0.append (PeakObject(x,y))
            print count[listnum], peaks_0[peaks_0.count-1].x(),peaks_0[peaks_0.count-1].y()
    
