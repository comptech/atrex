from PyQt4 import QtCore, QtGui
from myPeaks import *
from myDetector import *
from peakEditDlg import *



class myPeakTableWidget (QtGui.QTableWidget) :

    numPeaks = 0
    headList = QtCore.QString("X;Y;2-theta;d-spacing;h;k;l;rot. angle").split(";")
    myDet = 0
    peaks = 0
    imname =''
    numPeaks = 0


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
        self.cellDoubleClicked.connect (self.peakEdit)

    def setImageFileName (self, imname) :
        self.imfile = imname


    def setDetector (self, det) :
        self.myDet = det


    def setPeaks (self, peaks) :
        self.peaks = peaks
        count = 0
        self.setRowCount (len(peaks))
        for p in peaks :
            xy = p.DetXY
            str = '%.2f'%xy[0]
            self.setItem (count, 0, QtGui.QTableWidgetItem(str))
            str = '%.2f'%xy[1]
            self.setItem (count, 1, QtGui.QTableWidgetItem(str))
            tthval = self.myDet.calculate_tth_from_pixels(xy, self.myDet.gonio)
           # xyz = self.myDet.calculate_xyz_from_pixels (xy, self.myDet.gonio)
            str = '%.3f'%tthval
            self.setItem (count, 2, QtGui.QTableWidgetItem(str))
            count = count + 1
        self.numPeaks = count

    def addPeak (self, peak) :
        xy = peak.DetXY
        str = '%d'%xy[0]
        self.setItem (self.numPeaks, 0, QtGui.QTableWidgetItem(str))
        str = '%d'%xy[1]
        self.setItem (self.numPeaks, 1, QtGui.QTableWidgetItem(str))
        tthval = self.myDet.calculate_tth_from_pixels(xy, self.myDet.gonio)
        str = '%f'%tthval
        self.setItem (self.numPeaks, 2, QtGui.QTableWidgetItem(str))
        self.numPeaks += 1

    """ peakEdit
        method called by dbl clicking of the peakTableWidget item
        will open a dialog to further edit the peak parameters
        """
    def peakEdit (self, row, col):
        #open peakEditDlg
        curpeak = self.peaks[row]
        pedit_dlg = peakEditDlg (curpeak, row)
        pedit_dlg.setImageFile (self.imfile)
        pedit_dlg.exec_()

