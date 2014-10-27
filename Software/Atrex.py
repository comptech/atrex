from PyQt4 import QtCore, QtGui, uic
from myImage import *
from myImDisplay import *
from atrex_utils import *
from myPeaks import *
import sys
import os.path
import time
import myPeakTable
import myDetector

class Atrex (QtGui.QMainWindow):
    displayedImage = False
    minRange = 0
    maxRange = 99
    
    def __init__(self) :
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi ("uiMainWin.ui", self)
        self.ui.openImageButton.clicked.connect (self.openImage)
        self.ui.browseImageDirButton.clicked.connect (self.defImageDir)
        self.ui.browseWorkDirButton.clicked.connect (self.defWorkDir)
        self.ui.rangeSlider.valueChanged.connect (self.newSliderValue)
        self.ui.rangeSlider.sliderReleased.connect (self.newImageValue)
        self.ui.incrementImageButton.clicked.connect (self.incrementImageValue)
        self.ui.decrementImageButton.clicked.connect (self.decrementImageValue)

        self.ui.pushButton_Detector_Open_calibration.clicked.connect (self.openDetectorCalibration)
        self.ui.pushButton_Detector_Save_calibration.clicked.connect (self.saveDetectorCalibration)

        self.ui.Peaks_Button_Search.clicked.connect (self.SearchForPeaks)

        self.ui.updateImageDispButton.clicked.connect (self.updateImage)
        self.ui.maxDNSlider.valueChanged.connect (self.maxSliderUpdate)
        self.ui.minDNSlider.valueChanged.connect (self.minSliderUpdate)
        self.ui.zoomFacBox.valueChanged.connect (self.zoomFacUpdate)
        self.ui.imageWidget.centPt.connect (self.newCent)
        self.ui.imageWidget.addPeakSignal.connect (self.newPeak)
        self.ui.imageWidget.selectRectSignal.connect (self.selectRect)
        self.ui.imageWidget.setButtonModeSignal.connect (self.setButtons)
        self.ui.zoomWidget.addPeakSignal.connect (self.newPeak)
        self.ui.zoomWidget.setButtonModeSignal.connect (self.setButtons)
        self.ui.zoomButton.clicked.connect (self.zoomMode)
        self.ui.addPeakButton.clicked.connect (self.addPeakMode)
        self.ui.selectButton.clicked.connect (self.selectMode)
        self.ui.unselectButton.clicked.connect (self.unselectMode)
        self.ui.list1Button.toggled.connect (self.listButtonChanged)

        self.ui.peakListWidget.itemSelectionChanged.connect (self.PeakListBrowse)

        # peak tab buttons
        self.ui.selectAllButton.clicked.connect(self.selAllPeaks)
        self.ui.clearAllButton.clicked.connect (self.clearAllPeaks)
        self.ui.mvSelPeaksButton.clicked.connect(self.moveSelPeaks)
        self.ui.delSelPeaksButton.clicked.connect(self.delSelPeaks)
        self.ui.clearAllButton.clicked.connect(self.RemoveAllPeaks)

        self.ui.Peaks_Button_Open_PT.clicked.connect(self.OpenPeakTable)
        self.ui.Peaks_Button_Save_PT.clicked.connect(self.SavePeakTable)

        self.ui.zoomWidget.zmRectSignal.connect (self.newZmBox)
        self.ui.maxDNSlider.setRange (0, 65535)
        self.ui.minDNSlider.setRange (0, 65535)
        self.ui.maxDNSlider.setSingleStep (100)
        self.ui.minDNSlider.setSingleStep (100)
        self.ui.maxDNSlider.setValue (1000)
        self.ui.rangeSlider.setSingleStep(1) 
        self.workDirectory = QtCore.QString('')
        self.imageDirectory = QtCore.QString('')
        self.imageFile = QtCore.QString ('')
        self.myim = myImage () 
        self.zmCentLoc = [500,500]
        self.activeList = 0
        self.peaks = myPeakTable.myPeakTable() # This is the active PeakTable
        self.peaks0 = myPeakTable.myPeakTable() # This is the PeakTable0
        self.peaks1 = myPeakTable.myPeakTable() # This is the PeakTable1
        self.detector=myDetector.myDetector()
        self.peaks.setActiveList(self.peaks0, self.peaks1, self.activeList)
        self.imageWidget.setPeaks (self.peaks)
        self.zoomWidget.setPeaks (self.peaks)

        self.ui.zoomButton.setStyleSheet ("QPushButton {background-color: green}")
        self.ui.addPeakButton.setStyleSheet ("QPushButton {background-color: yellow}")
        self.ui.selectButton.setStyleSheet ("QPushButton {background-color: yellow}")
        self.ui.unselectButton.setStyleSheet ("QPushButton {background-color: yellow}")

        self.updatePeakNumberLE ()
        self.getHome ()
        self.ui.tabWidget.setCurrentIndex (0)

    def getHome (self) :
        # get the users home directory
        homedir = os.path.expanduser("~")
        self.paramFile = QtCore.QString("%1/atrex_params.txt").arg(homedir) 
        # then check to see if the atrex_params.txt file exists
        status = os.path.isfile (self.paramFile)
        str = QtCore.QString("")
        if (status) :
            qf = QtCore.QFile (self.paramFile)
            qf.open (QtCore.QIODevice.ReadOnly)
            qts = QtCore.QTextStream (qf)
            str = qts.readLine()
            if (str.length()>2) :
                self.ui.imDirLE.setText (str)
            str = qts.readLine()
            if (str.length()>2) :
                self.ui.imfileLE.setText (str)
                self.imageFile = str
                print 'displaying ',str
                self.openImageFile (str)
            str = qts.readLine()
            if (str.length()>2) :
                self.ui.outDirLE.setText (str)
            
        
        

    def closeEvent (self, event) :
        print 'Shutting down....'
        qf = QtCore.QFile (self.paramFile)
        qf.open (QtCore.QIODevice.WriteOnly)
        qts = QtCore.QTextStream (qf)
        if (self.imageDirectory.size()>1) :
            qts << self.imageDirectory << "\r\n" 
        else :
            qts << "\r\n"
        if (self.imageFile.size() > 1) :
            qts << self.imageFile << "\r\n"
        else :
            qts << "\r\n"
        if (self.workDirectory.size() > 1) :
            qts << self.workDirectory << "\r\n"
        else :
            qts << "\r\n"
            
        
        qf.close()
        
        

    """ Method to open the selected image
    """
    def openImage (self) :
        wdir = self.ui.imDirLE.text ()
        self.imageFile = QtGui.QFileDialog.getOpenFileName (self, 'Open Tiff Image', wdir)
        # get the path and put it in imDirLE
        z = QtCore.QDir.separator()
        wdir = self.imageFile.left (self.imageFile.lastIndexOf (z))
        self.ui.imDirLE.setText (wdir)
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
        self.minRange = mnmx[0]
        self.maxRange = mnmx[1]

    """ Method to open the selected image
    """
    def openImageFile (self, filename) :
        self.imageFile = filename
        z = QtCore.QDir.separator()
        wdir = self.imageFile.left (self.imageFile.lastIndexOf (z))
        self.ui.imDirLE.setText (wdir)
        # image file prefix will be used to build new images to display
        
        prefind = self.imageFile.lastIndexOf(".tif")
        self.imageFilePref = self.imageFile.left (prefind-3)
        print 'pref is ',self.imageFilePref
        print 'filename is ',self.imageFile
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
        self.minRange = mnmx[0]
        self.maxRange = mnmx[1]
        
        #self.ui.rangeSlider.set

    def zoomFacUpdate (self, value) :
        self.ui.zoomWidget.setZmFac (value)
        if (self.displayedImage) :
            self.ui.zoomWidget.writeQImage_lut (self.myim.imArray, self.zmCentLoc)
        
    def newCent (self, newloc) :
        print 'newCent'
        self.zmCentLoc[0] = newloc.x()
        self.zmCentLoc[1] = newloc.y()
        self.ui.zoomWidget.writeQImage_lut (self.myim.imArray, self.zmCentLoc)

    """ newZmBox method called when a the zoom window is updated.
        This sends the zoom rect to the imageWidget to update the zoom box outline.
        """
    def newZmBox (self, zmrect) :
        self.ui.imageWidget.setZmRect (zmrect) 

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

        status = self.displayImage (newimage)
        if (status) :
            self.ui.imfileLE.setText (newimage)
            self.imageFile = newimage
            
    def newSliderValue (self, newval) :
        #val = self.ui.rangeSlider.value()
        self.ui.selectedImageLE.setText (QtCore.QString.number(newval))

    def decrementImageValue (self) :
        val = self.ui.rangeSlider.value()
        val = val-1
        if (val >= self.minRange and val <= self.maxRange) :
            self.newSliderValue (val)
            self.ui.rangeSlider.setValue (val)
            self.newImageValue()

    def incrementImageValue (self) :
        val = self.ui.rangeSlider.value()
        val = val+1
        if (val >= self.minRange and val <= self.maxRange) :
            self.newSliderValue (val)
            self.ui.rangeSlider.setValue (val)
            self.newImageValue()
        


    """ newImageValue is called by the range slider callback and updates the selectedImageLE
        image number
    """
    def newImageValue (self) :
        newval = self.ui.rangeSlider.value()
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor (QtCore.Qt.BusyCursor))
        #self.ui.selectedImageLE.setText (QtCore.QString.number(newval))
        z = QtCore.QChar ('0')
        newimage = QtCore.QString ("%1%2.tif").arg(self.imageFilePref).arg(newval,3,10,z)
        print newimage
        status = self.displayImage (newimage)
        if (status) :
            self.ui.imfileLE.setText (newimage)
            self.imageFile = newimage
        QtGui.QApplication.restoreOverrideCursor ()
       

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
        #print self.imageDirectory
        self.ui.imDirLE.setText (self.imageDirectory)

    def defWorkDir (self) :
        self.workDirectory = QtGui.QFileDialog.getExistingDirectory (self, 'Define Work Directory',
                                                      self.workDirectory,
                                                      QtGui.QFileDialog.ShowDirsOnly)
        #print self.imageDirectory
        self.ui.outDirLE.setText (self.workDirectory)
        

    def displayImage (self, filename) :
        self.displayedImage = True
        mn = self.ui.imageMinLE.text().toInt()
        mx = self.ui.imageMaxLE.text().toInt()
        
        self.imageWidget.setMinMax (mn[0], mx[0])
        self.zoomWidget.setMinMax (mn[0], mx[0])
        
        
        qf = QtCore.QFile(filename)
        if (qf.exists()==False) :
            qf.close()
            return False
        else :
            qf.close()
        self.myim.readTiff (filename)
        status = self.myim.readText (filename)
        if status :
            str = QtCore.QString("0: %1  R : %2").arg(self.myim.omega0).arg(self.myim.omegaR)
            self.ui.omega0Lab.setText (str)
            #self.ui.omegaRLab.setText (self.myim.omegaR)
            self.ui.chiLab.setText (self.myim.chi)
            self.ui.expLab.setText (self.myim.exposureT)
            self.ui.detectorLab.setText (self.myim.detector)
        #self.ui.imageWidget.writeQImage (self.myim.imArray)
        self.ui.imageWidget.writeQImage_lut (self.myim.imArray)
        self.ui.zoomWidget.writeQImage_lut (self.myim.imArray, self.zmCentLoc) 
        self.ui.displayFileLabel.setText (filename)
        return (True)

    """ called by either imageWidget or zoomWidget when a user adds a new peak manually
    """
    def newPeak (self, pt) :
        peak=myPeakTable.myPeak()
        peak.setDetxy ([pt.x(), pt.y()])
        self.peaks.addPeak(peak)
        lstr = QtCore.QString(" %1\t%2").arg( pt.x()).arg( pt.y())
        self.ui.peakListWidget.addItem (lstr)
        self.updatePeakNumberLE ()
        self.imageWidget.repaint()
        self.zoomWidget.repaint()


    """ update peak list usually called when one of the peakList radio boxes is called
    """
    def updatePeakList (self) :
        self.ui.peakListWidget.clear ()
        #curList = self.peaks.peakLists[self.peaks.activeList]
        #for i in range (self.peaks.getpeakno()) :
        #    x=self.peaks.getPeaklistDetX()
        #   y=self.peaks.getPeaklistDetY()
        #  lstr = QtCore.QString(" %1\t%2").arg(x[i]).arg(y[i])
        #   self.ui.peakListWidget.addItem (lstr)
        for p in self.peaks.peaks:
            xy = p.DetXY
            lstr = QtCore.QString(" %1\t%2").arg(xy[0]).arg(xy[1])
            self.ui.peakListWidget.addItem (lstr)
    
    def listButtonChanged (self, event) :
        status = self.list1Button.isChecked()
        if (status) :
            self.peaks.setActiveList(self.peaks0, self.peaks1, 0)
        else :
            self.peaks.setActiveList(self.peaks0, self.peaks1, 1)
        self.updatePeakList () ;
        self.ui.imageWidget.repaint()
        self.ui.zoomWidget.repaint()


    """ zoomMode turns the cursor in the image and zoom widgets to zoom select
    """
    def zoomMode (self) :
        self.ui.imageWidget.zoomOn ()
        self.ui.zoomWidget.zoomOn () 
        self.setButtons (0)

    def addPeakMode (self) :
        self.ui.imageWidget.peakAdd()
        self.ui.zoomWidget.peakAdd()
        self.setButtons (1)

    def selectMode (self) :
        self.ui.imageWidget.selectOn ()
        self.ui.setButtons (2)

    def unselectMode (self) :
        self.ui.imageWidget.unselectOn()
        self.ui.setButtons (3)

    def selectRect (self, rect, sFlag) :
        print 'select peaks called'
        if (sFlag) :
            self.peaks.setSelected (rect)
        else :
            self.peaks.setUnselected (rect)
        self.ui.imageWidget.repaint()
        
    def selAllPeaks (self) :
        self.peaks.selectAll ()
        self.ui.imageWidget.repaint()

    def clearAllPeaks (self) :
        self.peaks.unselectAll()
        self.ui.imageWidget.repaint()

    def moveSelPeaks (self):
        self.peaks.moveSelected()
        self.updatePeakNumberLE()
        self.updatePeakList()
        self.ui.imageWidget.repaint()


    def RemoveAllPeaks(self):
        print 'remove all peaks'
        self.peaks.remove_all_peaks()
        self.updatePeakNumberLE()
        self.updatePeakList()
        self.ui.imageWidget.repaint()

    def delSelPeaks (self):
        self.peaks.deleteSelected()
        self.updatePeakNumberLE()
        self.updatePeakList()
        self.ui.imageWidget.repaint()



    """ function to change background button color from gray when mode is inactive to
        yellow when active
    """
    def setButtons (self, buttonNumber) :
        self.ui.zoomButton.setStyleSheet ("QPushButton {background-color: yellow}")
        self.ui.addPeakButton.setStyleSheet ("QPushButton {background-color: yellow}")
        self.ui.selectButton.setStyleSheet ("QPushButton {background-color: yellow}")
        self.ui.unselectButton.setStyleSheet ("QPushButton {background-color: yellow}")
        if (buttonNumber ==0) :
            self.ui.zoomButton.setStyleSheet ("QPushButton {background-color: green}")
        if (buttonNumber ==1) :
            self.ui.addPeakButton.setStyleSheet ("QPushButton {background-color: green}")
        if (buttonNumber ==2) :
            self.ui.selectButton.setStyleSheet ("QPushButton {background-color: green}")
        if (buttonNumber ==3) :
            self.ui.unselectButton.setStyleSheet ("QPushButton {background-color: green}")

        
    """ Update of the line edit to display # of list 1 and list 2 peaks
    """
    def updatePeakNumberLE (self) :
        pn=self.peaks.getpeakno()
        pn1=self.peaks1.getpeakno()
        str = QtCore.QString ("List 1 : %1\tList 2 : %2").arg(pn).arg(pn1)
        self.ui.numPeaksLE.setText(str)

    def openDetectorCalibration (self):
        self.Display_Detector_calibration(self.detector)

    def saveDetectorCalibration (self):
        self.Update_Detector_calibration()

    def Display_Detector_calibration(self, det):
        self.ui.imDirLE_Detector_Distance.setText (str(det.getdist()))
        XY=det.getbeamXY()
        self.ui.imDirLE_Detector_Beam_X.setText (str(XY[0]))
        self.ui.imDirLE_Detector_Beam_Y.setText (str(XY[1]))
        PS=det.getpsizeXY()
        self.ui.imDirLE_Detector_Pixel_size_X.setText (str(PS[0]))
        self.ui.imDirLE_Detector_Pixel_size_Y.setText (str(PS[1]))
        self.ui.imDirLE_Detector_Wavelength.setText (str(det.getwavelength()))
        self.ui.imDirLE_Detector_Rotation.setText (str(det.gettiltch()))
        self.ui.imDirLE_Detector_Tilt.setText (str(det.gettiltom()))
        self.ui.imDirLE_Detector_Twist.setText (str(det.gettwist()))
        self.ui.imDirLE_Detector_2theta.setText (str(det.getttheta()))

    def Update_Detector_calibration(self):
        self.detector.setdist(float(self.ui.imDirLE_Detector_Distance.text()))
        self.detector.setwavelength(float(self.ui.imDirLE_Detector_Wavelength.text ()))
        self.detector.settiltch(float(self.ui.imDirLE_Detector_Rotation.text ()))
        self.detector.settiltom(float(self.ui.imDirLE_Detector_Tilt.text ()))
        self.detector.settwist(float(self.ui.imDirLE_Detector_Twist.text ()))
        self.detector.setttheta(float(self.ui.imDirLE_Detector_2theta.text ()))
        bx=float(self.ui.imDirLE_Detector_Beam_X.text ())
        by=float(self.ui.imDirLE_Detector_Beam_Y.text ())
        px=float(self.ui.imDirLE_Detector_Pixel_size_X.text ())
        py=float(self.ui.imDirLE_Detector_Pixel_size_Y.text ())
        self.detector.setbeamXY([bx,by])
        self.detector.setpsizeXY([px,py])

    def SearchForPeaks(self):
        print 'Search for peaks'

        #thr=self.threshold                       # 100:       raw counts threshold for locating peaks
        #max_peak_size=self.mindist               # 10:        max allowed peak size with pixels above local background + Imin
        #num_of_segments = [self.pbox,self.pbox]  # [50.,50.]: number of segments in X and Y for local labckground estimation
        #perc=self.bbox                           # 1.0:       percent of median for background

        self.myim.search_for_peaks(self.peaks, 100, 10, [50.,50.],1.0)
        self.updatePeakNumberLE ()
        self.imageWidget.repaint()
        self.zoomWidget.repaint()
        self.updatePeakList()
        self.ui.imageWidget.repaint()

        print 'number of peaks received', self.peaks.getpeakno()

    def SavePeakTable(self):
        print 'write PT'
        wdir = self.ui.imDirLE.text ()
        PTFile = QtGui.QFileDialog.getSaveFileName (self, 'Save Peak Table', wdir)
        self.peaks.write_to_file(PTFile )

    def OpenPeakTable(self):
        print 'read PT'
        wdir = self.ui.imDirLE.text ()
        PTFile = QtGui.QFileDialog.getOpenFileName (self, 'Open Peak Table', wdir)
        self.peaks.read_from_file(PTFile )
        self.updatePeakNumberLE ()
        self.updatePeakList()
        self.ui.imageWidget.repaint()

    def PeakListBrowse(self):
        print 'peak list browse', self.ui.peakListWidget.currentRow()
        self.zmCentLoc[0] = 200
        self.zmCentLoc[1] = 300
        self.ui.PeakZoomWidget1.writeQImage_lut1 (self.myim.imArray, self.zmCentLoc)

app = QtGui.QApplication (sys.argv)
atrex = Atrex ()
atrex.show()

sys.exit (app.exec_())
print 'hello here'