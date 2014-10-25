import numpy as np
from math import *
from struct import *
import pickle
from PyQt4 import QtCore



class myDetector:

    def __init__(self):
       self.dist   = 0.0
       self.beamx  = 0.0
       self.beamy  = 0.0
       self.psizex = 0.0
       self.psizey = 0.0
       self.nopixx = 0
       self.nopixY = 0
       self.angle  = 0.0
       self.alpha  = 0.0
       self.omega0 = 0.0
       self.ttheta0= 0.0     
       self.tiltom = 0.0       
       self.tiltch = 0.0


class myPeak:
    
    def __init__(self):
        self.Stat     = 0                            # peak status
        self.HKL      = np.zeros(3,dtype=np.int)     # Miller indices
        self.XYZ      = np.zeros(3,dtype=np.float)   # coordinates of the reciprocal sp. vector
        self.selected = np.zeros(2,dtype=np.int)     # 0-selcted, 1-visible
        self.DetXY    = np.zeros(2,dtype=np.float)   # area detector pixel coordinates
        self.Gonio    = np.zeros(6,dtype=np.float)   # goniometer settings for the Area detector
        self.GonioSS  = np.zeros(6,dtype=np.float)   # setting angles for solid state detector
        self.nen      = 0                            # number of different energy components
        self.energies = np.zeros(10,dtype=np.float)  # energies
        self.IntAD    = np.zeros(2,dtype=np.float)   # Intensity from area detector with e.s.d
        self.position = np.zeros(3,dtype=np.float)   # Intensity from area detector with e.s.d
        self.IntSSD   = np.zeros(2,dtype=np.float)   # Will now be used to store individualized peak fitting box size
        self.Adp      = myDetector()                 # Area detector parameters

    def setDetxy(self, XY):
        self.DetXY=XY

    def getDetxy(self):
        return self.DetXY

class myPeakTable:
    
    def __init__(self):
        self.peakno=0
        self.selectedno=0
        self.peaks=[]
        self.activeList=0
        #for i in range(10000):
        #    self.peaks.append(myPeak())

    def setSelected (self, rectCoords) :
        for p in self.peaks[:]:
            point = QtCore.QPoint (p.DetXY[0], p.DetXY[1])
            state = rectCoords.contains (point)
            if (state) :
                p.selected[0]=1

    def setUnselected (self, rectCoords) :
        for p in self.peaks[:]:
            point = QtCore.QPoint (p.DetXY[0], p.DetXY[1])
            state = rectCoords.contains (point)
            if (state) :
                p.selected[0]=0


    def getPeaklistDetX(self):
        b=[]
        for i in range(self.peakno):
            xy=self.peaks[i].getDetxy()
            b.append(xy[0])
        return b

    def getPeaklistDetY(self):
        b=[]
        for i in range(self.peakno):
            xy=self.peaks[i].getDetxy()
            b.append(xy[1])
        return b

    def copy_peaktable(self, PT):
        self.peaks=PT.get_peaks()
        self.peakno=PT.getpeakno()
        self.selectedno=PT.getselectedno()
    
    def setActiveList (self, peaks0, peaks1, ind) :
        if ind == 0:
            peaks1.copy_peaktable(self) 
            self.copy_peaktable(peaks0) 
        else:
            peaks0.copy_peaktable(self) 
            self.copy_peaktable(peaks1)

    def deleteSelected (self):
        for p in self.peaks[:]:
            if p.selected[0]==1:
                self.peaks.remove(p)

    def getpeakno(self):
        return len (self.peaks)
        #return self.peakno

    def get_peaks(self):
        return self.peaks

    def getselectedno(self):
        return self.selectedno
    
    def setpeakno(self, pn):
        self.peakno=pn

    def addPeak(self, peak):
        self.peaks.append (peak)
        #self.peaks[self.peakno]=peak
        #self.peakno=self.peakno+1
        self.peakno = len(self.peaks)

    def removePeaks(self, plist):
        for i in plist:
            self.peaks.pop(i)
        self.peakno=self.peakno-len(plist)

    def selectPeaks(self, plist):
        for i in plist:
            self.peaks[i].selected[0]=1

    def unselectPeak(self, pn):
        for i in pn:
            self.peaks[i].selected[0]=0

    def unselectAll(self):
        for p in self.peaks:
            p.selected[0]=0
        #self.peaks[:].selected[0]=0

    def selectAll(self):
        for p in self.peaks:
            p.selected[0]=1
        #self.peaks[:].selected[0]=1
     
    def write_to_file(self, filename):
        self.truncate()
        pickle.dump( self, open( filename, "wb" ))  

    def read_from_file(self, filename):
        a=pickle.load( open( filename, "rb" ) )   
        self.peaks[0:a.peakno-1]=a.peaks
        self.peakno=a.peakno
        self.selectedno=a.selectedno
        
    def truncate(self):
        self.peaks=self.peaks[0:self.peakno-1]

       
