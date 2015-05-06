from PyQt4 import QtCore, QtGui, uic
from myPeaks import *

class peakEditDlg (QtGui.QDialog) :


    def __init__(self, peak, rownum) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("peakEditDlg.ui", self)
        self.peak = peak
        self.textSetD (self.ui.pe_id, rownum)
        self.textSetF (self.ui.pe_detXY_0, peak.DetXY[0])
        self.textSetF (self.ui.pe_detXY_1, peak.DetXY[1])

    def textSetD (self, LE, number) :
        str = "%d"%number
        LE.setText (str)


    def textSetF (self, LE, number) :
        str = "%.2f"%number
        LE.setText (str)
