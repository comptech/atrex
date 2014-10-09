# myImage.py
# python class to handle ATREX tiff images, extract image data for display and
# conversion to a numpy array

from PyQt4 import QtCore
from PIL import Image
import numpy as np
from math import *
import os.path


class myImage :

    omega0 = ''
    omegaR = ''
    chi = ''
    exposureT = ''
    detector = ''
    
    imFileName =''

    def readTiff (self, infile) :
        self.imFileName = infile
        print 'Loading ',infile
        im = Image.open (infile.toLatin1().data())
        (x,y) = im.size
        print x, y
        #img = mpimg.imread(infile.toLatin1().data())
        #plt.imshow(im)
        self.imArray = np.asarray(im.getdata())
        self.imArray = np.reshape (self.imArray,(x,y))
        print self.imArray.min(), self.imArray.max()

    ''' readText reads the image's associated text file extracting the
        omega0 and omegaR, chi, detector, and exposure time values. These
        are put into the respective members of this class.
    '''
    def readText (self, infile) :
        status = True 
        tfile = QtCore.QString("%1.txt").arg(infile)
        qf = QtCore.QFile (tfile)
        if not qf.exists() :
            return False
        qf.open (QtCore.QFile.ReadOnly)
        qts = QtCore.QTextStream(qf)
        while True :
            str = qts.readLine ()
            if (str.length() ==0) :
                break
            tokenize = str.split ('=')
            if tokenize[0].contains('mega0') :
                self.omega0 = tokenize[1].trimmed()
            if tokenize[0].contains('megaR') :
                self.omegaR = tokenize [1].trimmed()
            if tokenize[0].contains ('chi') :
                self.chi = tokenize[1].trimmed()
            if tokenize[0].contains('detector') :
                self.detector = tokenize[1].trimmed()
            if tokenize[0].contains('exp') :
                self.exposureT = tokenize[1].trimmed()
        return True
            
            
        
        
        

    
