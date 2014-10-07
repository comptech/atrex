from PyQt4 import QtCore, QtGui

import numpy as np
from math import *
from scipy.misc import imresize
from scipy.ndimage import zoom

class myImDisplay (QtGui.QWidget) :
    loadImage = 0
    dispMax = 65535
    dispMin = 0
    
    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)

    def setMinMax (self, min, max) :
        self.dispMin = min
        self.dispMax = max
        print "(min max ) are :", min, max


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
        a[:,:,2]=255-uarr[:,:]
        a[:,:,1]=255-uarr[:,:]
        a[:,:,0]=255-uarr[:,:]

        self.qimage = QtGui.QImage (a.data, a.shape[1], a.shape[0],QtGui.QImage.Format_ARGB32)
        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()

    

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
        print 'zoom fac : ', zmfac 
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
            #print index

        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()

    def paintEvent (self, event) :
        w = self.width()
        h = self.height()
        dim = w
        if (dim >h):
            dim = h
        print 'window dim is ', dim
        painter = QtGui.QPainter (self)
        if (self.loadImage ==1) :
                painter.drawImage (0, 0, self.qimage, 0., 0., dim, dim)
                
                
                                
