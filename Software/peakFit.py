


from gaussfitter import *
import numpy as np
import math
from PIL import Image

class peakFit :

    def __init__(self, arr):
        s = arr.shape
        n= np.zeros((200,200))
        size = n.shape
        self.inarr = arr
        self.fitpars =[0.,0.,0.,0.,0.,0.,0.]

    def fitArr (self) :
        bxsize = self.inarr.shape
        usemom=[True, True, True, True, True, True, True, True]
        # estimate fit parameters before fitting
        self.fitpars[0] = np.median (self.inarr)
        self.fitpars[1] = np.max (self.inarr)
        #find maximum location in inarr
        locmax = np.unravel_index(np.argmax (self.inarr), self.inarr.shape)


        self.fitpars[2] = locmax[1]
        self.fitpars[3] = locmax[0]
        self.fitpars[4] = 4
        self.fitpars[5] = 4

        self.fitpars = gaussfit (self.inarr, params=self.fitpars, usemoment=usemom)
        c='\t'
        print '***************Parameters **************'
        print '\tActual\tFitted'
        print 'backgnd : ',self.fitpars[0]
        print 'peak : ',self.fitpars[1]
        print 'cent_x : ',self.fitpars[2]
        print 'cent_y : ',self.fitpars[3]
        print 'width_x : ',self.fitpars[4]
        print 'width_y : ',self.fitpars[5]
        print 'rotate : ',self.fitpars[6]
        return self.fitpars


    def fitArray (self, myArr) :

        usemom=[True, True, True, True, True, True, True, True]
        self.fitpars = gaussfit (myArr, usemoment=usemom)
        c='\t'
        print '***************Parameters **************'
        print '\tActual\tFitted'
        print 'backgnd : ',self.fitpars[0]
        print 'peak : ',self.fitpars[1]
        print 'cent_x : ',self.fitpars[2]
        print 'cent_y : ',self.fitpars[3]
        print 'width_x : ',self.fitpars[4]
        print 'width_y : ',self.fitpars[5]
        print 'rotate : ',self.fitpars[6]
        return self.fitpars


    def returnFitArray (self, myArr) :
        (nx,ny) = myArr.shape
        self.fitted = twodgaussian (self.fitpars, rotate=True, shape= myArr.shape)
        return self.fitted


    def returnFit (self) :
        (nx,ny) = self.inarr.shape
        self.fitted = twodgaussian (self.fitpars, rotate=True, shape= self.inarr.shape)
        return self.fitted

    def interpArray (self, inarr, zmfac) :

        x,y=inarr.shape
        inarrcpx = np.zeros((x,y),dtype=np.complex128)
        inarrcpx[:].real = inarr
        iff = np.fft.fft2 (inarrcpx)
        iffshift = np.fft.fftshift(iff)
        #iffshift.tofile("/home/harold/workdir/ifftarr")

        nx_zm = x * zmfac
        ny_zm = y * zmfac
        x2= x / 2
        y2= y/2

        iffzm = np.zeros ((nx_zm, ny_zm), dtype=np.complex128)

        iffzm [0:x2, 0:y2]=iffshift[0:x2, 0:y2]
        iffzm [0:x2, ny_zm-y2:]=iffshift[0:x2, y2: ]
        iffzm [nx_zm-x2:, 0:y2]= iffshift[x2:, 0:y2]
        iffzm [nx_zm-x2:, ny_zm-y2:]= iffshift[x2:, y2:]

        #startLarge = nx_zm / 2 - x2
        #iffzm [startLarge:startLarge+x,startLarge:startLarge+x]=iff[:,:]



        #iffzm.tofile("/home/harold/workdir/ifftarrzm")
        fzm = np.abs(np.fft.ifft2(iffzm))
        #fzm = fzm.astype(np.int16)
        return fzm


