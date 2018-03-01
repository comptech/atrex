
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *
from myPeaks import *

class peakEditDlg (QDialog) :


    def __init__(self, peak, rownum) :
        QDialog.__init__(self)
        self.ui = loadUi("peakEditDlg.ui", self)
        self.peak = peak
        self.textSetD (self.ui.pe_id, rownum)
        self.textSetF (self.ui.pe_detXY_0, peak.DetXY[0])
        self.textSetF (self.ui.pe_detXY_1, peak.DetXY[1])

    def setImageFile (self, imf) :
        self.ui.pe_SourceImageLE.setText (imf)

    def textSetD (self, LE, number) :
        str = "%d"%number
        LE.setText (str)


    def textSetF (self, LE, number) :
        str = "%.2f"%number
        LE.setText (str)
