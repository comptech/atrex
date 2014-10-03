# myImage.py
# python class to handle ATREX tiff images, extract image data for display and
# conversion to a numpy array

from PIL import Image
import numpy as np
from math import *


class myImage :

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
        

    
