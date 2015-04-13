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
    barFlag = 1 # set for vertical bar, 2 for horizontal , 0 for none
    barDrag = False # rubber banding of vertical bar becomes true once user presses mouse near current location
    vbarloc = ns / 2
    hbarloc = nl / 2
    startx = 0
    starty = 0
    slideBarSignal = QtCore.pyqtSignal (int, int, int)
    rawArr = None

    def __init__(self, parent) :
        QtGui.QWidget.__init__(self, parent)
        self.zoomToggle = False

    def calcHisto (self, fulldata) :
        histo = np.histogram (fulldata, 65535, (1,65534))
        a = histo [0]
        b = histo [1]
        npts = np.sum(a)
        cuma = np.zeros((len(a)), dtype=np.float64)
        totalPct = 0.
        self.ind_5=0

        for i in range (len(a)) :
            cuma[i] = totalPct + float(a[i]) / float(npts)
            totalPct = cuma[i]
            if cuma[i] <= 0.018 :
                self.ind_5 = b[i]
            if cuma[i] <= 0.982 :
                self.ind_95 = b[i]
        self.dispMax = self.ind_95
        self.dispMin = self.ind_5

    def setMinMax (self, min, max) :
        self.dispMin = min
        self.dispMax = max

        range255 = self.dispMax - self.dispMin
        self.scale = 255. / range255
        #print '(im_w im_h disp_width disp_height)', w, h, self.xsize, self.ysize
        #print 'scale is :', self.scalefac
        uarr = (self.scale * (self.rawArr- self.dispMin)).astype(np.float)
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




    def arrayToQImage (self, arr, x0, y0) :
        input_xy = arr.shape
        self.startx = x0
        self.starty = y0

        self.rawArr = arr
        # for input square image,  simply resize image to smallest dimension
        im_w = self.width()
        im_h = self.height()
        self.ns = im_w
        self.nl = im_h

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
        self.vbarloc = float(input_xy[1]) / 2.
        self.hbarloc = float(input_xy[0]) / 2.
        self.vbarloc_orig = self.vbarloc
        self.hbarloc_orig = self.hbarloc

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
        self.vbarloc = float(im_w) / 2.
        self.hbarloc = float(im_h) / 2.


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
        self.startx = startx
        self.starty = starty
        if (endx > w) :
            endx = w
        if (endy > h) :
            endy = h

        tempdata = self.fulldata [starty:endy,startx:endx]
        self.rawArr = tempdata
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

    def mousePressEvent(self, event):
        button = event.button()
        if (button != 1) :
            return
        x = event.x()
        y = event.y()
        #turn on barDrag if mouseclick near the vert or horiz bar
        if self.barFlag == 1 :
            if abs (x - self.vbarloc * self.zmFac) < 15 :
                self.barDrag = True
        if self.barFlag == 2 :
            if (abs(y-self.hbarloc * self.zmFac)<15) :
                self.barDrag = True

    def mouseReleaseEvent (self, event):
        if (self.barDrag):
            self.barDrag = False
            if self.barFlag == 1 :
                self.vbarloc = event.x() / self.zmFac
                vbarlocFull = self.startx + event.x() / self.zmFac
                hbarlocFull = self.starty

            if self.barFlag == 2 :
                vbarlocFull = self.startx
                hbarlocFull = self.starty +event.y() / self.zmFac
                self.hbarloc = event.y() / self.zmFac
            self.slideBarSignal.emit (self.barFlag, vbarlocFull, hbarlocFull)
            self.repaint()

    def setBarFlag (self, val):
        self.barFlag = val

    def mouseMoveEvent (self, event):

        if self.barDrag :
            if self.barFlag == 1 :
                self.vbarloc = event.x() / self.zmFac
                vbarlocFull = self.startx + event.x() / self.zmFac
                hbarlocFull = self.starty

            if self.barFlag == 2 :
                vbarlocFull = self.startx
                hbarlocFull = self.starty +event.y() / self.zmFac
                self.hbarloc = event.y() / self.zmFac
            #self.slideBarSignal.emit (self.barFlag, vbarlocFull, hbarlocFull)
            self.repaint()


    def setBarFlag (self, ind):
        self.barFlag = ind

        self.vbarloc = self.vbarloc_orig
        self.hbarloc = self.hbarloc_orig
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
                if (self.barFlag == 1): #vertical bar
                    xloc = self.vbarloc * self.zmFac
                    painter.setPen (QtGui.QPen (QtCore.Qt.yellow))
                    painter.drawLine (xloc, 0, xloc, h-1)
                if (self.barFlag == 2): #horiz bar
                    yloc = self.hbarloc * self.zmFac
                    painter.setPen (QtGui.QPen (QtCore.Qt.yellow))
                    painter.drawLine (0, yloc, w-1, yloc)
