from PyQt4 import QtCore, QtGui

import numpy as np
from math import *
from scipy.misc import imresize
from scipy.ndimage import zoom

class myZmPeakDisplay (QtGui.QWidget) :
    loadImage = 0
    dispMax = 1000
    dispMin = 0
    zmFac = 4.
    newx = 0
    newy = 0
    ns = 21
    nl = 21
    zoomToggle = True
    peakToggle = False
    zoomRect = QtCore.QRect()


    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.zoomToggle = False


    def arrayToQImage (self, arr) :
        input_xy = arr.shape

        # for input square image,  simply resize image to smallest dimension
        im_w = self.width()
        im_h = self.height()

        zmfac = float(im_w)/ input_xy[0]
        zmfac_y = float(im_w)/input_xy[1]

        if zmfac_y < zmfac :
            zmfac = zmfac_y
        self.zmFac = zmfac

         # DN scaling
        maxval = np.max (arr)
        minval = np.min (arr)
        self.dispMin = minval
        self.dispMax = maxval



        range255 = self.dispMax - self.dispMin
        self.scale = 255. / range255
        #print '(im_w im_h disp_width disp_height)', w, h, self.xsize, self.ysize
        #print 'scale is :', self.scalefac
        uarr = (self.scale * (arr- self.dispMin)).astype(np.float)
        uarr [uarr>255.] = 255.
        uarr [uarr<0.] = 0.
        uarr = uarr.astype(np.uint8)

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

        # generate the lut

        for index in range(256) :
            self.qimage.setColor (index, QtGui.qRgb (index, index, index))

        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()

    def writeQImage_lut (self, fulldata, centloc) :
        # for input square image,  simply resize image to smallest dimension
        im_w = self.width()
        im_h = self.height()
        # based on the size of the window, determine number of pixels
        # to extract from fulldata
        zmfac = float(im_w) / self.ns
        zmfac_y = float(im_h) / self.nl
        if zmfac_y < zmfac :
            zmfac = zmfac_y
        self.zmFac = zmfac


        # used for startx and starty location
        ns2 = self.ns / 2
        nl2 = self.nl / 2

        newdim = im_w
        if (im_h < im_w) :
            newdim = im_h

        self.fulldata = fulldata
        h,w = self.fulldata.shape
        startx = centloc[0] - ns2
        starty = centloc[1] - nl2
        if (startx < 0) :
            startx = 0
        if (starty < 0) :
            starty = 0
        endx = startx + self.ns
        endy = starty + self.nl
        if (endx > w) :
            endx = w
        if (endy > h) :
            endy = h

        tempdata = self.fulldata [starty:endy,startx:endx]
        zmRect = QtCore.QRect (QtCore.QPoint(startx, starty),QtCore.QPoint(endx,endy))

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
            self.qimage.setColor (index, QtGui.qRgb (index, index, index))

        self.qimage.ndarray = a
        self.loadImage = 1
        self.repaint()


    def paintEvent (self, event) :
        w = self.width()
        h = self.height()
        dim = w
        if (dim >h):
            dim = h

        painter = QtGui.QPainter (self)
        bound = QtCore.QRect (0, 0, w-1, h-1) ;
        painter.drawRect (bound)

        if (self.loadImage ==1) :
                #painter.drawImage (0, 0, self.qimage, 0., 0., self.newx, self.newy)
                painter.drawImage (0,0, self.qimage, 0.,0.)