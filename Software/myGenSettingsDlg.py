
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *

class myGenSettingsDlg (QDialog) :

    secondFlag = False
    infile = ""
    status = 0

    def __init__(self) :
        QDialog.__init__(self)
        self.ui = loadUi("genSettingsDlg.ui", self)
        self.ui.writeSettingsButton.clicked.connect (self.closeUp)
        self.ui.cancelButton.clicked.connect (self.cancelThis)


    # initial loading of values in the dialog
    def setInitialVals (self, initAngle, incAngle, startNumber, numImages, chi, detect, exposTime) :
        self.ui.startAngLE.setText (self.makeStr(initAngle))
        self.ui.incAngLE.setText (self.makeStr(incAngle))
        self.ui.startNumLE.setText (self.makeStr(startNumber))
        self.ui.numImagesLE.setText (self.makeStr(numImages))
        self.ui.chiLE.setText (self.makeStr(chi))
        self.ui.detectLE.setText (self.makeStr(detect))
        self.ui.exposTimeLE.setText (self.makeStr(exposTime))


    # quickie utility to return string for input into lineEdit
    def makeStr (self, num):
        str = '%r'%num
        return str

    def getVals (self, array) :
        str = self.ui.startAngLE.text()
        array[0]=str.toFloat()[0]
        str = self.ui.incAngLE.text ()
        array[1] = str.toFloat()[0]
        str = self.ui.startNumLE.text ()
        array[2] = str.toInt()[0]
        str = self.ui.numImagesLE.text ()
        array[3] = str.toInt()[0]
        str = self.ui.chiLE.text ()
        array[4] = str.toFloat()[0]
        str = self.ui.detectLE.text ()
        array[5] = str.toFloat()[0]
        str = self.ui.exposTimeLE.text ()
        array[6] = str.toFloat()[0]

    def setArr (self, array1):
        self.arr = array1

    def cancelThis (self ):
        self.status = -1
        self.close()
        return self.status

    def closeUp (self):
        self.getVals (self.arr)
        self.status = 1
        self.close()
        return self.status