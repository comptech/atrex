from PyQt4 import QtCore, QtGui

import numpy as np
from math import *

class myImDisplay (QtGui.QWidget) :
    loadImage = 0
    
    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)

    def writeQImage (self, fulldata) :
        self.xsize = self.width()
        self.ysize = self.height()
        self.fulldata = fulldata
        tempdata = self.fulldata

        h,w = self.fulldata.shape
        self.max = np.max (tempdata)/10.
        self.min = np.min (tempdata)
        range = self.max - self.min
        self.scale = 255. / range
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
        a[:,:,2]=uarr[:,:]
        a[:,:,1]=uarr[:,:]
        a[:,:,0]=uarr[:,:]

        self.qimage = QtGui.QImage (a.data, a.shape[1], a.shape[0],QtGui.QImage.Format_ARGB32)
        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()

    def paintEvent (self, event) :
        w = self.width()
        h = self.height()
        painter = QtGui.QPainter (self)
        if (self.loadImage ==1) :
                painter.drawImage (0, 0, self.qimage, 0., 0., w, h)
        
                
                                
