from PyQt5.QtCore import *

import math
from PeakObject import *

class myPeaks (QObject) :

    peaks_0 =[]
    peaks_1 =[]
    peakLists = [peaks_0,peaks_1]
    activeList = 0 ;

    def __init__(self) :
        self.activeList = 0

    def addPeak (self,  x, y ) :
        lnum = self.activeList
        self.peakLists[lnum].append(PeakObject(x,y))


    def setActiveList (self, ind):
        self.activeList = ind 

    """ setSelected will set the select bool variable to state
        if the detXY coords are within rectCoords
        """
    def setSelected (self, rectCoords):
        print rectCoords
        state = True
        curList = self.peakLists[self.activeList]
        for peak in curList:
            point = QPoint (peak.x(), peak.y())
            state = rectCoords.contains (point)
            if state:
                peak.setSelected (state)
        

    def selectAll (self):
        curList=self.peakLists[self.activeList]
        for peak in curList:
            peak.selected = True

    def clearAll (self):
        curList=self.peakLists[self.activeList]
        for peak in curList:
            peak.selected = False

    def deleteSelected (self):
        curList=self.peakLists[self.activeList]
        for peak in curList[:]:
            if peak.selected:
                curList.remove(peak)
        print len(curList)

    def moveSelected (self):
        curList=self.peakLists[self.activeList]
        if (self.activeList == 0):
            otherList = 1
        else :
            otherList = 0

        inactList=self.peakLists[otherList]
        for peak in curList[:]:
            if peak.selected:
                #unselect the peak then move it to the other list
                peak.selected = False
                inactList.append(peak)
                curList.remove (peak)


