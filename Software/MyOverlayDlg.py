from PyQt4 import QtCore, QtGui, uic


class MyOverlayDlg (QtGui.QDialog) :

    secondFlag = False
    infile = ""

    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("uiPlotOverlayDlg.ui", self)
        self.ui.overlayBrowseButton.clicked.connect (self.browseFile)

    def setParams (self, infl, sflag) :
        self.ui.useSecondAxisCB.setChecked (sflag)
        self.ui.overlayFileLE.setText(infl)

    def accept (self) :
        str = self.ui.overlayFileLE.text ()
        self.infile = str.toLatin1().data()
        secondFlag = self.ui.useSecondAxisCB.isChecked()
        QtGui.QDialog.accept(self)

    def browseFile (self) :
        str = QtGui.QFileDialog.getOpenFileName (self, "Overlay XY ASCII File", self.infile, "Text Files (*.txt *.*)")
        self.overlayFileLE.setText (str)
