

from PyQt4 import QtCore, QtGui, uic
from myDetector import *
import numpy as np



class simulateDlg (QtGui.QDialog) :


    detect = myDetector()

    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("simulateDlg.ui", self)
        self.fillUp()
        self.sim_inc_omchiphi.clicked.connect (self.incVal)
        self.sim_dec_omchiphi.clicked.connect (self.decVal)
        self.ui.sim_closeButton.clicked.connect (self.closeUp)
        self.ui.sim_resetOCPButton.clicked.connect (self.resetOCP)


    def fillUp(self) :
        self.ui.sim_aLE.setText( '3.')
        self.ui.sim_bLE.setText( '3.')
        self.ui.sim_cLE.setText( '3.')
        self.ui.sim_alphaLE.setText('90.')
        self.ui.sim_betaLE.setText('90.')
        self.ui.sim_gammaLE.setText('90.')
        self.ui.sim_DACOpenLE.setText('18')
        self.ui.sim_chiLE.setText('0.')
        self.ui.sim_phiLE.setText('0.')
        self.ui.sim_omegaLE.setText ('0.')
        self.ui.sim_incidRangeLowLE.setText ('5.')
        self.ui.sim_incidRangeHighLE.setText ('25.')
        self.ui.sim_incLE.setText('1.')
        self.ui.sim_scaleIncLE.setText('.002')

    def incVal (self):
        incValue = self.ui.sim_incLE.text().toFloat()[0]
        # check for which radiobutton is selected
        valType = self.radState ()
        if (valType == 0) :
            value = self.ui.sim_omegaLE.text().toFloat()[0] + incValue
            str = "%f"%value
            self.ui.sim_omegaLE.setText(str)
            return
        if (valType == 1) :
            value = self.ui.sim_chiLE.text().toFloat()[0] + incValue
            str = "%f"%value
            self.ui.sim_chiLE.setText(str)
        if (valType == 2) :
            value = self.ui.sim_phiLE.text().toFloat()[0] + incValue
            str = "%f"%value
            self.ui.sim_phiLE.setText(str)


    def decVal (self):
        incValue = self.ui.sim_incLE.text().toFloat()[0]
        # check for which radiobutton is selected
        valType = self.radState ()
        if (valType == 0) :
            value = self.ui.sim_omegaLE.text().toFloat()[0] - incValue
            str = "%f"%value
            self.ui.sim_omegaLE.setText(str)
            return
        if (valType == 1) :
            value = self.ui.sim_chiLE.text().toFloat()[0] - incValue
            str = "%f"%value
            self.ui.sim_chiLE.setText(str)
        if (valType == 2) :
            value = self.ui.sim_phiLE.text().toFloat()[0] - incValue
            str = "%f"%value
            self.ui.sim_phiLE.setText(str)

    def radState(self):
        ### checks to see which radio button is checked
        ### returns 0 for omega
        ### returns 1 for chi
        ### returns 2 for phi
        if self.ui.omRad.isChecked() :
            return (0)
        if self.ui.chiRad.isChecked() :
            return (1)
        return (2)

    def resetOCP (self):
        str = '0.0'
        self.sim_omegaLE.setText(str)
        self.sim_chiLE.setText(str)
        self.sim_phiLE.setText(str)

    def closeUp (self) :
        self.destroy ()
