from PyQt4 import QtCore, QtGui
from myPeaks import *
from myDetector import *



class myPeakTableWidget (QtGui.QTableWidget) :

    numPeaks = 0
    headList = QtCore.QString("X;Y;2-theta;d-spacing;h;k;l;rot. angle").split(";")
    myDet = 0


    def __init__(self, parent=None) :
        QtGui.QTableWidget.__init__(self, parent)
        hhead = QtGui.QHeaderView (QtCore.Qt.Horizontal)
        hhead.setVisible(False)
        self.setHorizontalHeader (hhead)
        self.setColumnCount (8)
        self.setRowCount(8)
        #self.setHorizontalHeader (hhead)
        # peak table widget
        #hhead.setVisible(True)
        self.setHorizontalHeaderLabels(self.headList)
        #for i in range(8) :
            #for j in range(8) :
                #newItem = QtGui.QTableWidgetItem("%d %d"%(j,i))
                #self.setItem(i, j, newItem)
        self.setSelectionBehavior (QtGui.QAbstractItemView.SelectRows)


    def setDetector (self, det) :
        self.myDet = det


    def setPeaks (self, peaks) :
        count = 0
        self.setRowCount (len(peaks))
        for p in peaks :
            xy = p.DetXY
            str = '%d'%xy[0]
            self.setItem (count, 0, QtGui.QTableWidgetItem(str))
            str = '%d'%xy[1]
            self.setItem (count, 1, QtGui.QTableWidgetItem(str))
            tthval = self.myDet.calculate_tth_from_pixels(xy, self.myDet.gonio)
            str = '%f'%tthval
            self.setItem (count, 2, QtGui.QTableWidgetItem(str))
            count = count + 1


