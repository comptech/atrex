import numpy as np
from math import *
from struct import *
import cPickle as pickle
from PyQt4 import QtCore
import myDetector


class myPeak:
    def __init__(self):
        self.Stat = 0  # peak status
        self.HKL = np.zeros(3, dtype=np.int)  # Miller indices
        self.XYZ = np.zeros(3, dtype=np.float)  # coordinates of the reciprocal sp. vector
        self.selected = np.zeros(2, dtype=np.int)  # 0-selcted, 1-visible
        self.DetXY = np.zeros(2, dtype=np.float)  # area detector pixel coordinates
        self.Gonio = np.zeros(6, dtype=np.float)  # goniometer settings for the Area detector
        self.GonioSS = np.zeros(6, dtype=np.float)  # setting angles for solid state detector
        self.nen = 0  # number of different energy components
        self.energies = np.zeros(10, dtype=np.float)  # energies
        self.IntAD = np.zeros(2, dtype=np.float)  # Intensity from area detector with e.s.d
        self.position = np.zeros(3, dtype=np.float)  # Intensity from area detector with e.s.d
        self.IntSSD = np.zeros(2, dtype=np.float)  # Will now be used to store individualized peak fitting box size
        self.Adp = myDetector.myDetector()  # Area detector parameters
        self.clickSelected = False

    def setDetxy(self, XY):
        self.DetXY = XY

    def getDetxy(self):
        return self.DetXY

    def isselected(self):
        return self.selected[0]

    def distance(self, peak):
        x1 = self.DetXY[0]
        y1 = self.DetXY[1]
        xy = peak.getDetxy()
        x2 = xy[0]
        y2 = xy[1]
        return pow(pow(x1 - x2, 2) + pow(y1 - y2, 2), 0.5)

    def writePeak(self, file, ind):
        str = "%d %d %f %f %f %f %f" % (
            ind, self.Stat, self.DetXY[0], self.DetXY[1], self.XYZ[0], self.XYZ[1], self.XYZ[2])
        strout = "%s %d %d %d\r\n" % (str, self.HKL[0], self.HKL[1], self.HKL[2])
        file.write(strout)

    def parsePeak(self, str):
        s = str.split()
        self.Stat = int(s[1])
        self.DetXY[0] = float(s[2])
        self.DetXY[1] = float(s[3])
        self.XYZ[0] = float(s[4])
        self.XYZ[1] = float(s[5])
        self.XYZ[2] = float(s[6])
        self.HKL[0] = float(s[7])
        self.HKL[1] = float(s[8])
        self.HKL[2] = float(s[9])


# --------------------------------------------------------------------------

