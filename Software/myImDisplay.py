from PyQt4 import QtCore, QtGui

import numpy as np
from math import *
from scipy.misc import imresize
from scipy.ndimage import zoom
from scipy.ndimage import filters
from myPeaks import *

class myImDisplay (QtGui.QWidget) :
    loadImage = 0
    dispMax = 65535
    dispMin = 0
    zmFac = 3
    zmRect = QtCore.QRect ()
    centPt = QtCore.pyqtSignal(QtCore.QPoint)
    addPeakSignal = QtCore.pyqtSignal (QtCore.QPoint)
    selectRectSignal = QtCore.pyqtSignal (QtCore.QRect, bool)
    maskRectSignal = QtCore.pyqtSignal (QtCore.QRect, bool)
    setButtonModeSignal = QtCore.pyqtSignal (int)
    imcoordsSelectSignal = QtCore.pyqtSignal (list)
    dragZm = False
    zoomToggle = True
    peakToggle = False
    selectFlag = False
    unselectFlag = False
    maskFlag = False
    unmaskFlag = False
    dragFlag = False
    applyMaskFlag = False
    rgb_lut = np.zeros ((3,256), dtype=np.uint8)
    cakeImageFlag = False
    peakBoxSize = 33



    #peaks = myPeaks ()
    
    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.setContextMenuPolicy (QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect (self.contextMenuKickoff)
        for i in range (256) :
            self.rgb_lut[:,i] = i

    def setPeakBoxSize (self,val) :
        self.peakBoxSize = val

    def setCakeImage (self) :
        self.cakeImageFlag = True

    def contextMenuKickoff (self, point) :
        gPos = self.mapToGlobal (point)
        cMenu = QtGui.QMenu ()
        cMenu.addAction ("Zoom", self.zoomOn)
        cMenu.addAction ("Add Peak", self.peakAdd)
        cMenu.addAction ("SelectPeaks", self.selectOn)
        cMenu.addAction ("DeselectPeaks", self.unselectOn)
        cMenu.addAction ("Mask", self.maskOn)
        cMenu.addAction ("Un-Mask", self.unmaskOn)

        cMenu.exec_(gPos)

    def zoomOn (self) :
        self.zoomToggle = True
        self.peakToggle = False
        self.selectFlag = False
        self.unselectFlag = False
        self.maskFlag = False
        self.unmaskFlag = False
        self.setButtonModeSignal.emit (0)

    def peakAdd (self) :
        self.peakToggle = True
        self.zoomToggle = False
        self.selectFlag = False
        self.unselectFlag = False
        self.maskFlag = False
        self.unmaskFlag = False
        self.setButtonModeSignal.emit (1)

    def selectOn (self) :
        self.peakToggle = False
        self.zoomToggle = False
        self.selectFlag = True
        self.unselectFlag = False
        self.maskFlag = False
        self.unmaskFlag = False
        self.setButtonModeSignal.emit (2)

    def unselectOn (self) :
        self.peakToggle = False
        self.zoomToggle = False
        self.selectFlag = False
        self.unselectFlag = True
        self.maskFlag = False
        self.unmaskFlag = False
        self.setButtonModeSignal.emit (3)

    def maskOn (self) :
        self.peakToggle = False
        self.zoomToggle = False
        self.selectFlag = False
        self.unselectFlag = False
        self.maskFlag = True
        self.unmaskFlag = False
        self.setButtonModeSignal.emit (4)

    def unmaskOn (self) :
        self.peakToggle = False
        self.zoomToggle = False
        self.selectFlag = False
        self.unselectFlag = False
        self.maskFlag = False
        self.unmaskFlag = True
        self.setButtonModeSignal.emit (5)
        
    def setMinMax (self, min, max) :
        self.dispMin = min
        self.dispMax = max
        #print "(min max ) are :", min, max

    def setZmRect (self,rect) :
        topLeft = rect.topLeft()
        bottomRight = rect.bottomRight()
        self.zmRect = rect
        self.zmSize = bottomRight - topLeft
        self.repaint()

    def calcHisto (self, fulldata) :
        histo = np.histogram (fulldata, 65535, (1,65534))
        a = histo [0]
        b = histo [1]
        npts = np.sum(a)
        cuma = np.zeros((len(a)), dtype=np.float64)
        totalPct = 0.
        for i in range (len(a)) :
            cuma[i] = totalPct + float(a[i]) / float(npts)
            totalPct = cuma[i]
            if cuma[i] <= 0.018 :
                self.ind_5 = b[i]
            if cuma[i] <= 0.982 :
                self.ind_95 = b[i]
        self.dispMax = self.ind_95
        self.dispMin = self.ind_5


    # this is for the creating of the 32BPP QImage, currently using the lut version
    def writeQImage (self, fulldata) :
        self.xsize = self.width()
        self.ysize = self.height()
        self.fulldata = fulldata
        tempdata = self.fulldata

        # DN scaling
        self.max = np.max (tempdata)/10.
        self.min = np.min (tempdata)
        range = self.max - self.min
        self.scale = 255. / range

        # size scaling
        h,w = self.fulldata.shape
        xscale = int(w/self.xsize)
        yscale = int (h/self.ysize)

        self.pscale = xscale
        if (yscale > self.pscale) :
            self.pscale = yscale

        print 'scale is :', self.pscale
        uarr = (self.scale * (self.fulldata - self.min)).astype(np.uint8)
        uarr = uarr[::self.pscale, ::self.pscale]

        a = np.zeros ((uarr.shape[0], uarr.shape[1],4), dtype=np.uint8)
        a[:,:,3]=255
        a[:,:,2]=255-uarr[:,:]
        a[:,:,1]=255-uarr[:,:]
        a[:,:,0]=255-uarr[:,:]

        self.qimage = QtGui.QImage (a.data, a.shape[1], a.shape[0],QtGui.QImage.Format_ARGB32)
        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()

    
    """ writeQImage_lut will scale the input raw data from 0 to 255 based upon
        dispMin and dispMax values. Currently using a grey scale lut but will
        build in several other options for color mapping DN.
    """
    def writeQImage_lut (self, fulldata) :
        # for input square image,  simply resize image to smallest dimension
        im_w = self.width()
        im_h = self.height()
        newdim = im_w
        if (im_h < im_w) :
            newdim = im_h
        
        self.fulldata = fulldata
        tempdata = self.fulldata

        h,w = self.fulldata.shape
        zmfac = float(newdim)/float(w)
        self.zmFac = zmfac
        self.max = np.max (tempdata)/10.
        self.min = np.min (tempdata)
        range255 = self.dispMax - self.dispMin
        self.scale = 255. / range255
        
        #print '(im_w im_h disp_width disp_height)', w, h, self.xsize, self.ysize
        #print 'scale is :', self.scalefac
        uarr = (self.scale * (self.fulldata - self.dispMin)).astype(np.float)
        uarr [uarr>255.] = 255.
        uarr [uarr<0.] = 0.
        uarr = uarr.astype(np.uint8)
        #newarr = imresize (uarr, (newdim,newdim))
        newarr = zoom (uarr, zmfac, order=3)
        self.imdata = newarr.copy()
        if (self.applyMaskFlag) :
            newarr = self.applyMaskToArray (newarr)
        #if (self.applyMaskFlag) :
        #    newarr = newarr * self.mymask

        #a = np.zeros ((newarr.shape[0], newarr.shape[1]), dtype=np.uint8)
        #a[:,:]=255-newarr[:,:]
        
        self.qimage = QtGui.QImage (newarr.data, newarr.shape[1], newarr.shape[0],
                                    QtGui.QImage.Format_Indexed8)

        #a[:,:,1]=255-uarr[:,:]
        #a[:,:,0]=255-uarr[:,:]

        # generate the lut
        
        for index in range(256) :
        #    self.qimage.setColor (index, QtGui.qRgb (index, index, index))
            self.qimage.setColor (index, QtGui.qRgb(self.rgb_lut[0,index], self.rgb_lut[1,index], self.rgb_lut[2,index]))
        #self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()
        #self.peakFind()


    def setLUT (self, ind) :
        self.rgb_lut = np.zeros ((3,256), dtype=np.uint8)
        if ind == 0 :
            for i in range (256) :
                self.rgb_lut[:,i] = i
        if ind == 1 :
            for i in range (256) :
                self.rgb_lut[:,i] = 255 - i
        if ind == 2 :
            f = open ("Data/Rainbow_Bands.lut", "rb")
            self.rgb_lut = np.fromfile (f, dtype=np.uint8).reshape (3,256)
        if ind == 3 :
            f = open ("Data/Redhot.lut", "rb")
            self.rgb_lut = np.fromfile (f, dtype=np.uint8).reshape (3,256)
        if ind == 4 :
            f = open ("Data/ICA.lut", "rb")
            self.rgb_lut = np.fromfile (f, dtype=np.uint8).reshape (3,256)
        if ind == 5 :
            f = open ("Data/thermal.lut", "rb")
            self.rgb_lut = np.fromfile (f, dtype=np.uint8).reshape (3,256)
        # Not being used
        if ind == 6 :
            f = open ("Data/haze.lut", "rb")
            self.rgb_lut = np.fromfile (f, dtype=np.uint8).reshape (3,256)
            #self.rgb_lut = temparr.reshape (3,256)
            #self.rgb_lut = temparr.reshape (3,256)
        for i in range(256) :
        #    self.qimage.setColor (index, QtGui.qRgb (index, index, index))
            self.qimage.setColor (i, QtGui.qRgb(self.rgb_lut[ 0,i], self.rgb_lut[ 1,i], self.rgb_lut[ 2,i]))
        self.repaint()


    #############################################################
    ####    Mouse Functions
    def mouseReleaseEvent (self, event) :
        self.dragZm = False
        """
        if (self.selectFlag | self.unselectFlag) :

            self.selectPointLR = event.pos ()
            #need to convert to fullres coords
            x1 = self.selectPointLR.x() / self.zmFac
            y1 = self.selectPointLR.y() / self.zmFac
            x0 = self.selectPointUL.x() / self.zmFac
            y0 = self.selectPointUL.y() / self.zmFac
            newRect = QtCore.QRect (x0, y0, x1-x0, y1-y0)
            smode = True
            if (self.unselectFlag) :
                smode = False
            # emit the signal so that the Atrex class can mark selected peaks
            self.dragFlag = False
            self.selectRectSignal.emit (newRect, smode)
"""
            
        
    def mousePressEvent (self, event) :
        xyzvals = [0.,0.,0]
        # if right button, let context menu handlers work

        if (event.button() == QtCore.Qt.RightButton) :
            return

        # full res coords
        xloc = int(event.x() / self.zmFac)
        yloc = int(event.y() / self.zmFac)
        # display coords
        xwin = event.x()
        ywin = event.y()
        xyzvals [0] = xloc
        xyzvals [1] = yloc

        # would like to get the image raw values for this point....
        val = self.fulldata [yloc, xloc]
        xyzvals [2] = val
        self.imcoordsSelectSignal.emit (xyzvals)

        # if the select button has been triggered, need to first
        # put down an anchor point or left point for qrect
        # return after setting the upper left
        if (self.selectFlag or self.unselectFlag) and not self.dragFlag :
            self.selectPointUL = event.pos()
            self.selectPointLR = event.pos()
            self.dragFlag = True
            self.setMouseTracking (True)
            return

        # do the same thing for the mask selection
        if (self.maskFlag or self.unmaskFlag) and not self.dragFlag :
            self.selectPointUL = event.pos()
            self.selectPointLR = event.pos()
            self.dragFlag = True
            self.setMouseTracking (True)
            return

        if (self.selectFlag or self.unselectFlag) and self.dragFlag :
            self.selectPointLR = event.pos ()
            #need to convert to fullres coords
            x1 = self.selectPointLR.x() / self.zmFac
            y1 = self.selectPointLR.y() / self.zmFac
            x0 = self.selectPointUL.x() / self.zmFac
            y0 = self.selectPointUL.y() / self.zmFac
            # insert logic here to determine upper left and lower right.... that will then be ul, lr
            newRect = QtCore.QRect (x0, y0, x1-x0, y1-y0)
            smode = True
            if (self.unselectFlag) :
                smode = False
            # emit the signal so that the Atrex class can mark selected peaks
            self.dragFlag = False
            self.setMouseTracking (False)
            self.selectRectSignal.emit (newRect, smode)
            return

        if (self.maskFlag or self.unmaskFlag) and self.dragFlag :
            self.selectPointLR = event.pos ()
            #need to convert to fullres coords
            x1 = self.selectPointLR.x() / self.zmFac
            y1 = self.selectPointLR.y() / self.zmFac
            x0 = self.selectPointUL.x() / self.zmFac
            y0 = self.selectPointUL.y() / self.zmFac

            if (x1 < x0) :
                up_left = x1
                wid = x0 - x1
            else :
                up_left = x0
                wid = x1 - x0
            if (y0 < y1) :
                up_top = y0
                ht = y1 - y0
            else :
                up_top = y1
                ht = y0 - y1
            newRect = QtCore.QRect (up_left, up_top, wid, ht)
            smode = True
            if (self.unmaskFlag) :
                smode = False
            # emit the signal so that the Atrex class can mark selected peaks
            self.dragFlag = False
            self.setMouseTracking (False)
            self.maskRectSignal.emit (newRect, smode)
            return




        # check to see if near the upperLeft corner of the zoom box,
        # if so, start dragging the zoom box
        
        xdist =  (xloc - self.zmRect.topLeft().x())
        ydist =  (yloc - self.zmRect.topLeft().y())
        dist =  sqrt (xdist*xdist+ ydist *ydist)
        print dist
        if (dist < 10) :
            self.dragZm = True
            return
        

        print '(X Y) : ', xloc, yloc
        newloc = QtCore.QPoint(xloc,yloc)
        if (self.zoomToggle) :
            self.centPt.emit (newloc)
        else :
            print 'new peak at ', xloc, yloc
            self.addPeakSignal.emit (QtCore.QPoint(xloc,yloc))
            
            
    #def mouseDoubleClickEvent (self, event) :
    #    print 'DOUBLE CLICK captured'

        
    def mouseMoveEvent (self, event) :
        
        if (self.dragZm ) :
            upleft = event.pos() / self.zmFac
            self.zmRect.setTopLeft(upleft)
            self.zmRect.setBottomRight (upleft+self.zmSize)
            self.centPt.emit (upleft + self.zmSize/2)
            self.repaint()
        if (self.selectFlag | self.unselectFlag) :
            self.selectPointLR =(event.pos())
            self.repaint()
        if (self.maskFlag | self.unmaskFlag) :
            self.selectPointLR =(event.pos())
            self.repaint()
            

    ''' test routine for peak finding based upon kernel maximum filter
        and threshold value'''
    
    def peakFind (self) :
        thresh = 1500
        neigh = 11
        self.dmax = filters.maximum_filter (self.fulldata, neigh).astype(np.float32)
        dsub = [self.dmax==self.fulldata]
        self.dmax = self.dmax * dsub
        self.dmax[self.dmax<thresh]=0
        print 'shape of dmaxf', self.dmax.shape

    """ Previously established myPeaks object made available to the
        imageWidget object
        """
    def setPeaks (self, pks) :
        self.peaks = pks 
        
    """ Paint routine for the imageWidget
    """
    def paintEvent (self, event) :
        w = self.width()
        h = self.height()
        dim = w
        if (dim >h):
            dim = h
        bsize2 = self.peakBoxSize / 2 * self.zmFac
        
        painter = QtGui.QPainter (self)
        if (self.loadImage ==1) :
                painter.drawImage (0, 0, self.qimage, 0., 0., dim, dim)
                if (self.cakeImageFlag) :
                    return
                topLeft = self.zmRect.topLeft() * self.zmFac
                botRight = self.zmRect.bottomRight() * self.zmFac
                painter.setPen (QtGui.QPen (QtCore.Qt.red))
                painter.drawRect (QtCore.QRect(topLeft, botRight))
                peakcount = self.peaks.getpeakno()
                painter.setPen (QtGui.QPen (QtCore.Qt.green))
                for i in range (peakcount) :
                    xloc = self.peaks.peaks[i].DetXY[0]*self.zmFac
                    yloc = self.peaks.peaks[i].DetXY[1]*self.zmFac
                    upLeft = QtCore.QPoint (xloc-bsize2,yloc-bsize2)
                    lowRight = QtCore.QPoint (xloc+bsize2+1, yloc+bsize2+1)
                    newRect = QtCore.QRect (upLeft, lowRight)
                    painter.setPen (QtGui.QPen (QtCore.Qt.green))
                    if self.peaks.peaks[i].selected[0] :
                        painter.setPen (QtGui.QPen (QtCore.Qt.magenta))
                    if self.peaks.peaks[i].clickSelected :
                        painter.setPen (QtGui.QPen (QtCore.Qt.yellow))
                    painter.drawRect (newRect)
                if (self.selectFlag and self.dragFlag) :
                    pen = QtGui.QPen (QtCore.Qt.magenta)
                    pen.setStyle (QtCore.Qt.DashLine)
                    painter.setPen (pen)

                    painter.drawRect (QtCore.QRect(self.selectPointUL, self.selectPointLR))
                if (self.unselectFlag and self.dragFlag) :
                    pen = QtGui.QPen (QtCore.Qt.cyan)
                    pen.setStyle (QtCore.Qt.DashLine)
                    painter.setPen (pen)
                    painter.drawRect (QtCore.QRect(self.selectPointUL, self.selectPointLR))
                if (self.maskFlag and self.dragFlag) :
                    pen = QtGui.QPen (QtCore.Qt.darkYellow)
                    pen.setStyle (QtCore.Qt.DashLine)
                    painter.setPen (pen)

                    painter.drawRect (QtCore.QRect(self.selectPointUL, self.selectPointLR))
                if (self.unmaskFlag and self.dragFlag) :
                    pen = QtGui.QPen (QtCore.Qt.yellow)
                    pen.setStyle (QtCore.Qt.DashLine)
                    painter.setPen (pen)
                    painter.drawRect (QtCore.QRect(self.selectPointUL, self.selectPointLR))

    def applyMask (self, fullmask) :
        self.applyMaskFlag = True
        zm = zoom (fullmask, self.zmFac, order=0)
        self.curmask = zm.astype (np.uint8)
        newdata = self.imdata.copy()
        #newdata[w[0],w[1]] = 0
        newdata = self.curmask * self.imdata
        #newdata[w[0],w[1]] = 0
        self.qimage = QtGui.QImage (newdata.data, newdata.shape[1], newdata.shape[0],
                                    QtGui.QImage.Format_Indexed8)
        for index in range(256) :
            self.qimage.setColor (index, QtGui.qRgb (index, index, index))

        self.repaint()


    def applyMaskToArray (self, arr) :

        return self.curmask * arr