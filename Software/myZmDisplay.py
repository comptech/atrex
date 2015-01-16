from PyQt4 import QtCore, QtGui

import numpy as np
from math import *
from scipy.misc import imresize
from scipy.ndimage import zoom

class myZmDisplay (QtGui.QWidget) :
    loadImage = 0
    dispMax = 65535
    dispMin = 0
    zmFac = 4
    newx = 0
    newy = 0
    zoomToggle = True
    peakToggle = False
    zoomRect = QtCore.QRect()
    applyMaskFlag = False

    # Class Signals 
    addPeakSignal = QtCore.pyqtSignal (QtCore.QPoint)
    setButtonModeSignal = QtCore.pyqtSignal (int)
    zmRectSignal = QtCore.pyqtSignal(QtCore.QRect)
    rgb_lut = np.zeros ((3,256), dtype=np.uint8)
    for i in range (256):
        rgb_lut[:,i] = i

    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.setContextMenuPolicy (QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect (self.contextMenuKickoff)

    def setLUT (self, arr):
        self.rgb_lut[:,:] = arr[:,:]
        self.writeQImage_update()

    def contextMenuKickoff (self, point) :
        gPos = self.mapToGlobal (point)
        cMenu = QtGui.QMenu ()
        cMenu.addAction ("Zoom", self.zoomOn)
        cMenu.addAction ("Add Peak", self.peakAdd)
        cMenu.exec_(gPos)

    def zoomOn (self) :
        self.zoomToggle = True
        self.peakToggle = False
        self.setButtonModeSignal.emit (0)

    def peakAdd (self) :
        self.peakToggle = True
        self.zoomToggle = False
        self.setButtonModeSignal.emit (1)

    def setPeaks (self, pks) :
        self.peaks = pks 

    def setZmFac (self,zm) :
        self.zmFac = zm


    def setMinMax (self, min, max) :
        self.dispMin = min
        self.dispMax = max
        print "(min max ) are :", min, max


    def setFulldata (self, fd) :
        self.fulldata = fd 

    
    """ writeQImage_lut will scale the input raw data from 0 to 255 based upon
        dispMin and dispMax values. Currently using a grey scale lut but will
        build in several other options for color mapping DN.
        centloc[0] is x coord of center, centloc[1] is y coord
    """
    def writeQImage_lut (self, fulldata, centloc) :
        # for input square image,  simply resize image to smallest dimension
        im_w = self.width()
        im_h = self.height()
        # based on the size of the window, determine number of pixels
        # to extract from fulldata
        numsamp = im_w / self.zmFac 
        numline = im_h / self.zmFac 
        ns2 = numsamp / 2
        nl2 = numline / 2

        newdim = im_w
        if (im_h < im_w) :
            newdim = im_h

        self.fulldata = fulldata
        self.centloc = centloc

        h,w = self.fulldata.shape
        startx = centloc[0] - ns2
        starty = centloc[1] - nl2
        if (startx < 0) :
            startx = 0
        if (starty < 0) :
            starty = 0
        endx = startx + numsamp
        endy = starty + numline
        if (endx > w) :
            endx = w
        if (endy > h) :
            endy = h 

        if not self.applyMaskFlag :
            tempdata = self.fulldata [starty:endy,startx:endx]
        else :
            tempdata = self.fulldata [starty:endy, startx: endx] * self.mymask[starty:endy, startx: endx]

        zmRect = QtCore.QRect (QtCore.QPoint(startx, starty),QtCore.QPoint(endx,endy))
        self.zmRectSignal.emit (zmRect)
        self.zoomRect = zmRect

        range255 = self.dispMax - self.dispMin
        self.scale = 255. / range255
        
        #print '(im_w im_h disp_width disp_height)', w, h, self.xsize, self.ysize
        #print 'scale is :', self.scalefac
        uarr = (self.scale * (tempdata - self.dispMin)).astype(np.float)
        uarr [uarr>255.] = 255.
        uarr [uarr<0.] = 0.
        uarr = uarr.astype(np.uint8)
        #newarr = imresize (uarr, (newdim,newdim))

        # zoom up the array by the zmFac
        newarr = zoom (uarr, self.zmFac, order=3)
        ysize = newarr.shape[1] / 4 * 4
        xsize = newarr.shape[0] / 4 * 4

        a = np.zeros ((xsize, ysize), dtype=np.uint8)
        a[:,:]=newarr[0:ysize,0:xsize]
        self.newx = a.shape[0]
        self.newy = a.shape[1]
        self.qimage = QtGui.QImage (a.data, a.shape[1], a.shape[0],
                                    QtGui.QImage.Format_Indexed8)
        #a[:,:,1]=255-uarr[:,:]
        #a[:,:,0]=255-uarr[:,:]

        # generate the lut
        
        for index in range(256) :
            self.qimage.setColor (index, QtGui.qRgb (self.rgb_lut[0,index], self.rgb_lut[1,index], self.rgb_lut[2,index]))
            
        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()


    """ writeQImage_lut will scale the input raw data from 0 to 255 based upon
        dispMin and dispMax values. Currently using a grey scale lut but will
        build in several other options for color mapping DN.
        centloc[0] is x coord of center, centloc[1] is y coord
    """
    def writeQImage_update (self) :
        # for input square image,  simply resize image to smallest dimension
        im_w = self.width()
        im_h = self.height()
        # based on the size of the window, determine number of pixels
        # to extract from fulldata
        numsamp = im_w / self.zmFac
        numline = im_h / self.zmFac
        ns2 = numsamp / 2
        nl2 = numline / 2

        newdim = im_w
        if (im_h < im_w) :
            newdim = im_h



        h,w = self.fulldata.shape
        startx = self.centloc[0] - ns2
        starty = self.centloc[1] - nl2
        if (startx < 0) :
            startx = 0
        if (starty < 0) :
            starty = 0
        endx = startx + numsamp
        endy = starty + numline
        if (endx > w) :
            endx = w
        if (endy > h) :
            endy = h

        if not self.applyMaskFlag :
            tempdata = self.fulldata [starty:endy,startx:endx]
        else :
            tempdata = self.fulldata [starty:endy, startx: endx] * self.mymask [starty:endy, startx: endx]

        zmRect = QtCore.QRect (QtCore.QPoint(startx, starty),QtCore.QPoint(endx,endy))
        self.zmRectSignal.emit (zmRect)
        self.zoomRect = zmRect

        range255 = self.dispMax - self.dispMin
        self.scale = 255. / range255

        #print '(im_w im_h disp_width disp_height)', w, h, self.xsize, self.ysize
        #print 'scale is :', self.scalefac
        uarr = (self.scale * (tempdata - self.dispMin)).astype(np.float)
        uarr [uarr>255.] = 255.
        uarr [uarr<0.] = 0.
        uarr = uarr.astype(np.uint8)
        #newarr = imresize (uarr, (newdim,newdim))

        # zoom up the array by the zmFac
        newarr = zoom (uarr, self.zmFac, order=3)
        ysize = newarr.shape[1] / 4 * 4
        xsize = newarr.shape[0] / 4 * 4

        a = np.zeros ((xsize, ysize), dtype=np.uint8)
        a[:,:]=newarr[0:ysize,0:xsize]
        self.newx = a.shape[0]
        self.newy = a.shape[1]
        self.qimage = QtGui.QImage (a.data, a.shape[1], a.shape[0],
                                    QtGui.QImage.Format_Indexed8)
        #a[:,:,1]=255-uarr[:,:]
        #a[:,:,0]=255-uarr[:,:]

        # generate the lut

        #for index in range(256) :
        #   self.qimage.setColor (index, QtGui.qRgb (index, index, index))
        for index in range(256) :
            self.qimage.setColor (index, QtGui.qRgb (self.rgb_lut[0,index], self.rgb_lut[1,index], self.rgb_lut[2,index]))

        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()



    def mousePressEvent (self, event) :
        startPt = self.zoomRect.topLeft()
        xloc = event.x() / self.zmFac + startPt.x()
        yloc = event.y() / self.zmFac + startPt.y()
        if (self.peakToggle) :
            self.addPeakSignal.emit (QtCore.QPoint(xloc,yloc))

    def paintEvent (self, event) :
        w = self.width()
        h = self.height()
        dim = w
        if (dim >h):
            dim = h
        
        painter = QtGui.QPainter (self)
        
        
        if (self.loadImage ==1) :
                #painter.drawImage (0, 0, self.qimage, 0., 0., self.newx, self.newy)
                painter.drawImage (0,0, self.qimage, 0.,0.)
                actList = self.peaks.activeList
                peakcount = self.peaks.getpeakno()
                painter.setPen (QtGui.QPen (QtCore.Qt.green))
                startPt = self.zoomRect.topLeft()
                for i in range (peakcount) :
                    xloc = self.peaks.peaks[i].getDetxy()[0]
                    yloc = self.peaks.peaks[i].getDetxy()[1]
                    #check if in zoom window
                    centpt = QtCore.QPoint(xloc,yloc)
                    inside = self.zoomRect.contains (centpt)
                    if (inside != True):
                        continue ;
                    xloc = (xloc  - startPt.x()) * self.zmFac
                    yloc =  (yloc - startPt.y()) * self.zmFac
                    upLeft = QtCore.QPoint (xloc-10.,yloc-10.)
                    lowRight = QtCore.QPoint (xloc+10, yloc+10)
                    newRect = QtCore.QRect (upLeft, lowRight)
                    painter.setPen (QtGui.QPen (QtCore.Qt.magenta))
                    if self.peaks.peaks[i].isselected() :
                        painter.setPen (QtGui.QPen (QtCore.Qt.green))

                    painter.drawRect (newRect)
        #outline the widget
        painter.setPen (QtGui.QPen (QtCore.Qt.black))
        qrFrame = QtCore.QRect (0,0,w-1,h-1)
        painter.drawRect (qrFrame)
                                

    def applyMask (self, mask):
        self.mymask = mask
        self.applyMaskFlag = True
        self.writeQImage_update()

