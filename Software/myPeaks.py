from PyQt4 import QtCore

import math
from PeakObject import *

class myPeaks (QtCore.QObject) :

    peaks_0 =[]
    peaks_1 =[]
    peakLists = [peaks_0,peaks_1]
    count =[0,0]
    activeList = 0 ;

    def __init__(self) :
        self.count[0]=0
        self.count[1]=0

    def addPeak (self,  x, y ) :
        lnum = self.activeList
        self.count[lnum] += 1
        index = self.count[lnum]-1
        self.peakLists[lnum].append(PeakObject(x,y))
            
        print index, self.peakLists[lnum][index].x(),self.peakLists[lnum][index].y()
    

    def setActiveList (self, ind) :
        self.activeList = ind 
