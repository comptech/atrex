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
    setButtonModeSignal = QtCore.pyqtSignal (int)
    dragZm = False
    zoomToggle = True
    peakToggle = False
    #peaks = myPeaks ()
    
    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.setContextMenuPolicy (QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect (self.contextMenuKickoff)

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
        
        
    def setMinMax (self, min, max) :
        self.dispMin = min
        self.dispMax = max
        print "(min max ) are :", min, max

    def setZmRect (self,rect) :
        topLeft = rect.topLeft()
        bottomRight = rect.bottomRight()
        self.zmRect = rect
        self.zmSize = bottomRight - topLeft
        self.repaint()

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
        

        a = np.zeros ((newarr.shape[0], newarr.shape[1]), dtype=np.uint8)
        a[:,:]=255-newarr[:,:]
        
        self.qimage = QtGui.QImage (a.data, a.shape[1], a.shape[0],
                                    QtGui.QImage.Format_Indexed8)
        #a[:,:,1]=255-uarr[:,:]
        #a[:,:,0]=255-uarr[:,:]

        # generate the lut
        
        for index in range(256) :
            self.qimage.setColor (index, QtGui.qRgb (index, index, index))
            
        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()
        #self.peakFind()

    def mouseReleaseEvent (self, event) :
        self.dragZm = False
        
    def mousePressEvent (self, event) :
        # if right button, let context menu handlers work
        if (event.button() == QtCore.Qt.RightButton) :
            return 
        xloc = int(event.x() / self.zmFac)
        yloc = int(event.y() / self.zmFac)

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
        
        if (self.dragZm == False) :
            return
        
        upleft = event.pos() / self.zmFac
        self.zmRect.setTopLeft(upleft)
        self.zmRect.setBottomRight (upleft+self.zmSize)
        self.centPt.emit (upleft + self.zmSize/2)
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
        
        painter = QtGui.QPainter (self)
        if (self.loadImage ==1) :
                painter.drawImage (0, 0, self.qimage, 0., 0., dim, dim)
                topLeft = self.zmRect.topLeft() * self.zmFac
                botRight = self.zmRect.bottomRight() * self.zmFac
                painter.setPen (QtGui.QPen (QtCore.Qt.red))
                painter.drawRect (QtCore.QRect(topLeft, botRight))
                actList = self.peaks.activeList
                peakcount = len(self.peaks.peakLists[actList])
                painter.setPen (QtGui.QPen (QtCore.Qt.green))
                for i in range (peakcount) :
                    xloc = self.peaks.peakLists[actList][i].x()*self.zmFac
                    yloc = self.peaks.peakLists[actList][i].y()*self.zmFac
                    upLeft = QtCore.QPoint (xloc-10.,yloc-10.)
                    lowRight = QtCore.QPoint (xloc+10, yloc+10)
                    newRect = QtCore.QRect (upLeft, lowRight)
                    
                    painter.drawRect (newRect)
                painter.setPen (QtGui.QPen (QtCore.Qt.black))
                                
