### MainPeak.py
###
### This routine is part of the Atrex software package.
### The MainPeaks routine is a standalone routine for peak searching, bypassing the need to run the Atrex software.
### As can be seen, the input to the routine is a TIFF xrd file

from myImage import *
import myPeakTable

class MainPeaks () :

    def __init__(self, fname) :
        self.setImage (fname)


    def setImage (self, fname):

        self.myimage = myImage ()
        self.myimage.readTiffRaw (fname)
        self.peaks = myPeakTable.myPeakTable ()

    def peakSearch (self) :

        thr = 100
        max_peak_size = 10
        num_of_segments = [50, 50]
        perc = 1.
        self.myimage.search_for_peaks (self.peaks, thr, max_peak_size, num_of_segments, perc)
        count = 0
        for p in self.peaks.peaks :
            print count, p.DetXY[0], p.DetXY[1]
            count += 1

    def writePeaksToFile (self, asciiFile) :
        try :
            f = open (asciiFile, 'w')
            count = 0
            for p in self.peaks.peaks :
                s = '%d\t%d\t%d\r\n'%(count,p.DetXY[0], p.DetXY[1])
                f.write (s)
                count+= 1
            f.close()
        except IOError :
            print 'Error writing to %s'%(asciiFile)




testimage = '/home/harold/workdir/atrex_save/Software/Images/F1_Fs100_P4_C2_D1s_004.tif'
mp = MainPeaks (testimage)
mp.peakSearch ()
mp.writePeaksToFile ('/home/harold/peaks.txt')
mp.writePeaksToFile ('/home/harold/peaks.txt')