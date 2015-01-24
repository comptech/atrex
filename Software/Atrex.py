from PyQt4 import QtCore, QtGui, uic
from myImage import *
from tifffile import *
from myImDisplay import *
from atrex_utils import *
from myMask import *
from myPeaks import *
from MyOverlayDlg import *
from JCPDS import *
from scipy import ndimage
import sys
import os.path
import time
import myPeakTable
import myDetector


class Atrex(QtGui.QMainWindow):
    displayedImage = False
    minRange = 0
    maxRange = 99
    mergeSumMode = True
    mymask = myMask()
    olayFile =""
    olaySecFlag = False
    firstDisplay = True

    imsize = (0,0)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi("uiMainWin.ui", self)
        self.ui.refSampleTabWidget.setColumnWidth (1, 250)
        self.ui.refSampleTabWidget.setHorizontalHeaderLabels (QtCore.QStringList()<< "Name" << "Value")
        self.ui.sampleReflectTabWidget.setHorizontalHeaderLabels \
            (QtCore.QStringList()<< "D-Spacing" << "Intensity" << "H"<<"K"<<"L")
        #self.ui.refSampleTabWidget.verticalHeader().setRowHeight (8)
        self.ui.openImageButton.clicked.connect(self.openImage)
        self.ui.browseImageDirButton.clicked.connect(self.defImageDir)
        self.ui.browseWorkDirButton.clicked.connect(self.defWorkDir)
        self.ui.rangeSlider.valueChanged.connect(self.newSliderValue)
        self.ui.rangeSlider.sliderReleased.connect(self.newImageValue)
        self.ui.incrementImageButton.clicked.connect(self.incrementImageValue)
        self.ui.decrementImageButton.clicked.connect(self.decrementImageValue)
        self.ui.mergeButton.clicked.connect(self.mergeImageRange)
        self.ui.lutCB.currentIndexChanged.connect (self.lutChanged)

        self.ui.pushButton_Detector_Open_calibration.clicked.connect(self.openDetectorCalibration)
        self.ui.pushButton_Detector_Save_calibration.clicked.connect(self.saveDetectorCalibration)

        self.ui.Peaks_Button_Search.clicked.connect(self.SearchForPeaks)

        self.ui.updateImageDispButton.clicked.connect(self.updateImage)
        self.ui.maxDNSlider.valueChanged.connect(self.maxSliderUpdate)
        self.ui.minDNSlider.valueChanged.connect(self.minSliderUpdate)
        self.ui.zoomFacBox.valueChanged.connect(self.zoomFacUpdate)
        self.ui.imageWidget.centPt.connect(self.newCent)
        self.ui.imageWidget.addPeakSignal.connect(self.newPeak)
        self.ui.imageWidget.selectRectSignal.connect(self.selectRect)
        self.ui.imageWidget.maskRectSignal.connect(self.maskRect)
        self.ui.imageWidget.setButtonModeSignal.connect(self.setButtons)
        self.ui.zoomWidget.addPeakSignal.connect(self.newPeak)
        self.ui.zoomWidget.setButtonModeSignal.connect(self.setButtons)
        self.ui.zoomButton.clicked.connect(self.zoomMode)
        self.ui.addPeakButton.clicked.connect(self.addPeakMode)
        self.ui.selectButton.clicked.connect(self.selectMode)
        self.ui.unselectButton.clicked.connect(self.unselectMode)
        self.ui.maskButton.clicked.connect(self.maskMode)
        self.ui.unmaskButton.clicked.connect(self.unmaskMode)
        self.ui.list1Button.toggled.connect(self.listButtonChanged)
        self.ui.peakListWidget.itemClicked.connect(self.peakListClicked)

        self.ui.peakListWidget.itemSelectionChanged.connect(self.PeakListBrowse)

        # peak tab buttons
        self.ui.selectAllButton.clicked.connect(self.selAllPeaks)
        self.ui.clearAllButton.clicked.connect(self.clearAllPeaks)
        self.ui.mvSelPeaksButton.clicked.connect(self.moveSelPeaks)
        self.ui.delSelPeaksButton.clicked.connect(self.delSelPeaks)
        self.ui.seriesSrchButton.clicked.connect(self.SearchForPeaksSeries)
        # self.ui.clearAllButton.clicked.connect(self.RemoveAllPeaks)

        self.ui.Peaks_Button_Open_PT.clicked.connect(self.OpenPeakTable)
        self.ui.Peaks_Button_Save_PT.clicked.connect(self.SavePeakTable)

        self.ui.zoomWidget.zmRectSignal.connect(self.newZmBox)
        self.ui.maxDNSlider.setRange(0, 65535)
        self.ui.minDNSlider.setRange(0, 65535)
        self.ui.maxDNSlider.setSingleStep(100)
        self.ui.minDNSlider.setSingleStep(100)
        self.ui.maxDNSlider.setValue(1000)
        self.ui.rangeSlider.setSingleStep(1)
        self.workDirectory = QtCore.QString('')
        self.imageDirectory = QtCore.QString('')
        self.imageFile = QtCore.QString('')
        self.detectFile = QtCore.QString('')
        self.myim = myImage()
        self.zmCentLoc = [500, 500]
        self.activeList = 0
        self.peaks = myPeakTable.myPeakTable()  # This is the active PeakTable
        self.peaks0 = myPeakTable.myPeakTable()  # This is the PeakTable0
        self.peaks1 = myPeakTable.myPeakTable()  # This is the PeakTable1
        self.detector = myDetector.myDetector()
        self.peaks.setActiveList(self.peaks0, self.peaks1, self.activeList)
        self.imageWidget.setPeaks(self.peaks)
        self.zoomWidget.setPeaks(self.peaks)

        self.ui.zoomButton.setStyleSheet("QPushButton {background-color: green}")
        self.ui.addPeakButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.selectButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.unselectButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.maskButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.unmaskButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.refsampLabel.setStyleSheet ("QLabel{background-color:white}")

        # mask tab buttons
        self.ui.clearMaskButton.clicked.connect(self.clearMask)
        self.ui.saveMaskFileButton.clicked.connect(self.saveMask)
        self.ui.readMaskFileButton.clicked.connect(self.readMask)

        #detector tab buttons
        self.ui.readTextDetFileButton.clicked.connect(self.readTextDetect)
        self.ui.writeTextDetFileButton.clicked.connect(self.writeTextDetect)
        self.ui.testCalcButton.clicked.connect (self.testCalc)

        #integrate tab buttons
        self.ui.integrateCurrentButton.clicked.connect(self.intCurrent)
        self.ui.calc2ThetaButton.clicked.connect (self.calc2theta)
        self.detector.tDoneAll.connect (self.done2theta)
        self.ui.integrateCurrentButton.setEnabled (False)

        self.updatePeakNumberLE()
        self.getHome()
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.zoomTabWidgets.setCurrentIndex(0)

        #plot tab buttons and signal/slots
        self.ui.plot_inputXYButton.clicked.connect(self.plotXYFromFile)
        self.ui.plot_saveFileButton.clicked.connect(self.savePlotToFile)
        self.ui.plot_updateButton.clicked.connect(self.updatePlot)
        self.ui.plot_overlayXY.clicked.connect (self.overlayPlotFromFile)

        #Powder tab
        self.ui.JCPDSReadButton.clicked.connect (self.readJCPDS)
        self.ui.XPOWReadButton.clicked.connect (self.readXPOW)

    def getHome(self):
        # get the users home directory
        homedir = os.path.expanduser("~")
        self.paramFile = QtCore.QString("%1/atrex_params.txt").arg(homedir)
        # then check to see if the atrex_params.txt file exists
        status = os.path.isfile(self.paramFile)
        str = QtCore.QString("")
        if (status):
            qf = QtCore.QFile(self.paramFile)
            qf.open(QtCore.QIODevice.ReadOnly)
            qts = QtCore.QTextStream(qf)
            str = qts.readLine()
            if (str.length() > 2):
                self.ui.imDirLE.setText(str)
            str = qts.readLine()
            if (str.length() > 2):
                self.ui.imfileLE.setText(str)
                self.imageFile = str
                print 'displaying ', str
                self.openImageFile(str)
            str = qts.readLine()
            if (str.length() > 2):
                self.ui.outDirLE.setText(str)
            str = qts.readLine()
            if (str.length() > 2):
                self.detectFile = str
                self.detector.read_from_text_file(str.toLatin1().data())
                self.Display_Detector_calibration(self.detector)


    def closeEvent(self, event):
        print 'Shutting down....'
        qf = QtCore.QFile(self.paramFile)
        qf.open(QtCore.QIODevice.WriteOnly)
        qts = QtCore.QTextStream(qf)
        if (self.imageDirectory.size() > 1):
            qts << self.imageDirectory << "\r\n"
        else:
            qts << "\r\n"
        if (self.imageFile.size() > 1):
            qts << self.imageFile << "\r\n"
        else:
            qts << "\r\n"
        if (self.workDirectory.size() > 1):
            qts << self.workDirectory << "\r\n"
        else:
            qts << "\r\n"
        if (self.detectFile.size()>1) :
            qts << self.detectFile << "\r\n"
        else:
            qts << "\r\n"
        qf.close()


    """ Method to open the selected image
    """

    def openImage(self):
        wdir = self.ui.imDirLE.text()
        self.imageFile = QtGui.QFileDialog.getOpenFileName(self, 'Open Tiff Image', wdir)
        # get the path and put it in imDirLE
        # z = QtCore.QDir.separator()
        fi = QtCore.QFileInfo (self.imageFile)
        basename = fi.baseName()
        wdir = self.imageFile.left(self.imageFile.lastIndexOf(basename))
        self.ui.imDirLE.setText(wdir)
        # image file prefix will be used to build new images to display
        prefind = self.imageFile.lastIndexOf(".tif")
        self.imageFilePref = self.imageFile.left(prefind - 3)
        print 'pref is ', self.imageFilePref
        self.imfileLE.setText(self.imageFile)
        self.displayImage(self.imageFile)
        # self.myim.readTiff (self.imageFile)
        #self.ui.imageWidget.writeQImage (self.myim.imArray)
        mnmx = getImageRange(wdir, self.imageFile)
        self.ui.minRangeLabel.setText(QtCore.QString.number(mnmx[0]))
        self.ui.maxRangeLabel.setText(QtCore.QString.number(mnmx[1]))
        self.ui.selectedImageLE.setText(QtCore.QString.number(mnmx[2]))
        self.ui.rangeSlider.setRange(mnmx[0], mnmx[1])
        self.ui.rangeSlider.setValue(mnmx[2])
        self.minRange = mnmx[0]
        self.maxRange = mnmx[1]
        self.firstDisplay = True

    """ Method to open the selected image
    """

    def openImageFile(self, filename):
        self.imageFile = filename
        fi = QtCore.QFileInfo (self.imageFile)
        basename = fi.baseName()
        wdir = self.imageFile.left(self.imageFile.lastIndexOf(basename))
        self.ui.imDirLE.setText(wdir)
        # z = QtCore.QDir.separator()
        # wdir = self.imageFile.left(self.imageFile.lastIndexOf(z))
        # self.ui.imDirLE.setText(wdir)
        # image file prefix will be used to build new images to display

        prefind = self.imageFile.lastIndexOf(".tif")
        self.imageFilePref = self.imageFile.left(prefind - 3)
        print 'pref is ', self.imageFilePref
        print 'filename is ', self.imageFile
        self.imfileLE.setText(self.imageFile)
        self.displayImage(self.imageFile)
        # self.myim.readTiff (self.imageFile)
        #self.ui.imageWidget.writeQImage (self.myim.imArray)
        mnmx = getImageRange(wdir, self.imageFile)
        self.ui.minRangeLabel.setText(QtCore.QString.number(mnmx[0]))
        self.ui.maxRangeLabel.setText(QtCore.QString.number(mnmx[1]))
        self.ui.selectedImageLE.setText(QtCore.QString.number(mnmx[2]))
        self.ui.rangeSlider.setRange(mnmx[0], mnmx[1])
        self.ui.rangeSlider.setValue(mnmx[2])
        self.minRange = mnmx[0]
        self.maxRange = mnmx[1]



        #self.ui.rangeSlider.set

    def zoomFacUpdate(self, value):
        self.ui.zoomWidget.setZmFac(value)
        if (self.displayedImage):
            self.ui.zoomWidget.writeQImage_lut(self.myim.imArray, self.zmCentLoc)

    def newCent(self, newloc):
        print 'newCent'
        self.zmCentLoc[0] = newloc.x()
        self.zmCentLoc[1] = newloc.y()
        self.ui.zoomWidget.writeQImage_lut(self.myim.imArray, self.zmCentLoc)

    """ newZmBox method called when a the zoom window is updated.
        This sends the zoom rect to the imageWidget to update the zoom box outline.
        """

    def newZmBox(self, zmrect):
        self.ui.imageWidget.setZmRect(zmrect)

    """ updateImage method called when Update button is clicked.
        This will read the selectedImageLE text, convert to an int, then
        calculate the new image name. Final step is then to display that image.
    """

    def updateImage(self):
        # get the image num and convert to float
        z = QtCore.QChar('0')
        tmpstr = self.ui.selectedImageLE.text()
        imnum = tmpstr.toInt()
        print 'New image number ', imnum[0]
        newimage = QtCore.QString("%1%2.tif").arg(self.imageFilePref).arg(imnum[0], 3, 10, z)

        status = self.displayImage(newimage)
        if (status):
            self.ui.imfileLE.setText(newimage)
            self.imageFile = newimage

    def newSliderValue(self, newval):
        # val = self.ui.rangeSlider.value()
        self.ui.selectedImageLE.setText(QtCore.QString.number(newval))

    def decrementImageValue(self):
        val = self.ui.rangeSlider.value()
        val = val - 1
        if (val >= self.minRange and val <= self.maxRange):
            self.newSliderValue(val)
            self.ui.rangeSlider.setValue(val)
            self.newImageValue()

    def incrementImageValue(self):
        val = self.ui.rangeSlider.value()
        val = val + 1
        if (val >= self.minRange and val <= self.maxRange):
            self.newSliderValue(val)
            self.ui.rangeSlider.setValue(val)
            self.newImageValue()


    """ newImageValue is called by the range slider callback and updates the selectedImageLE
        image number
    """

    def newImageValue(self):
        newval = self.ui.rangeSlider.value()
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        # self.ui.selectedImageLE.setText (QtCore.QString.number(newval))
        z = QtCore.QChar('0')
        newimage = QtCore.QString("%1%2.tif").arg(self.imageFilePref).arg(newval, 3, 10, z)
        print newimage
        status = self.displayImage(newimage)
        if (status):
            self.ui.imfileLE.setText(newimage)
            self.imageFile = newimage
        QtGui.QApplication.restoreOverrideCursor()


    """ maxSliderUpdate is called by the DN max slider and updates the text line
        edit box. The value in the edit box is used when 
    """

    def maxSliderUpdate(self, newval):
        self.ui.imageMaxLE.setText(QtCore.QString.number(newval))

    """ minSliderUpdate is called by the DN max slider and updates the text line
        edit box. The value in the edit box is used when 
    """

    def minSliderUpdate(self, newval):
        self.ui.imageMinLE.setText(QtCore.QString.number(newval))

    def lutChanged (self, index) :
        self.imageWidget.setLUT (index)
        self.zoomWidget.setLUT (self.imageWidget.rgb_lut)


    def defImageDir(self):
        self.imageDirectory = QtGui.QFileDialog.getExistingDirectory(self, 'Define Image Directory',
                                                                     self.imageDirectory,
                                                                     QtGui.QFileDialog.ShowDirsOnly)
        # print self.imageDirectory
        self.ui.imDirLE.setText(self.imageDirectory)

    def defWorkDir(self):
        self.workDirectory = QtGui.QFileDialog.getExistingDirectory(self, 'Define Work Directory',
                                                                    self.workDirectory,
                                                                    QtGui.QFileDialog.ShowDirsOnly)
        # print self.imageDirectory
        self.ui.outDirLE.setText(self.workDirectory)


    def displayImage(self, filename):

        mn = self.ui.imageMinLE.text().toInt()
        mx = self.ui.imageMaxLE.text().toInt()

        self.imageWidget.setMinMax(mn[0], mx[0])
        self.zoomWidget.setMinMax(mn[0], mx[0])

        qf = QtCore.QFile(filename)
        if (qf.exists() == False):
            qf.close()
            return False
        else:
            qf.close()
        self.myim.readTiff(filename)
        status = self.myim.readText(filename)
        self.imsize = self.myim.imArraySize

        if self.firstDisplay :
            self.firstDisplay = False
            self.imageWidget.calcHisto (self.myim.imArray)
            mn = self.imageWidget.dispMin
            mx = self.imageWidget.dispMax
            self.zoomWidget.setMinMax (mn, mx)
            self.ui.minDNSlider.setValue (mn)
            self.ui.maxDNSlider.setValue (mx)


        if not self.displayedImage:
            self.mymask.createMask(self.myim.imArraySize[0], self.myim.imArraySize[1])
            self.displayedImage = True
        if status:
            str = QtCore.QString("0: %1  R : %2").arg(self.myim.omega0).arg(self.myim.omegaR)
            self.ui.omega0Lab.setText(str)
            # self.ui.omegaRLab.setText (self.myim.omegaR)
            self.ui.chiLab.setText(self.myim.chi)
            self.ui.expLab.setText(self.myim.exposureT)
            self.ui.detectorLab.setText(self.myim.detector)
        # self.ui.imageWidget.writeQImage (self.myim.imArray)

        self.ui.imageWidget.writeQImage_lut(self.myim.imArray)
        #
        self.ui.zoomWidget.writeQImage_lut(self.myim.imArray, self.zmCentLoc)
        self.ui.displayFileLabel.setText(filename)
        return (True)

    """ called by either imageWidget or zoomWidget when a user adds a new peak manually
    """

    def newPeak(self, pt):
        peak = myPeakTable.myPeak()
        peak.setDetxy([pt.x(), pt.y()])
        self.peaks.addPeak(peak)
        lstr = QtCore.QString(" %1\t%2").arg(pt.x()).arg(pt.y())
        self.ui.peakListWidget.addItem(lstr)
        self.updatePeakNumberLE()
        self.imageWidget.repaint()
        self.zoomWidget.repaint()


    """ update peak list usually called when one of the peakList radio boxes is called
    """

    def updatePeakList(self):
        self.ui.peakListWidget.clear()
        # curList = self.peaks.peakLists[self.peaks.activeList]
        #for i in range (self.peaks.getpeakno()) :
        #    x=self.peaks.getPeaklistDetX()
        #   y=self.peaks.getPeaklistDetY()
        #  lstr = QtCore.QString(" %1\t%2").arg(x[i]).arg(y[i])
        #   self.ui.peakListWidget.addItem (lstr)
        for p in self.peaks.peaks:
            xy = p.DetXY
            lstr = QtCore.QString(" %1\t%2").arg(xy[0]).arg(xy[1])
            self.ui.peakListWidget.addItem(lstr)

    # peakListCLicked will give a new color to the peak
    def peakListClicked(self, event):
        itemNumber = self.ui.peakListWidget.currentRow()
        xy = self.peaks.peaks[itemNumber].DetXY

        # self.ui.zoomWidget.writeQImage_lut (self.myim.imArray, xy)
        self.ui.peakZoomWidget.writeQImage_lut(self.myim.imArray, xy)

        #for demo only
        subdat = self.myim.imArray[xy[1] - 10:xy[1] + 10, xy[0] - 10:xy[0] + 10]
        filtered = ndimage.gaussian_filter(subdat, 1)
        self.ui.peakZoomCalcWidget.arrayToQImage(filtered)
        resids = subdat - filtered
        self.ui.peakZoomResidsWidget.arrayToQImage(resids)


    def listButtonChanged(self, event):
        status = self.list1Button.isChecked()
        if (status):
            self.peaks.setActiveList(self.peaks0, self.peaks1, 0)
        else:
            self.peaks.setActiveList(self.peaks0, self.peaks1, 1)
        self.updatePeakList();
        self.ui.imageWidget.repaint()
        self.ui.zoomWidget.repaint()


    """ zoomMode turns the cursor in the image and zoom widgets to zoom select
    """

    def zoomMode(self):
        self.ui.imageWidget.zoomOn()
        self.ui.zoomWidget.zoomOn()
        self.setButtons(0)

    def addPeakMode(self):
        self.ui.imageWidget.peakAdd()
        self.ui.zoomWidget.peakAdd()
        self.setButtons(1)

    def selectMode(self):
        self.ui.imageWidget.selectOn()
        self.ui.setButtons(2)

    def unselectMode(self):
        self.ui.imageWidget.unselectOn()
        self.ui.setButtons(3)

    def maskMode(self):
        self.ui.imageWidget.maskOn()
        self.ui.setButtons(4)

    def unmaskMode(self):
        self.ui.imageWidget.unmaskOn()
        self.ui.setButtons(5)

    def selectRect(self, rect, sFlag):
        if (sFlag):
            self.peaks.setSelected(rect)
        else:
            self.peaks.setUnselected(rect)
        self.ui.imageWidget.repaint()

    def maskRect(self, rect, sFlag):
        self.mymask.setMask(rect, sFlag)
        self.ui.imageWidget.applyMask(self.mymask.img)
        self.ui.zoomWidget.applyMask(self.mymask.img)
        self.myim.applyMask(self.mymask.img)

    def clearMask(self):
        self.mymask.resetMask()
        self.ui.imageWidget.applyMask(self.mymask.img)
        self.ui.zoomWidget.applyMask(self.mymask.img)
        self.myim.applyMask(self.mymask.img)

    def saveMask(self):
        outstr = QtGui.QFileDialog.getSaveFileName(self, "Save Filename", self.workDirectory, 'Image File (*.tif)')
        self.mymask.saveToFile(outstr)

    def readMask(self):
        outstr = QtGui.QFileDialog.getOpenFileName(self, "Save Filename", self.workDirectory, 'Image File (*.tif)')
        self.mymask.readTiff(outstr)
        self.ui.imageWidget.applyMask(self.mymask.img)
        self.ui.zoomWidget.applyMask(self.mymask.img)

    def selAllPeaks(self):
        self.peaks.selectAll()
        self.ui.imageWidget.repaint()

    def clearAllPeaks(self):
        self.peaks.unselectAll()
        self.ui.imageWidget.repaint()

    def moveSelPeaks(self):
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

    def delSelPeaks(self):
        self.peaks.deleteSelected()
        self.updatePeakNumberLE()
        self.updatePeakList()
        self.ui.imageWidget.repaint()


    """ function to change background button color from gray when mode is inactive to
        yellow when active
    """

    def setButtons(self, buttonNumber):
        self.ui.zoomButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.addPeakButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.selectButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.unselectButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.maskButton.setStyleSheet("QPushButton {background-color: yellow}")
        self.ui.unmaskButton.setStyleSheet("QPushButton {background-color: yellow}")
        if (buttonNumber == 0):
            self.ui.zoomButton.setStyleSheet("QPushButton {background-color: green}")
        if (buttonNumber == 1):
            self.ui.addPeakButton.setStyleSheet("QPushButton {background-color: green}")
        if (buttonNumber == 2):
            self.ui.selectButton.setStyleSheet("QPushButton {background-color: green}")
        if (buttonNumber == 3):
            self.ui.unselectButton.setStyleSheet("QPushButton {background-color: green}")
        if (buttonNumber == 4):
            self.ui.maskButton.setStyleSheet("QPushButton {background-color: green}")
        if (buttonNumber == 5):
            self.ui.unmaskButton.setStyleSheet("QPushButton {background-color: green}")


    """ Update of the line edit to display # of list 1 and list 2 peaks
    """




    def updatePeakNumberLE(self):
        pn = self.peaks.getpeakno()
        pn1 = self.peaks1.getpeakno()
        str = QtCore.QString("List 1 : %1\tList 2 : %2").arg(pn).arg(pn1)
        self.ui.numPeaksLE.setText(str)

    def openDetectorCalibration(self):
        self.Display_Detector_calibration(self.detector)

    def saveDetectorCalibration(self):
        self.Update_Detector_calibration()

    def Display_Detector_calibration(self, det):
        self.ui.LE_Detector_Distance.setText(str(det.getdist()))
        XY = det.getbeamXY()
        self.ui.LE_Detector_Beam_X.setText(str(XY[0]))
        self.ui.LE_Detector_Beam_Y.setText(str(XY[1]))
        PS = det.getpsizeXY()
        self.ui.LE_Detector_Pixel_size_X.setText(str(PS[0]))
        self.ui.LE_Detector_Pixel_size_Y.setText(str(PS[1]))
        self.ui.LE_Detector_Wavelength.setText(str(det.getwavelength()))
        self.ui.LE_Detector_Rotation.setText(str(det.gettiltch()))
        self.ui.LE_Detector_Tilt.setText(str(det.gettiltom()))
        self.ui.LE_Detector_Twist.setText(str(det.gettwist()))
        self.ui.LE_Detector_2theta.setText(str(det.getttheta()))

    def Update_Detector_calibration(self):
        self.detector.setdist(float(self.ui.LE_Detector_Distance.text()))
        self.detector.setwavelength(float(self.ui.LE_Detector_Wavelength.text()))
        self.detector.settiltch(float(self.ui.LE_Detector_Rotation.text()))
        self.detector.settiltom(float(self.ui.LE_Detector_Tilt.text()))
        self.detector.settwist(float(self.ui.LE_Detector_Twist.text()))
        self.detector.setttheta(float(self.ui.LE_Detector_2theta.text()))
        bx = float(self.ui.LE_Detector_Beam_X.text())
        by = float(self.ui.LE_Detector_Beam_Y.text())
        px = float(self.ui.LE_Detector_Pixel_size_X.text())
        py = float(self.ui.LE_Detector_Pixel_size_Y.text())
        self.detector.setbeamXY([bx, by])
        self.detector.setpsizeXY([px, py])

    def SearchForPeaks(self):
        print 'Search for peaks'

        # thr=self.threshold                       # 100:       raw counts threshold for locating peaks
        #max_peak_size=self.mindist               # 10:        max allowed peak size with pixels above local background + Imin
        #num_of_segments = [self.pbox,self.pbox]  # [50.,50.]: number of segments in X and Y for local labckground estimation
        #perc=self.bbox                           # 1.0:       percent of median for background

        self.myim.search_for_peaks(self.peaks, 100, 10, [50., 50.], 1.0)
        self.updatePeakNumberLE()
        self.imageWidget.repaint()
        self.zoomWidget.repaint()
        self.updatePeakList()
        self.ui.imageWidget.repaint()

        print 'number of peaks received', self.peaks.getpeakno()

    def SearchForPeaksSeries(self):
        self.peaks.remove_all_peaks()
        z = QtCore.QChar('0')
        tempimg = myImage()
        for i in range(self.minRange, self.maxRange):
            newimage = QtCore.QString("%1%2.tif").arg(self.imageFilePref).arg(i, 3, 10, z)
            tempimg.readTiff(newimage)
            self.myim.search_for_peaks_arr(tempimg.imArray, self.peaks, 100, 10, [50, 50], 1.0)
        self.updatePeakNumberLE()
        self.imageWidget.repaint()
        self.zoomWidget.repaint()
        self.updatePeakList()
        self.ui.imageWidget.repaint()

    def mergeImageRange(self):
        # get the output tif file name....
        tempimg = myImage()
        outname = QtGui.QFileDialog.getSaveFileName(self, "Merge Filename", self.workDirectory, "Image File (*.tif)")
        z = QtCore.QChar('0')
        self.mergeSumMode = self.ui.sumButton.isChecked()

        nimages = self.maxRange - self.minRange + 1

        if (self.mergeSumMode == True):
            for i in range(self.minRange, self.maxRange + 1):
                newimage = QtCore.QString("%1%2.tif").arg(self.imageFilePref).arg(i, 3, 10, z)
                tempimg.readTiff(newimage)
                if i == self.minRange:
                    mergeArr = tempimg.imArray.copy().astype(np.float32)
                else:
                    mergeArr = tempimg.imArray + mergeArr
            maxval = np.max(mergeArr)
            if (maxval > 65535):
                scaleval = 65534. / maxval
                str = QtCore.QString("Merge exceeds 65535, scaled by %1").arg(scaleval)
                # qinfo = QtGui.QMessageBox.warning(None, "Information", str)
                mergeArr *= scaleval
        else:
            for i in range(self.minRange, self.maxRange + 1):
                newimage = QtCore.QString("%1%2.tif").arg(self.imageFilePref).arg(i, 3, 10, z)
                tempimg.readTiff(newimage)
                if i == self.minRange:
                    mergeArr = tempimg.imArray.copy().astype(np.float32) / nimages
                else:
                    mergeArr = tempimg.imArray / nimages + mergeArr

        # if maxval > 65535 :
        #    mergeArr = mergeArr / maxval * 655354.
        mergeArr = mergeArr.astype(np.uint16)
        # now write to tif file
        #im = Image.fromarray (mergeArr.astype(np.float32))
        #im.save (outname.toLatin1().data())
        imsave(outname.toLatin1().data(), mergeArr)
        self.openImageFile (outname)

    def SavePeakTable(self):
        print 'write PT'
        wdir = self.ui.imDirLE.text()
        PTFile = QtGui.QFileDialog.getSaveFileName(self, 'Save Peak Table', wdir)
        self.peaks.write_to_file(PTFile)

    def OpenPeakTable(self):
        print 'read PT'
        wdir = self.ui.imDirLE.text()
        PTFile = QtGui.QFileDialog.getOpenFileName(self, 'Open Peak Table', wdir)
        self.peaks.read_from_file(PTFile)
        self.updatePeakNumberLE()
        self.updatePeakList()
        self.ui.imageWidget.repaint()

    def PeakListBrowse(self):
        print 'peak list browse', self.ui.peakListWidget.currentRow()
        self.zmCentLoc[0] = 200
        self.zmCentLoc[1] = 300


    def readTextDetect(self):
        detfile = QtGui.QFileDialog.getOpenFileName(self, 'Open Detector File', self.workDirectory)
        self.detectFile = detfile
        self.detector.read_from_text_file(detfile.toLatin1().data())
        self.Display_Detector_calibration(self.detector)

    def writeTextDetect(self):
        detfile = QtGui.QFileDialog.getSaveFileName(self, 'Output Detector File', self.workDirectory)
        self.detector.write_to_text_file(detfile.toLatin1().data())


    def updatePlot(self):
        ptype = 0
        if (self.ui.symbCB.isChecked()):
            ptype = 1
        if (self.ui.splineCB.isChecked()):
            ptype |= 2
        self.ui.myplotWidget.setpType(ptype)
        # self.ui.myplotWidget.replot()
        tstr = self.ui.plot_titleLE.text().toLatin1().data()
        xstr = self.ui.plot_xLE.text().toLatin1().data()
        ystr = self.ui.plot_yLE.text().toLatin1().data()
        self.myplotWidget.setLabels(tstr, xstr, ystr)
        self.myplotWidget.plotData()

    def savePlotToFile(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Output Plot Image', self.workDirectory,
                                                     "Image File (*.png)")
        len = filename.length()
        if (len < 1): return
        self.myplotWidget.outputToFile(filename.toLatin1().data())


    def plotXYFromFile(self):

        filename = QtGui.QFileDialog.getOpenFileName(self, 'ASCII XY File', self.workDirectory, "Text File (*.txt)")
        len = filename.length
        if (len < 1): return
        file = open (filename.toLatin1().data(), 'r')
        xvals =[]
        yvals =[]
        i = 0
        for line in file :
            i = i+ 1
            line = line.strip()
            lineList = line.split(" ")
            xvals.append (float(lineList[0]))
            yvals.append (float(lineList[1]))
        self.myplotWidget.setXYData (xvals, yvals)

    def overlayPlotFromFile (self) :
        olayDlg = MyOverlayDlg ()
        olayDlg.setParams (self.olayFile, self.olaySecFlag)
        olayDlg.exec_()
        xvals =[]
        yvals =[]
        i=0

        file = open (olayDlg.infile, "r")
        for line in file :
            i = i+ 1
            line = line.strip()
            lineList = line.split(" ")
            xvals.append (float(lineList[0]))
            yvals.append (float(lineList[1]))
        self.myplotWidget.setOverlayXYData (xvals, yvals, False)

    def readXPOW (self) :
        table = self.ui.refSampleTabWidget
        table.clearContents()
        filename = QtGui.QFileDialog.getOpenFileName(self, "Input .txt File")
        refsamp = JCPDS ()
        refsamp.read_xpow (filename.toLatin1().data())
        propString = refsamp.getParamString()
        nrows = len (propString) / 2
        #nrowsTable=self.ui.refSampleTabWidget.rowCount()
        #if nrows > nrowsTable :
        self.ui.refSampleTabWidget.setRowCount (nrows)
        for i in range(nrows) :

            itemTitle = QtGui.QTableWidgetItem ()
            itemTitle.setBackgroundColor (QtCore.Qt.yellow)
            itemValue = QtGui.QTableWidgetItem ()
            itemTitle.setText (propString[i*2])
            itemValue.setText (str(propString[i*2+1]).strip())
            table.setItem (i, 0, itemTitle)
            table.setItem (i, 1, itemValue)

        # then load up the reflection table
        table = self.ui.sampleReflectTabWidget
        table.clearContents()
        nrows = len (refsamp.reflections)

        table.setRowCount (nrows)
        count = 0
        for r in refsamp.reflections :
            itemD = QtGui.QTableWidgetItem ()
            itemD.setText (str(r.d0))
            table.setItem (count, 0, itemD)
            itemIntens = QtGui.QTableWidgetItem ()
            itemIntens.setText (str(r.inten))
            table.setItem (count, 1, itemIntens)
            itemH = QtGui.QTableWidgetItem ()
            itemH.setText (str(r.h))
            table.setItem (count, 2, itemH)
            itemK = QtGui.QTableWidgetItem ()
            itemK.setText (str(r.k))
            table.setItem (count, 3, itemK)
            itemL = QtGui.QTableWidgetItem ()
            itemL.setText (str(r.l))
            table.setItem (count, 4, itemL)
            count += 1
        self.ui.refsampLabel.setText (filename)

    def readJCPDS (self):
        table = self.ui.refSampleTabWidget
        table.clearContents()
        filename = QtGui.QFileDialog.getOpenFileName(self, "Input .jcpds File")
        refsamp = JCPDS ()
        refsamp.read_file (filename)
        propString = refsamp.getParamString()

        nrows = len (propString) / 2
        #nrowsTable=self.ui.refSampleTabWidget.rowCount()
        #if nrows > nrowsTable :
        self.ui.refSampleTabWidget.setRowCount (nrows)
        for i in range(nrows) :

            itemTitle = QtGui.QTableWidgetItem ()
            itemTitle.setBackgroundColor (QtCore.Qt.yellow)
            itemValue = QtGui.QTableWidgetItem ()
            itemTitle.setText (propString[i*2])
            itemValue.setText (str(propString[i*2+1]).strip())
            table.setItem (i, 0, itemTitle)
            table.setItem (i, 1, itemValue)

        nrows = len (refsamp.reflections)

        # then load up the reflection table
        table = self.ui.sampleReflectTabWidget
        table.clearContents()
        table.setRowCount (nrows)
        count = 0
        for r in refsamp.reflections :
            itemD = QtGui.QTableWidgetItem ()
            itemD.setText (str(r.d0))
            table.setItem (count, 0, itemD)
            itemIntens = QtGui.QTableWidgetItem ()
            itemIntens.setText (str(r.inten))
            table.setItem (count, 1, itemIntens)
            itemH = QtGui.QTableWidgetItem ()
            itemH.setText (str(r.h))
            table.setItem (count, 2, itemH)
            itemK = QtGui.QTableWidgetItem ()
            itemK.setText (str(r.k))
            table.setItem (count, 3, itemK)
            itemL = QtGui.QTableWidgetItem ()
            itemL.setText (str(r.l))
            table.setItem (count, 4, itemL)
            count += 1


        self.ui.refsampLabel.setText (filename)

    """ Callback from integrateCurrentButton click
    """
    def intCurrent (self):
        # need to put a check in here to make sure that the ttheta image exists
        tthetaArr = np.zeros (self.imsize, dtype=np.float32)
        #f = open ('/home/harold/ttheta', 'r')
        #tthetaArr = np.fromfile (f,dtype=np.float32).reshape(self.imsize)
        #f.close()
        self.myim.integrate (self.detector.tthetaArr)
        self.integratePlotWidget.setXYData_Integrate (self.myim.tthetabin, self.myim.avg2tth)


    def testCalc (self) :
        #self.detector.create_ttheta_array (self.myim.imArraySize)
        self.detector.testStuff()

    def calc2theta (self) :
        saveFlag = self.ui.save2ThetaCB.isChecked()
        self.detector.calc2theta(saveFlag)

    def done2theta (self) :
        self.ui.integrateCurrentButton.setEnabled(True)

app = QtGui.QApplication(sys.argv)
atrex = Atrex()
atrex.show()

sys.exit(app.exec_())
