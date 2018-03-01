from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *


class MyOverlayDlg (QDialog) :

    secondFlag = False
    infile = ""

    def __init__(self) :
        QDialog.__init__(self)
        self.ui = loadUi("uiPlotOverlayDlg.ui", self)
        self.ui.overlayBrowseButton.clicked.connect (self.browseFile)


    def setParams (self, infl, sflag) :
        self.ui.useSecondAxisCB.setChecked (sflag)
        self.ui.overlayFileLE.setText(infl)

    def accept (self) :
        str = self.ui.overlayFileLE.text ()
        self.infile = str.toLatin1().data()
        secondFlag = self.ui.useSecondAxisCB.isChecked()
        QDialog.accept(self)

    def browseFile (self) :
        str = QFileDialog.getOpenFileName (self, "Overlay XY ASCII File", self.infile, "Text Files (*.txt *.*)")
        self.overlayFileLE.setText (str)
