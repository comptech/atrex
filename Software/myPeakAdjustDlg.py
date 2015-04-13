from PyQt4 import QtCore, QtGui, uic
from myZmPeakDisplay import *

class myPeakAdjustDlg (QtGui.QDialog) :

    zmPeakRaw = None
    rawMnMx = [0.,0.]
    fitMnMx = [0.,0.]
    residsMnMx = [0.,0.]

    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("peakDisplayAdjust.ui", self)
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
            str = QtCore.QString ("%1").arg(self.rawMnMx[0])
            self.ui.minLE.setText (str)
            str = QtCore.QString ("%1").arg(self.rawMnMx[1])
            self.ui.maxLE.setText (str)
        if (self.ui.fittedRB.isChecked()) :
            str = QtCore.QString ("%1").arg(self.fitMnMx[0])
            self.ui.minLE.setText (str)
            str = QtCore.QString ("%1").arg(self.fitMnMx[1])
            self.ui.maxLE.setText (str)
        if (self.ui.residsRB.isChecked()) :
            str = QtCore.QString ("%1").arg(self.residsMnMx[0])
            self.ui.minLE.setText (str)
            str = QtCore.QString ("%1").arg(self.residsMnMx[1])
            self.ui.maxLE.setText (str)


    def update (self):
        min = self.ui.minLE.text().toFloat()[0]
        max = self.ui.maxLE.text().toFloat()[0]
        if (self.ui.rawRB.isChecked()) :
            self.zmPeakRaw.setMinMax (min, max)
        if (self.ui.fittedRB.isChecked()) :
            self.zmPeakFit.setMinMax (min, max)
        if (self.ui.residsRB.isChecked()) :
            self.zmPeakResids.setMinMax (min, max)