class myPeakTable:
    def __init__(self):
        self.peakno = 0
        self.selectedno = 0
        self.peaks = []
        self.activeList = 0
        #for i in range(10000):
        #    self.peaks.append(myPeak())

    def zero (self) :
        self.peakno = 0
        del self.peaks[:]

    def setSelected(self, rectCoords):
        for p in self.peaks[:]:
            point = QtCore.QPoint(p.DetXY[0], p.DetXY[1])
            state = rectCoords.contains(point)
            if (state):
                p.selected[0] = 1


    def setUnselected(self, rectCoords):
        for p in self.peaks[:]:
            point = QtCore.QPoint(p.DetXY[0], p.DetXY[1])
            state = rectCoords.contains(point)
            if (state):
                p.selected[0] = 0


    def getPeaklistDetX(self):
        b = []
        for i in range(self.peakno):
            xy = self.peaks[i].getDetxy()
            b.append(xy[0])
        return b

    def getPeaklistDetY(self):
        b = []
        for i in range(self.peakno):
            xy = self.peaks[i].getDetxy()
            b.append(xy[1])
        return b

    def copy_peaktable(self, PT):
        self.peaks = PT.get_peaks()
        self.peakno = PT.getpeakno()
        self.selectedno = PT.getselectedno()

    def setActiveList(self, peaks0, peaks1, ind):
        self.activeList = ind
        if ind == 0:
            peaks1.copy_peaktable(self)
            self.copy_peaktable(peaks0)
            self.peaks1 = peaks1
        else:
            peaks0.copy_peaktable(self)
            self.copy_peaktable(peaks1)
            self.peaks0 = peaks0

    def deleteSelected(self):
        for p in self.peaks[:]:
            if p.selected[0] == 1:
                self.peaks.remove(p)

    def moveSelected(self):
        if (self.activeList == 0):
            ptOther = self.peaks1
        else:
            ptOther = self.peaks0
        for p in self.peaks[:]:
            if p.selected[0] == 1:
                p.selected[0] = 0
                ptOther.addPeak(p)
                self.peaks.remove(p)


    def getpeakno(self):
        return len(self.peaks)
        #return self.peakno

    def get_peaks(self):
        return self.peaks

    def getonepeak(self, i):
        return self.peaks[i]

    def getselectedno(self):
        return self.selectedno

    def setpeakno(self, pn):
        self.peakno = pn

    def addPeak(self, peak):
        self.peaks.append(peak)
        #self.peaks[self.peakno]=peak
        #self.peakno=self.peakno+1
        self.peakno = len(self.peaks)

    def removePeaks(self, plist):
        for i in plist:
            self.peaks.pop(i)
        self.peakno = self.peakno - len(plist)

    def selectPeaks(self, plist):
        for i in plist:
            self.peaks[int(i)].selected[0] = 1

    def unselectPeak(self, pn):
        for i in pn:
            self.peaks[i].selected[0] = 0

    def unselectAll(self):
        for p in self.peaks:
            p.selected[0] = 0
            #self.peaks[:].selected[0]=0

    def selectAll(self):
        for p in self.peaks:
            p.selected[0] = 1
            #self.peaks[:].selected[0]=1

    def write_to_file(self, filename):
        self.truncate()
        f = open(filename, "wb")
        pickle.dump(self, f)
        f.close()

    # ASCII file write , pickle not seeming to work for class...
    def write_to_fileA(self, filename):
        npks = self.getpeakno()
        if npks < 1:
            return
        str = "%d\r\n" % npks
        f = open(filename, "w")
        f.write(str)
        count = 0
        for p in self.peaks:
            p.writePeak(f, count)
            count += 1
        f.close()




    def read_from_fileA(self, filename):
        f = open(filename, "r")
        self.peaks = []
        count = -1
        for line in f:
            if count == -1:
                npeaks = int(line)
                count += 1
            else:

                m = myPeak()
                m.parsePeak(line)
                self.addPeak(m)
                count += 1


    def read_from_file(self, filename):
        a = pickle.load(open(filename, "rb"))
        self.peaks[0:a.peakno - 1] = a.peaks
        self.peakno = a.peakno
        self.selectedno = a.selectedno


    def truncate(self):
        self.peaks = self.peaks[0:self.peakno - 1]


    def remove_all_peaks(self):
        self.peakno = 0
        del self.peaks[:]

    def calculate_all_xyz_from_pix (self, det, kappa,theta,omegaFlag) :

        for p in self.peaks :
            pix = p.getDetxy()
            gonio = p.Gonio
            gonio[0] = kappa
            gonio[1] = theta







    def remove_peaks_outside_aa(self, detect):
        for p in self.peaks:
            xy = p.getDetxy()

            x = xy[0] - detect.nopixx / 2.
            y = xy[1] - detect.nopixy / 2.
            dist = sqrt(x ** 2 + y ** 2)
            if (dist > detect.nopixx / 2 - 10.):
                p.selected[0] = 1
            else:
                p.selected[0] = 0
        self.deleteSelected()


    def find_closest_peak(self, peak, START_NO):
        tab = np.zeros([self.peakno - START_NO, 2], dtype=np.float)
        for i in range(START_NO, self.peakno):
            disti = peak.distance(self.getonepeak(i))
            tab[i - START_NO, 0] = disti
            tab[i - START_NO, 1] = i
        return tab


    def find_close_overlaps (self, pn, farval) :

        noverlaps = [0,pn]
        xy1 = self.peaks[pn].getDetxy()
        for j in range (self.peakno-1) :
            if j != pn :
                xy2 = self.peaks[j].getDetxy()
                dxy = np.asarray(xy1) - np.asarray(xy2)
                dst = sqrt (dxy[0]**2 + dxy[1]**2)
                if dst < farval :
                    noverlaps[0] = noverlaps[0] + 1
                    noverlaps.append(j)
        return noverlaps




    def find_multiple_peak_copies(self):
        i = 0
        while (i < self.peakno - 2):
            p = self.getonepeak(i)
            di = self.find_closest_peak(p, i + 1)
            b = di[:, 0]
            w = np.where(b < 3)
            #w1=w.tolist()
            #if len(w) > 0:
            #     di=[[di],transpose([0,i])]
            #     w=[w,n_elements(di2)/2]
            #m=max(self.peaks[di[w,1]].intAD[0],kk)
            for j in w: self.selectPeaks((di[j, 1]))
            #self.unselect_peak, di[w[kk],1]
            # self.deleteSelected()
            #     pn=self->peakno()
            #     if kk ne i then i=i+1
            # else:
            i = i + 1
        self.deleteSelected()


    def select_close_overlaps(self, far):
        npeaks = self.peakno
        for i in range(npeaks - 3):
            xy1 = self.peaks[i].getDet()
            for j in range(i + 1, npeaks - 2):
                xy2 = self.peaks[j].getDetxy()
                dist = self.getDist(xy1, xy2)
                if (dist < far):
                    self.peaks[i].selected[0] = 1
                    self.peaks[j].selected[0] = 1


    def getDist(self, xy1, xy2):
        xdiff = xy1[0] - xy2[0]
        ydiff = xy1[1] - xy2[1]
        return sqrt(xdiff ** 2 + ydiff ** 2)

    def save_p4p(self, fname):
        f = open(fname, "w")
        str = 'FILEID Seattle      ?             4.00        08/20/08 14:27:16 C8H8Se3\r\n'
        f.write(str)
        str = 'SITEID ?                                   ?\r\n'
        f.write(str)
        str = 'TITLE    ?\r\n'
        f.write(str)
        str = 'CHEM   C8 H8 Se3'
        f.write(str)
        str = 'CELL      4.9159   11.1888   16.6681   90.0000   90.0000   90.0000    916.791\r\n'
        f.write(str)
        str = 'CELLSD    0.0011    0.0028    0.0091    0.0000    0.0000    0.0000     0.229\r\n'
        f.write(str)
        str = 'ORT1    -4.4774786e-002  2.9954357e-002  5.4960791e-002\r\n'
        f.write(str)
        str = 'ORT2    -4.7662384e-002  7.9853413e-002 -2.2988310e-002\r\n'
        f.write(str)
        str = 'ORT3    -1.9262548e-001 -2.6721303e-002 -7.0872242e-003\r\n'
        f.write(str)
        str = 'ZEROS   0.0000000  0.0000000  0.0000000    0.0000    0.0000    0.0000\r\n'
        f.write(str)
        str = 'SOURCE ?      0.41328   0.41328   0.41328   1.00000    0.00    0.00\r\n'
        f.write(str)
        str = 'LIMITS    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00    0.00\r\n'
        f.write(str)
        str = 'MORPH  ?\r\n'
        f.write(str)

        str = 'DNSMET ?\r\n'
        f.write(str)
        str = 'CCOLOR ?\r\n'
        f.write(str)
        str = 'CSIZE  ?            ?            ?            ?            ?\r\n'
        f.write(str)
        str = 'ADPAR      512.0000    512.0000      5.0000    1024\r\n'
        f.write(str)
        str = 'ADCOR       20.1957      9.0120     -0.0658      0.0000      0.0000      0.0000\r\n'
        f.write(str)
        str = 'BRAVAIS Orthorhombic          P\r\n'
        f.write(str)
        str = 'MOSAIC  0.44 0.84\r\n'
        f.write(str)
        st0 = 'REF1K H      -1  -4   2 -30.000 180.000   0.150  54.736   15.40  166.45 1691.26    158'
        z = 0.0
        for p in self.peaks:
            str = '%s%11.6f%11.6f%11.6f%11.6f%11.6f%11.6f%11.6f\r\n'%(st0, p.XYZ[0], p.XYZ[1], p.XYZ[2], z, z, z, z)
            f.write(str)

        str = 'DATA  SPATIAL linear          linear          3.0  512.00  512.00   17.000   3136 1024\r\n'
        f.write(str)
        f.close()


