# myMask.py
# python class for Atrex mask images, image will normally be established as the size of the Atrex tif image,
# and will be either 0 or 1.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PIL import Image
import numpy as np
from math import *
import os.path


class myMask (QObject):

    nsamps=0
    nlines=0




    def createMask (self, nsamps, nlines):
        self.img = np.ones ((nlines, nsamps), dtype=np.uint16)
        self.nsamps = nsamps
        self.nlines = nlines

    def setMask (self, rect, maskMode):
        #maskMode - true set to zero ; false set to 1
        ul = rect.topLeft()
        lr = rect.bottomRight()
        x0 = ul.x()
        y0 = ul.y()
        x1 = lr.x()
        y1 = lr.y()

        val = 0
        if not maskMode :
            val = 1

        self.img[y0:y1,x0:x1] = val


    def resetMask (self):
        self.img[:,:] = 1

    def saveToFile (self, fname):
        if (not fname.contains('.tif')) and (not fname.contains('.TIF')) :
            print "could not save : need a .tif extension"
            qinfo = QMessageBox.warning (None, "Information", "Output file requires .tif suffix, Please try again")
            return
        Img = Image.fromarray (self.img.astype (np.uint8))
        Img.save (fname.toLatin1().data(), "TIFF")

    def readTiff (self, infile) :
        self.imFileName = infile
        print 'Loading  mask',infile
        im = Image.open (infile.toLatin1().data())
        (x,y) = im.size

        tempimg = np.asarray(im.getdata()).astype(np.uint8)

        tempimg = np.reshape (tempimg,(y,x))
        self.img = tempimg.astype(np.uint16)
        #print self.imArray.min(), self.imArray.max()
