# myImage.py
# python class to handle ATREX tiff images, extract image data for display and
# conversion to a numpy array

from PyQt4 import QtCore
from PIL import Image
import numpy as np
from math import *
import os.path
import congrid as cgd
import myPeakTable


class myImage :

    omega0 = ''
    omegaR = ''
    chi = ''
    exposureT = ''
    detector = ''
    imArraySize =[0,0]
    
    imFileName =''

    def readTiff (self, infile) :
        self.imFileName = infile
        print 'Loading ',infile
        im = Image.open (infile.toLatin1().data())
        (x,y) = im.size
        print x, y
        self.imArraySize=[x,y]
        #img = mpimg.imread(infile.toLatin1().data())
        #plt.imshow(im)
        self.imArray = np.asarray(im.getdata())
        self.imArray = np.reshape (self.imArray,(y,x))
        self.imArray_orig = self.imArray
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


    def estimate_local_background (self, img, nbinx, nbiny, thr, perc):
        n0x=len(img)
        n0y=len(img[0])
        out_img=np.zeros([n0x,n0y],dtype=np.int16)
        sx=int(n0x/nbinx)
        sy=int(n0y/nbiny)
        for i in range(nbinx):
            for j in range(nbiny):
                x1=i*sx
                if i < nbinx-1:
                    x2=(i+1)*sx
                else:
                    x2=n0x-1
                y1=j*sy
                if j < nbiny-1:
                    y2=(j+1)*sy
                else:
                    y2=n0y-1
                box=img[x1:x2,y1:y2]
                b=box[np.where(box > 0)]
                if len(b) > 0:
                    out_img[x1:x2,y1:y2]=np.median(b)*perc
                else:
                    out_img[x1:x2,y1:y2]=thr*perc
        return out_img


    def grow_peak (self, arr, bkg, x,y, mins, xmax, ymax):
        #-- up
        if y < ymax-1 :
            yu=y+1
            while (arr[x,yu] > bkg[x,y]+mins) and (yu < ymax-1): yu=yu+1
        else:
            yu=y
        #-- down
        if y > 0 :
            yd=y-1
            while (arr[x,yd] > bkg[x,y]+mins) and (yd > 0): yd=yd-1
        else:
            yd=y
        #-- left
        if x > 0 :
            xl=x-1
            while (max(arr[xl,yd:yu]) > bkg[x,y]+mins) and (xl > 0): xl=xl-1
        else:
            xl=x
        #-- right
        if x < xmax-1:
            xr=x+1
            while (max(arr[xr,yd:yu]) > bkg[x,y]+mins) and (xr < xmax-1) : xr=xr+1
        else:
            xr=x
        #----------- max intensity
        bb=arr[xl:xr,yd:yu]
        m=np.amax(bb)
        XY=np.where(bb == m)
        return [xl,xr, yd,yu, xl+XY[0][0],yd+XY[1][0],m]


    def search_for_peaks_arr (self, arr, peaks, thr, max_peak_size, num_of_segments, perc):
        sxy = arr.shape
        topX=sxy[1]
        topY=sxy[0]
        img1=cgd.congrid(arr, [1000,1000])
        bg=self.estimate_local_background (img1, 50, 50, 100, 1.0)

        w=np.where(img1-bg > thr)
        for i in range(len(w[0])):
            XYs=[w[1][i],w[0][i]]
            if img1[XYs[1],XYs[0]]-bg[XYs[1],XYs[0]] > thr :
                XY=[0.0,0.0]
                aa=self.grow_peak(img1, bg, XYs[1],XYs[0], thr/2., 1000, 1000)
                if (max([aa[1]-aa[0], aa[3]-aa[2]]) < max_peak_size) and (aa[6] > thr) :
                    XY[0]=aa[5]*topX/1000
                    XY[1]=aa[4]*topY/1000
                    peak=myPeakTable.myPeak()
                    peak.setDetxy(XY)
                    #peak.setIntAD=img1[aa[4],aa[5]]
                    #ref_peak.setgonio=im.sts.gonio
                    peaks.addPeak(peak)
                img1[aa[2]:aa[3],aa[0]:aa[1]]=0
        peaks.find_multiple_peak_copies()

    def search_for_peaks (self, peaks, thr, max_peak_size, num_of_segments, perc):
        #thr=self.threshold                       # 100:       raw counts threshold for locating peaks
        #max_peak_size=self.mindist               # 10:        max allowed peak size with pixels above local background + Imin
        #num_of_segments = [self.pbox,self.pbox]  # [50.,50.]: number of segments in X and Y for local labckground estimation
        #perc=self.bbox                           # 1.0:       percent of median for background

        topX=self.imArraySize[0]
        topY=self.imArraySize[1]
        img1=cgd.congrid(self.imArray, [1000,1000])
        bg=self.estimate_local_background (img1, 50, 50, 100, 1.0)

        w=np.where(img1-bg > thr)
        for i in range(len(w[0])):
            XYs=[w[1][i],w[0][i]]
            if img1[XYs[1],XYs[0]]-bg[XYs[1],XYs[0]] > thr :
                XY=[0.0,0.0]
                aa=self.grow_peak(img1, bg, XYs[1],XYs[0], thr/2., 1000, 1000)
                if (max([aa[1]-aa[0], aa[3]-aa[2]]) < max_peak_size) and (aa[6] > thr) :
                    XY[0]=aa[5]*topX/1000
                    XY[1]=aa[4]*topY/1000
                    peak=myPeakTable.myPeak()
                    peak.setDetxy(XY)
                    #peak.setIntAD=img1[aa[4],aa[5]]
                    #ref_peak.setgonio=im.sts.gonio
                    peaks.addPeak(peak)
                img1[aa[2]:aa[3],aa[0]:aa[1]]=0
        peaks.find_multiple_peak_copies()
        # remove duplicates that are too close


        #ptc=pt->get_object()
        #self.peaktable=ptc
        #obj_destroy, pt
        #if show_progress_bar then $
        #cgProgressBar -> Destroy
        #print, 'Initial number of points:',w0
        #print, 'Computation time: ',systime(/seconds)-t0
        #end

        
        
    # applies the mask to imgArray, mask must be same shape as imgArray
    def applyMask (self, arr):
        self.imArray = self.imArray_orig * arr
    
