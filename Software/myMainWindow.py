from PyQt4 import QtCore, QtGui, uic
from myImage import *
from myImDisplay import *
import sys
import time

class myMainWindow (QtGui.QMainWindow) :

    def __init__(self) :
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi ("uiMainWin.ui", self)
        self.ui.openImageButton.clicked.connect (self.openImage)
        self.ui.workdir = ''
        self.myim = myImage () 

    def openImage (self) :
        wdir = self.ui.imfileLE.text ()
        print len(wdir)
        self.imageFile = QtGui.QFileDialog.getOpenFileName (self, 'Open Tiff Image', self.workdir) 
        self.imfileLE.setText (self.imageFile)
        self.myim.readTiff (self.imageFile)
        self.ui.imageWidget.writeQImage (self.myim.imArray)
        
app = QtGui.QApplication (sys.argv)
mainWindow = myMainWindow()
mainWindow.show()

sys.exit (app.exec_())
