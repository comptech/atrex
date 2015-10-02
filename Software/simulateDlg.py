

from PyQt4 import QtCore, QtGui, uic
from myDetector import *
import numpy as np



class simulateDlg (QtGui.QDialog) :


    detect = myDetector()

    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("simulateDlg.ui", self)
        self.fillUp()


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