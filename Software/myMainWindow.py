from PyQt4 import QtCore, QtGui, uic
from myImage import *
from myImDisplay import *
from atrex_utils import *
import sys
import time

class myMainWindow (QtGui.QMainWindow) :

    def __init__(self) :
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi ("uiMainWin.ui", self)
        self.ui.openImageButton.clicked.connect (self.openImage)
        self.ui.browseImageDirButton.clicked.connect (self.defImageDir)
        self.ui.rangeSlider.setSingleStep(1) 
        self.workDirectory = ''
        self.imageDirectory = ''
        self.myim = myImage () 

    def openImage (self) :
        wdir = self.ui.imDirLE.text ()
        print len(wdir)
        self.imageFile = QtGui.QFileDialog.getOpenFileName (self, 'Open Tiff Image', wdir) 
        self.imfileLE.setText (self.imageFile)
        self.myim.readTiff (self.imageFile)
        self.ui.imageWidget.writeQImage (self.myim.imArray)
        mnmx = getImageRange (wdir, self.imageFile)
        self.ui.rangeMinLE.setText (QtCore.QString.number(mnmx[0]))
        self.ui.rangeMaxLE.setText (QtCore.QString.number(mnmx[1]))
        self.ui.rangeSlider.setRange (mnmx[0],mnmx[1])
        self.ui.rangeSlider.setValue (mnmx[2])
        
        #self.ui.rangeSlider.set
    
        

    def defImageDir (self) :
        self.imageDirectory = QtGui.QFileDialog.getExistingDirectory (self, 'Define Image Directory',
                                                      self.imageDirectory,
                                                      QtGui.QFileDialog.ShowDirsOnly)
        print self.imageDirectory
        self.ui.imDirLE.setText (self.imageDirectory)
        
app = QtGui.QApplication (sys.argv)
mainWindow = myMainWindow()
mainWindow.show()

sys.exit (app.exec_())
