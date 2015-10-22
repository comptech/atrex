

from PyQt4 import QtCore, QtGui, uic
import myDetector
import myPeakTable
import numpy as np
from crystallography import *
from myPredict import *



class simulateDlg (QtGui.QDialog) :

    updatePeaks = QtCore.pyqtSignal ()



    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("simulateDlg.ui", self)
        self.fillUp()
        self.sim_inc_omchiphi.clicked.connect (self.incVal)
        self.sim_dec_omchiphi.clicked.connect (self.decVal)
        self.sim_genBButton.clicked.connect (self.genB)
        self.sim_changeBButton.clicked.connect (self.changeB)
        self.sim_assignHKLButton.clicked.connect (self.assignHKL)
        self.ui.sim_closeButton.clicked.connect (self.closeUp)
        self.ui.sim_resetOCPButton.clicked.connect (self.resetOCP)
        self.myDetect = myDetector.myDetector()
        self.ub = np.zeros ((3,3),dtype=np.float64)
        self.myPredict = myPredict()
        self.myPeaks = myPeakTable.myPeakTable()
        self.bravType = 'P'


    def setDetector (self, mydetect) :
        self.myDetect = mydetect

    def setPeakTable (self, ptable) :
        self.myPeaks = ptable

    def setPredict (self, myPredict) :
        self.myPredict = myPredict

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

    def genB (self):
        lp = self.read_LP()
        self.ub = b_from_lp(lp)
        self.displayMatrix  (0)
        self.generate_laue()

    def changeB (self):
        lp = self.read_LP()
        self.ub = b_from_lp(lp)
        self.displayMatrix  (0)

    def resetOCP (self):
        str = '0.0'
        self.sim_omegaLE.setText(str)
        self.sim_chiLE.setText(str)
        self.sim_phiLE.setText(str)


    def read_LP (self):
        a = self.sim_aLE.text().toFloat()[0]
        b = self.sim_bLE.text().toFloat()[0]
        c = self.sim_cLE.text().toFloat()[0]
        alpha = self.sim_alphaLE.text().toFloat()[0]
        gamma = self.sim_gammaLE.text().toFloat()[0]
        beta = self.sim_betaLE.text().toFloat()[0]
        lp = [a,b,c,alpha,beta,gamma]

        return lp

    def displayMatrix (self, matType) :
        ### display in the matrixDispText Box matrix
        ### 0 - UB

        if (matType ==0) :
            l0 = '%10.5f\t%10.5f\t%10.5f\r\n%10.5f\t%10.5f\t%10.5f\r\n%10.5f\t%10.5f\t%10.5f'%(self.ub[0,0],self.ub[0,1],self.ub[0,2],self.ub[1,0],self.ub[1,1],self.ub[1,2],self.ub[2,0],self.ub[2,1],self.ub[2,2])
            self.sim_matrixDispText.setText(l0)
            return

    def assignHKL (self) :
        lp = self.read_LP()
        numpeaks = self.myPeaks.getpeakno()
        print 'number of peaks in assign hkl is ', numpeaks


    def getBravaisType (self) :
        self.bravType = self.ui.sim_bravTypeCB.currentText().toLatin1().data()


    def generate_laue (self) :
        en0 = self.ui.sim_incidRangeLowLE.text().toFloat()[0]
        en1 = self.ui.sim_incidRangeHighLE.text().toFloat()[0]
        DAC_open = self.ui.sim_DACOpenLE.text().toFloat()[0]
        #updates the bravType member
        self.getBravaisType ()
        self.myDetect.generate_peaks_laue(self.ub, self.myPeaks, self.myPredict, [en0,en1],self.bravType, DAC_open)
        numpeaks = self.myPeaks.getpeakno ()
        print 'Numpeaks is now : ', numpeaks
        self.updatePeaks.emit()


    def closeUp (self) :
        self.close ()
