


from gaussfitter import *
import numpy as np
import math



class peakFit :

    def __init__(self, arr):
        s = arr.shape
        n= np.zeros((200,200))
        size = n.shape
        self.inarr = arr
        self.fitpars =[0.,0.,0.,0.,0.,0.,0.]

    def fitArr (self) :

        usemom=[True, True, True, True, True, True, True, True]
        self.fitpars = gaussfit (self.inarr, usemoment=usemom)
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

    def returnFit (self) :
        (nx,ny) = self.inarr.shape
        self.fitted = twodgaussian (self.fitpars, rotate=True, shape= self.inarr.shape)
        return self.fitted
