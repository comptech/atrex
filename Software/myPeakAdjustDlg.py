
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *


from myZmPeakDisplay import *

class myPeakAdjustDlg (QDialog) :

    zmPeakRaw = None
    rawMnMx = [0.,0.]
    fitMnMx = [0.,0.]
    residsMnMx = [0.,0.]

    def __init__(self) :
        QDialog.__init__(self)
        self.ui = loadUi("peakDisplayAdjust.ui", self)
        self.ui.updateAdjustButton.clicked.connect (self.update)
        self.ui.rawRB.toggled.connect (self.changedType)
        self.ui.fittedRB.toggled.connect (self.changedType)
        self.ui.residsRB.toggled.connect (self.changedType)
        self.ui.closeButton.clicked.connect (self.close)


    def setPeakDisplay (self, type, dispWidget):
        if type==0 :
            self.zmPeakRaw = dispWidget
            self.rawMnMx[0] = dispWidget.dispMin
            self.rawMnMx[1] = dispWidget.dispMax

        if type==1 :
            self.zmPeakFit = dispWidget
            self.fitMnMx[0] = dispWidget.dispMin
            self.fitMnMx[1] = dispWidget.dispMax

        if type==2 :
            self.zmPeakResids = dispWidget
            self.residsMnMx[0] = dispWidget.dispMin
            self.residsMnMx[1] = dispWidget.dispMax

    def changedType (self, bval):
        self.updateLEFields ()

    def updateLEFields(self):
        if (self.ui.rawRB.isChecked()) :
            str = '%f'%self.rawMnMx[0]
            self.ui.minLE.setText (str)
            str = '%f' % self.rawMnMx[1]
            self.ui.maxLE.setText (str)
        if (self.ui.fittedRB.isChecked()) :
            str = '%f' % self.fitMnMx[0]
            self.ui.minLE.setText (str)
            str = '%f' % self.fitMnMx[1]
            self.ui.maxLE.setText (str)
        if (self.ui.residsRB.isChecked()) :
            str = '%f' % self.residsMnMx[0]
            self.ui.minLE.setText (str)
            str = '%f' % self.residsMnMx[1]
            self.ui.maxLE.setText (str)


    def update (self):
        min = float(self.ui.minLE.text())
        max = float(self.ui.maxLE.text())
        if (self.ui.rawRB.isChecked()) :
            self.zmPeakRaw.setMinMax (min, max)
        if (self.ui.fittedRB.isChecked()) :
            self.zmPeakFit.setMinMax (min, max)
        if (self.ui.residsRB.isChecked()) :
            self.zmPeakResids.setMinMax (min, max)

