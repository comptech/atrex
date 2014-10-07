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
        self.ui.rangeSlider.valueChanged.connect (self.newImageValue)
        self.ui.updateImageDispButton.clicked.connect (self.updateImage)
        self.ui.maxDNSlider.valueChanged.connect (self.maxSliderUpdate)
        self.ui.minDNSlider.valueChanged.connect (self.minSliderUpdate)
        self.ui.maxDNSlider.setRange (0, 65535)
        self.ui.minDNSlider.setRange (0, 65535)
        self.ui.maxDNSlider.setSingleStep (100)
        self.ui.minDNSlider.setSingleStep (100)
        self.ui.maxDNSlider.setValue (1000)
        self.ui.rangeSlider.setSingleStep(1) 
        self.workDirectory = ''
        self.imageDirectory = ''
        self.myim = myImage () 

    def openImage (self) :
        wdir = self.ui.imDirLE.text ()
        print len(wdir)
        self.imageFile = QtGui.QFileDialog.getOpenFileName (self, 'Open Tiff Image', wdir)
        # image file prefix will be used to build new images to display
        prefind = self.imageFile.lastIndexOf(".tif")
        self.imageFilePref = self.imageFile.left (prefind-3)
        print 'pref is ',self.imageFilePref
        self.imfileLE.setText (self.imageFile)
        self.displayImage (self.imageFile)
        #self.myim.readTiff (self.imageFile)
        #self.ui.imageWidget.writeQImage (self.myim.imArray)
        mnmx = getImageRange (wdir, self.imageFile)
        self.ui.minRangeLabel.setText (QtCore.QString.number(mnmx[0]))
        self.ui.maxRangeLabel.setText (QtCore.QString.number(mnmx[1]))
        self.ui.selectedImageLE.setText (QtCore.QString.number(mnmx[2]))
        self.ui.rangeSlider.setRange (mnmx[0],mnmx[1])
        self.ui.rangeSlider.setValue (mnmx[2])
        
        
        #self.ui.rangeSlider.set

    """ updateImage method called when Update button is clicked.
        This will read the selectedImageLE text, convert to an int, then
        calculate the new image name. Final step is then to display that image.
    """
    def updateImage (self) :
        # get the image num and convert to float
        z = QtCore.QChar ('0')
        tmpstr = self.ui.selectedImageLE.text()
        imnum = tmpstr.toInt ()
        print 'New image number ',imnum[0]
        newimage = QtCore.QString ("%1%2.tif").arg(self.imageFilePref).arg(imnum[0],3,10,z)
        print newimage
        status = self.displayImage (newimage)
        if (status) :
            self.ui.imfileLE.setText (newimage)
            self.imageFile = newimage
            
    """ newImageValue is called by the range slider callback and updates the selectedImageLE
        image number
    """
    def newImageValue (self, newval) :
       self.ui.selectedImageLE.setText (QtCore.QString.number(newval))

    """ maxSliderUpdate is called by the DN max slider and updates the text line
        edit box. The value in the edit box is used when 
    """
    def maxSliderUpdate (self, newval) :
        self.ui.imageMaxLE.setText (QtCore.QString.number(newval))

    """ minSliderUpdate is called by the DN max slider and updates the text line
        edit box. The value in the edit box is used when 
    """
    def minSliderUpdate (self, newval) :
        self.ui.imageMinLE.setText (QtCore.QString.number(newval))


    def defImageDir (self) :
        self.imageDirectory = QtGui.QFileDialog.getExistingDirectory (self, 'Define Image Directory',
                                                      self.imageDirectory,
                                                      QtGui.QFileDialog.ShowDirsOnly)
        print self.imageDirectory
        self.ui.imDirLE.setText (self.imageDirectory)
        

    def displayImage (self, filename) :
        mn = self.ui.imageMinLE.text().toInt()
        mx = self.ui.imageMaxLE.text().toInt()
        print 'display, min is ', mn[0]
        self.imageWidget.setMinMax (mn[0], mx[0])
        qf = QtCore.QFile(filename)
        if (qf.exists()==False) :
            qf.close()
            return False
        else :
            qf.close()
        self.myim.readTiff (filename)
        #self.ui.imageWidget.writeQImage (self.myim.imArray)
        self.ui.imageWidget.writeQImage_lut (self.myim.imArray)
        return (True)
        
app = QtGui.QApplication (sys.argv)
mainWindow = myMainWindow()
mainWindow.show()

sys.exit (app.exec_())
