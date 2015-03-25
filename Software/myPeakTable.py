import numpy as np
from math import *
from struct import *
import pickle
from PyQt4 import QtCore
import myDetector




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
        self.Adp      = myDetector.myDetector()                 # Area detector parameters
        self.clickSelected = False

    def setDetxy(self, XY):
        self.DetXY=XY

    def getDetxy(self):
        return self.DetXY

    def isselected(self):
        return self.selected[0]

    def distance (self, peak):
        x1=self.DetXY[0]
        y1=self.DetXY[1]
        xy=peak.getDetxy()
        x2=xy[0]
        y2=xy[1]
        return pow(pow(x1-x2,2)+pow(y1-y2,2),0.5)

#--------------------------------------------------------------------------

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
        self.activeList = ind
        if ind == 0:
            peaks1.copy_peaktable(self) 
            self.copy_peaktable(peaks0)
            self.peaks1 = peaks1
        else:
            peaks0.copy_peaktable(self) 
            self.copy_peaktable(peaks1)
            self.peaks0 = peaks0

    def deleteSelected (self):
        for p in self.peaks[:]:
            if p.selected[0]==1:
                self.peaks.remove(p)

    def moveSelected (self):
        if (self.activeList==0) :
            ptOther = self.peaks1
        else :
            ptOther = self.peaks0
        for p in self.peaks[:] :
            if p.selected[0]==1:
                p.selected[0]=0
                ptOther.addPeak (p)
                self.peaks.remove(p)


    def getpeakno(self):
        return len (self.peaks)
        #return self.peakno

    def get_peaks(self):
        return self.peaks

    def getonepeak(self, i):
        return self.peaks[i]

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
            self.peaks[int(i)].selected[0]=1

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
        f=open(filename, "wb")
        pickle.dump(self, f)

    def read_from_file(self, filename):
        a=pickle.load( open( filename, "rb" ) )   
        self.peaks[0:a.peakno-1]=a.peaks
        self.peakno=a.peakno
        self.selectedno=a.selectedno
        
    def truncate(self):
        self.peaks=self.peaks[0:self.peakno-1]

    def remove_all_peaks(self):
        self.peakno=0
        del self.peaks[:]




    def find_closest_peak(self, peak, START_NO):
        tab=np.zeros([self.peakno-START_NO,2],dtype=np.float)
        for i in range (START_NO, self.peakno) :
            disti=peak.distance(self.getonepeak(i))
            tab[i-START_NO,0]=disti
            tab[i-START_NO,1]=i
        return tab


    def find_multiple_peak_copies(self):
        i=0
        while (i < self.peakno-2):
            p=self.getonepeak(i)
            di=self.find_closest_peak(p,i+1)
            b=di[:,0]
            w=np.where(b < 3)
            #w1=w.tolist()
            #if len(w) > 0:
           #     di=[[di],transpose([0,i])]
           #     w=[w,n_elements(di2)/2]
            #m=max(self.peaks[di[w,1]].intAD[0],kk)
            for j in w: self.selectPeaks((di[j,1]))
                #self.unselect_peak, di[w[kk],1]
           # self.deleteSelected()
           #     pn=self->peakno()
           #     if kk ne i then i=i+1
           # else:
            i=i+1
        self.deleteSelected()