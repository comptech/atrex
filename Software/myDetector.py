import os
import pickle
import tifffile

from crystallography import *
from vector_math import *
from threading import Thread
from PyQt4 import QtCore, QtGui
from ctypes import *
from numpy.ctypeslib import ndpointer
from platform import *
from myImage import *
from calibrant import *
import congrid as cgd
from gaussfitter import *
from peakFit1 import *
from scipy.misc import imresize
#import Atrex

import myPeakTable


class myDetector (QtCore.QObject):

    tDone = QtCore.pyqtSignal (int)
    tDoneAll = QtCore.pyqtSignal ()
    calPeaks = QtCore.pyqtSignal()
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.dist = 0.0
        self.beamx = 0.0
        self.beamy = 0.0
        self.psizex = 0.0
        self.psizey = 0.0
        self.nopixx = 2048
        self.nopixy = 2048
        self.twist = 0.0
        self.alpha = 0.
        self.angle = 0.
        self.tiltom = 0.0
        self.tiltch = 0.0
        self.ttheta = 0.0
        self.wavelength = 0.0
        self.calibrant = 1
        self.dacopen = 18.

        self.gonio = [0., 0., 0.]
        self.tthetaArr = np.zeros((2048,2048), dtype=np.float32)
        self.tthetaBin = np.zeros ((2048,2048), dtype=np.uint16)
        self.threadDone = [False, False, False, False, False, False, False, False]
        self.refineTwistFlag = False

        osname = system()

        if "Win" in osname :
            self.CalcTheta = CDLL ("./ctheta.dll")
        else :
            self.CalcTheta = CDLL ('./ctheta.so')

        self.tDone.connect (self.threadDoneSlot)

        self.CalcTheta.testPyth.argtypes= [ndpointer(np.int32), c_int]
        self.CalcTheta.create_theta_array.argtypes = [ndpointer(np.int32), c_float, \
            ndpointer(np.float32), ndpointer(np.float32), ndpointer(np.float32), \
            ndpointer(np.float32), ndpointer(np.float32), ndpointer(np.float32), c_float, c_float,\
            ndpointer(np.uint16)]
        testarrs = np.zeros(2, dtype=np.int32)
        testarrs[0]= 32
        testarrs[1]= 48
        self.CalcTheta.testPyth (testarrs, 2)
        self.eqprox = [0.,0.]
        self.eqproxfine = [0.,0.]

    def setTopLevel (self, a):
        self.topLevel = a

    def getdist(self):
        return self.dist

    def setdist(self, d):
        self.dist = d

    def getwavelength(self):
        return self.wavelength

    def setwavelength(self, d):
        self.wavelengtht = d

    def gettiltom(self):
        return self.tiltom

    def settiltom(self, d):
        self.tiltom = d

    def gettiltch(self):
        return self.tiltch

    def settiltch(self, d):
        self.tiltch = d

    def getttheta(self):
        return self.ttheta

    def setttheta(self, d):
        self.ttheta = d

    def gettwist(self):
        return self.twist

    def settwist(self, d):
        self.ttwist = d

    def getbeamXY(self):
        return [self.beamx, self.beamy]

    def setbeamXY(self, xy):
        self.beamx = xy[0]
        self.beamy = xy[1]

    def getpsizeXY(self):
        return [self.psizex, self.psizey]

    def setpsizeXY(self, xy):
        self.psizex = xy[0]
        self.psizey = xy[1]

    def getnopixXY(self):
        return [self.nopixx, self.nopixy]

    def setnopixXY(self, xy):
        self.nopixx = xy[0]
        self.nopixy = xy[1]

    def write_to_file(self, filename):
        pickle.dump(self, open(filename, "wb"))

    def read_from_file(self, filename):
        a = pickle.load(open(filename, "rb"))
        self.dist = a.dist
        self.beamx = a.beamx
        self.beamy = a.beamy
        self.psizex = a.psizex
        self.psizey = a.psizey
        self.nopixx = a.nopixx
        self.nopixy = a.nopixy
        self.twist = a.twist
        self.tiltom = a.tiltom
        self.tiltch = a.tiltch
        self.ttheta = a.ttheta
        self.wavelength = a.wavelength

    def read_from_text_file(self, filename):
        fil = open(filename, 'r')
        flist = []
        linebreak = '\n'
        for fline in fil:
            flist.append(fline.replace(linebreak, ""))

        self.psizex = float(flist[0])
        self.psizey = float(flist[1])
        self.dist = float(flist[2])
        self.wavelength = float(flist[3])
        self.beamx = float(flist[4])
        self.beamy = float(flist[5])
        self.tiltom = float(flist[6])
        self.tiltch = float(flist[7])
        if (len (flist) > 8) :
		    self.angle = float(flist[8])
        else :
            self.angle = 0.
        if (len(flist) > 9) :
			self.alpha = float(flist[8])
        else :
            self.alpha = 0.




    def write_to_text_file(self, filename):
        if (len(filename)< 1) :
            return
        fil = open(filename, 'w')
        fil.write(str(self.psizex) + '\n')
        fil.write(str(self.psizey) + '\n')
        fil.write(str(self.dist) + '\n')
        fil.write(str(self.wavelength) + '\n')
        fil.write(str(self.beamx) + '\n')
        fil.write(str(self.beamy) + '\n')
        fil.write(str(self.tiltom) + '\n')
        fil.write(str(self.tiltch) + '\n')
        fil.write(str(self.angle) + '\n')
        fil.write(str(self.alpha) + '\n')
        fil.close()

    def calculate_tth_from_pixels(self, pix, gonio):
        sd = self.calculate_sd_from_pixels(pix, gonio)
        sd0 = [1, 0, 0]
        ang = ang_between_vecs (sd, sd0)
        return ang

    def calculate_pixels_from_sd(self, sd, gonio):
        vec1 = [1.,0.,0]
        vec2 = [1.,0.,0]
        vec3 = [1.,0.,0]
        sd2 = [1.,0.,0]
        pix = [0.,0]

        sd2 = sd / vlength(sd)

        tth = generate_rot_mat (3,gonio[1])
        sd1 = np.dot(sd2, tth)

        #calculate the Bragg angle
        tth = ang_between_vecs (sd1, vec3)

        #calc det normal and apply tilts
        det = np.asarray([-1,0.,0.])
        omt = generate_rot_mat(2, -self.tiltch)
        iomt = np.linalg.inv(omt)
        cht = generate_rot_mat(1, self.tiltom)
        icht = np.linalg.inv(cht)

        mtx = self.tilt_mtx()
        imtx = np.linalg.inv(mtx)
        det1 = np.dot(det,mtx)
        dv = line_plane_intersection (sd1, det1, [0.,0.,0.],[self.dist,0.,0.])
        dv1 = dv + det * self.dist
        dvi = np.dot (dv1,imtx)

        pix[0]=-dv[1]/self.psizex + self.beamx
        pix[1]=dv[2]/self.psizey + self.beamy

        #apply twist
        va = np.asarray([0.0,0.,0.])
        va[1]=pix[0]-self.nopixx/2.
        va[2]=pix[1]-self.nopixy/2.

        chiA = generate_rot_mat(1, self.angle)
        vb = np.dot(va,chiA)
        pix[0] = vb[0,1]+self.nopixx/2.
        pix[1] = vb[0,2]+self.nopixy/2.
        #pix = [vb[1]+self.nopixx/2, vb[2]+self.nopixy/2.]
        return pix





    def calculate_sd_from_pixels(self, pix, gonio):
        xpix = pix[0]
        ypix = pix[1]

        # calculate relative coordinates
        xrel = -1. * (xpix - self.beamx) * self.psizex
        yrel = (ypix - self.beamy) * self.psizey

        vec1 = np.asarray([0.,0.,0.])
        vec2 = np.asarray([0.,0.,0.])
        vec3 = np.asarray([0.,0.,0.])

        va= np.asarray([0., xpix-self.nopixx/2., ypix-self.nopixy/2.])

        chiA = generate_rot_mat (1, -self.angle)
        vb = np.dot(va, chiA)
        vb[0,1]=vb[0,1]+self.nopixx/2.
        vb[0,2]=vb[0,2]+self.nopixy/2.

        xrel =-(vb[0,1]-self.beamx)*self.psizex
        yrel=(vb[0,2]-self.beamy)*self.psizey





        # sd at 2theta 0
        vec1a = np.asarray([0.,xrel, yrel])
        Vec1 = vec1a

        vec1a = np.asmatrix(vec1a)
        vec2 = np.dot(vec1a, self.tilt_mtx())


        vec2a = np.asarray([self.dist, 0., 0.])
        vec3 = vec2 + vec2a
        vec2[0,0] += self.dist

        tth = generate_rot_mat (3, -gonio[1])

        vec3 = np.dot(vec3, tth)
        vec3 = vec3 / vlength(vec3)
        sd = np.transpose (vec3)
        #sd0 = vec3 / vlength(vec3)

        return sd

    def calculate_sd_from_pixels_arr(self, pix, gonio):
        xpix = pix[0]
        ypix = pix[1]


        # calculate relative coordinates
        xrel = -1. * (xpix - self.beamx) * self.psizex
        yrel = (ypix - self.beamy) * self.psizey

        # sd at 2theta 0
        vec1a = np.array([0.,xrel, yrel])

        #vec1a = np.asmatrix(vec1a)
        vec2 = np.dot(vec1a,self.tiltmtx)


        #vec2a = [self.dist, 0., 0.]
        #vec3 = vec2 + np.asmatrix(vec2a)
        vec2[0] += self.dist
        #tth = generate_rot_mat (3, -gonio[1])
        vec3 = np.dot(vec2,self.tth)
        #vec3 = np.asarray(vec3)
        #sd0 = vec3 / vlength(vec3)

        return vec3


    def tilt_mtx (self) :
        omt = generate_rot_mat (3, self.tiltch)
        cht = generate_rot_mat (1, self.tiltom)
        icht = np.linalg.inv (cht)
        tiltmtx = cht * omt * icht
        return tiltmtx

    def genTiltMtx (self) :
        omt = generate_rot_mat (3, self.tiltch)
        cht = generate_rot_mat (1, self.tiltom)
        icht = np.linalg.inv (cht)
        self.tiltmtx = np.asarray(cht * omt * icht)
        self.tth = np.asarray(generate_rot_mat (3, -self.gonio[1]))

    """ Go through the array of image size calculating the 2theta based upon detector parameters
    """
    def calc2theta (self, saveFlag) :
        #self.tiltch = -30
        self.tiltom = 40.
        self.genTiltMtx()
        self.calcTthDLL ()
        # get the file name if we are saving 2theta to array
        if saveFlag :
            outFile = QtGui.QFileDialog.getSaveFileName (None, "Output to Tiff", "",'Tiff File (*.tif)')
            outfl = outFile.toLatin1().data()
            tifffile.imsave (outfl, self.tthetaArr)
            #self.tthetaArr.tofile (outfl)
        self.tDoneAll.emit()


    def testStuff (self) :
        self.genTiltMtx ()
        self.calcTthDLL ()
        return

        for i in range (8) :
            self.threadDone[i] = False
        t0= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,0,0, 0))
        t1= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,0,512, 1))
        t2= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,0,1024, 2))
        t3= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,0,1536, 3))
        t4= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,1024,0, 4))
        t5= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,1024,512,5))
        t6= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,1024, 1024,6))
        t7= Thread (target=self.create_ttheta_array_sub, args=(2048,2048,1024, 1536,7))
        t0.start()
        #t1.start()
        #t2.start()
        #t3.start()
        #t4.start()
        #t5.start()
        #t6.start()
        #t7.start()


        tth0 = self.calculate_tth_from_pixels ([0, 1024], [0,0,0])
        tth1 = self.calculate_tth_from_pixels ([2047, 1024], [0,0,0])
        tth2 = self.calculate_tth_from_pixels ([1024, 0], [0,0,0])
        tth3 = self.calculate_tth_from_pixels ([1024, 2047], [0,0,0])
        print tth0, tth1, tth2, tth3


    def create_ttheta_array (self, xysize) :
        self.genTiltMtx ()
        self.tthetaArr = np.zeros(xysize, dtype=np.float32)
        x2 = xysize[1] / 2
        y2 = xysize[0] / 2
        sd0 = [1, 0, 0]
        outdist = y2
        npix = long(xysize[0]) * xysize[1]
        for i in range (xysize[0]) :
            if i %50 == 0 :
                print "Working on line %d"%i
            for j in range(xysize[1]) :
                dist = sqrt(float ((i-y2)**2+(j-x2)**2))
                if (dist>outdist) :
                    continue
                #self.tthetaArr [i, j] = self.calculate_tth_from_pixels ([j, i], self.gonio)
                #sd = self.calculate_sd_from_pixels_arr([j,i], self.gonio)
                xrel = -1. * (j - self.beamx) * self.psizex
                yrel = (i - self.beamy) * self.psizey
                vec1a = np.array([0.,xrel, yrel])

                #vec1a = np.asmatrix(vec1a)
                vec2 = np.dot(vec1a,self.tiltmtx)


                #vec2a = [self.dist, 0., 0.]
                #vec3 = vec2 + np.asmatrix(vec2a)
                vec2[0] += self.dist
                #tth = generate_rot_mat (3, -gonio[1])
                vec3 = np.dot(vec2,self.tth)

                self.tthetaArr[i,j] = ang (vec3, sd0)

        #f = open ("/home/harold/ttheta", 'w')
        #self.tthetaArr.tofile (f)
        #f.close()

    def create_ttheta_array_sub (self, ysize, xsize, starty, startx, tnum) :
        self.genTiltMtx ()

        xysize = [ysize,xsize]
        x2 = xysize[1] / 2
        y2 = xysize[0] / 2
        sd0 = [1, 0, 0]
        outdist = y2
        npix = long(xysize[0]) * xysize[1]
        for i in range (starty, starty+1024) :
            if i %50 == 0 :
                print "Working on line %d"%i
            for j in range (startx, startx+512) :
                dist = sqrt(float ((i-y2)**2+(j-x2)**2))
                if (dist>outdist) :
                    continue
                #self.tthetaArr [i, j] = self.calculate_tth_from_pixels ([j, i], self.gonio)
                #sd = self.calculate_sd_from_pixels_arr([j,i], self.gonio)
                xrel = -1. * (j - self.beamx) * self.psizex
                yrel = (i - self.beamy) * self.psizey
                vec1a = np.array([0.,xrel, yrel])

                #vec1a = np.asmatrix(vec1a)
                vec2 = np.dot(vec1a,self.tiltmtx)

                #vec2a = [self.dist, 0., 0.]
                #vec3 = vec2 + np.asmatrix(vec2a)
                vec2[0] += self.dist
                #tth = generate_rot_mat (3, -gonio[1])
                vec3 = np.dot(vec2,self.tth)

                self.tthetaArr[i,j] = ang (vec3, sd0)

        self.threadDone[tnum] = True
        self.tDone.emit (tnum)

    def calcTthDLL (self) :
        psz = np.zeros (2, dtype=np.float32)
        imsz = np.zeros (2, dtype=np.int32)
        beamsz = np.zeros (2, dtype=np.float32)
        psz[0]=self.psizex
        psz[1]=self.psizey


        imsz[0]=2048
        imsz[1]=2048
        beamsz[0] = self.beamx
        beamsz[1] = self.beamy
        self.genTiltMtx()
        self.CalcTheta.create_theta_array (imsz, self.dist, beamsz, psz, self.tiltmtx.reshape(9).astype(np.float32), self.tth.reshape(9).astype(np.float32),\
            np.asarray(self.gonio).astype(np.float32), self.tthetaArr, 0., 0., self.tthetaBin)
        #f = open ("/home/harold/ttheta", 'w')
        #self.tthetaArr.tofile (f)
        #f.close()


    def generate_peaks_laue (self, ub, optable, pred, en, exti, DAC_open):

        gonio = [0.,0.,0.,0.,0.,0.]
        for h in range(pred.h1,pred.h2+1) :
            for k in range (pred.k1, pred.k2+1) :
                for l in range (pred.l1, pred.l2+1) :
                    if (h==0 and k==0 and l==0) :
                        continue

                    hkl =np.asarray([h, k, l])
                    if (syst_extinction (exti, hkl)==1) :
                        xyz = np.dot (ub, hkl)
                        if (vlength(xyz) >0.0000001) :
                            #print 'hkl is : ', h,k,l
                            Ene = en_from_xyz(xyz)
                            if (Ene > en[0] and Ene <= en[1]) :
                                pix = np.asarray(self.calculate_pixels_from_xyz (xyz, gonio))
                                r = pix - np.asarray([self.beamx, self.beamy])
                                r = sqrt(r[0]**2+r[1]**2)
                                psi2 = self.calculate_psi_angles (gonio, pix)
                                if pix[0] > 0 and pix[0] < self.nopixx-1 and \
                                pix[1]>0 and pix[1] < self.nopixy -1 and abs(psi2[0,1]) < DAC_open :
                                    refpeak = myPeakTable.myPeak()
                                    refpeak.DetXY = pix
                                    refpeak.gonio = gonio
                                    refpeak.XYZ = xyz
                                    refpeak.energies[0] =Ene
                                    refpeak.hkl = hkl
                                    optable.addPeak (refpeak)








    def calcTthDLL (self) :
        psz = np.zeros (2, dtype=np.float32)
        imsz = np.zeros (2, dtype=np.int32)
        beamsz = np.zeros (2, dtype=np.float32)
        psz[0]=self.psizex
        psz[1]=self.psizey


        imsz[0]=2048
        imsz[1]=2048
        beamsz[0] = self.beamx
        beamsz[1] = self.beamy
        self.genTiltMtx()
        self.CalcTheta.create_theta_array (imsz, self.dist, beamsz, psz, self.tiltmtx.reshape(9).astype(np.float32), self.tth.reshape(9).astype(np.float32),\
            np.asarray(self.gonio).astype(np.float32), self.tthetaArr, 0., 0., self.tthetaBin)


    def threadDoneSlot (self, tnum) :
        for i in range (8) :
            if self.threadDone[i] == False :
                done = False
                return

        print "TTheta calculation complete - writing output file"

    def calculate_pixels_from_xyz(self, xyz, gonio):
        sd =[0.,0.,0.]
        pix=[0.,0.]
        xyz1= xyz/vlength(xyz)

        al=generate_rot_mat( 2, self.alpha)
        #al= Mtx
        om=generate_rot_mat(3, gonio[3])
        #om=Mtx
        ch=generate_rot_mat( 1, gonio[4])

        ial = np.linalg.inv(al)
        iom = np.linalg.inv(om)
        ich = np.linalg.inv(ch)

        hl0 = np.dot(iom,ial)
        hl1 = np.dot (al, hl0)
        hl2 = np.dot (ich, hl1)
        hl = np.dot (xyz1, hl2)

        sd = self.calculate_sd_from_hl(hl)
        pix = self.calculate_pixels_from_sd (sd, self.gonio)
        return pix



# def thetaCalcThread (det, starts, stops):

    def generateRotMatrix (self, axisnumber, angle):
        Mtx = np.zeros ((3,3),dtype=np.float32)
        s = math.radians(angle)
        if (axisnumber ==1):
            Mtx[0,0] =1.
            Mtx[1,1]=math.cos(s)
            Mtx[1,2]=-math.sin(s)
            Mtx[2,1]=math.sin(s)
            Mtx[2,2]=math.cos(s)
            return Mtx
        if (axisnumber ==2) :
            Mtx[1,1]=1.
            Mtx[0,0]=math.cos(s)
            Mtx[0,2]=math.sin(s)
            Mtx[2,0]=-math.sin(s)
            Mtx[2,2]=math.cos(s)
            return Mtx
        if (axisnumber ==3) :
            Mtx[2,2]=1.
            Mtx[0,0]=math.cos(s)
            Mtx[0,1]=math.sin(s)
            Mtx[1,0]=-math.sin(s)
            Mtx[1,1]=math.cos(s)
            return Mtx

    @staticmethod
    def calculate_sd_from_hl ( hl):
        hl= hl/vlength(hl)
        s0 = [1.,0.,0]
        s0 = np.asarray(s0)
        al = ang_between_vecs(hl,s0)
        if (al < 90.) :
            hl = -hl
            al = ang_between_vecs(hl,s0)
            om = 90.-al
        om = al -90
        tth = om * 2
        hle = math.sin(math.radians(tth))/math.cos(math.radians(om))
        h = hl*hle
        sd = s0+h
        return sd

    def calculate_psi_angles (self, gonio, pix) :
        nn = len(pix)/2
        pix = np.asarray (pix).reshape(2)
        gonio = np.asarray(gonio).reshape(6)
        y = np.zeros((nn,2), dtype=np.float32)
        for i in range (nn ) :
            psi1 = gonio[3]
            e1 = np.asarray([1,0.,0.])
            mtx = generate_rot_mat(3,-gonio[3])
            e1 = np.dot(e1,mtx)
            sd = self.calculate_sd_from_pixels (pix[:], gonio[:])
            ang0 = ang_between_vecs(sd,e1)
            ang1 = ang_between_vecs(sd,-1.*e1)
            psi2 = min (ang0, ang1)
            y[i,:]=[psi1,psi2]
        return y

    def generate_all_peaks (self, ub, pktable, wv, pred, exti, dac_open, box):
        pktable.zero()
        kt = self.read_kappa_and_ttheta()
        gonio = np.zeros(6, dtype=np.float32)
        # 2theta
        gonio[1] = kt[1]
        # kappa/chi
        gonio[4] = pred.chi
        boxval = self.topLevel.read_box_change()
        refpeak = myPeakTable.myPeak()
        refpeak.IntSSD[0:2]=[boxval, boxval]
        for h in range (pred.h1, pred.h2+1) :
            for k in range (pred.k1, pred.k2+1) :
                for l in range (pred.l1, pred.l2+1) :
                    hkl = [h,k,l]
                    extinct = syst_extinction (exti, hkl)
                    if extinct == 1 :
                        xyz = np.dot (hkl,ub)
                        om = get_omega(A_to_kev(wv), xyz)
                        #om = solve_general_axis (A_to_kev(wv), xyz, gonio)
                        om0 = om[0]
                        if om0 >= pred.om_start and om0 <= pred.om_start + pred.om_range :
                            gonio[3] = om0
                            pix = self.calculate_pixels_from_xyz(xyz, gonio)
                            r = [pix[0]-self.beamx, pix[1]-self.beamy]
                            r = math.sqrt (r[0]**2+r[1]**2)
                            psi2 = self.calculate_psi_angles(gonio, pix)
                            print pix[0], psi2[0][1]
                            if (pix[0]>0 and pix[0] < self.nopixx-1 and abs(psi2[0,1]< dac_open)) :
                                refpeak.setDetxy (pix)
                                refpeak.gonio = gonio
                                refpeak.xyz = xyz
                                refpeak.hkl = hkl
                                refpeak.IntSSD[0:2] = [box[0], box[0]]
                                pktable.appendPeak (refpeak)



    def read_kappa_and_ttheta(self) :
        a=np.zeros(2,dtype=np.float32)
        theta = self.topLevel.ui.LE_Detector_2theta.text().toFloat()[0]
        kappa = self.topLevel.ui.LE_Detector_kappa.text().toFloat()[0]
        a[0] = theta
        a[1] = kappa
        return a


    ## refineCalibration
    # function called when Detector -> Refine calibration button
    # is clicked.
    # @param - myImage as displayed calibration image is used for input
    def refineCalibration (self, myim) :
        re = 1
        #check button later
        #re = self.which_calibration (self)
        # check if powder or solid, if powder re = 1
        if (re == 1) :
            self.testCalibration_esd (myim)

    def testCalibration_esd (self, myim) :
        esd = np.zeros(9, dtype=np.float32)
        en = A_to_kev (self.wavelength)
        cut = 30.
        dist_tol = 1.8
        IovS = self.topLevel.ui.det_snrLE.text().toFloat()[0]
        start_dist = self.dist - self.dist * 0.5
        end_dist = self.dist + self.dist *.5
        im = myim.imArray.astype(np.int64)
        imarr = cgd.congrid (im, [500, 500], method='nearest',minusone=True).astype(np.int64)
        zarr = np.zeros ((500,500),dtype=np.uint8)

        bg = self.local_background (imarr)
        imarr.tofile ("/home/harold/imarr.dat")
        # only for debug

        hpf = imarr / bg.astype(np.int64)

        self.ff = np.where ((hpf > IovS) & (imarr>20.))

        nn = len(self.ff[0])
        print 'number of pixels meeting the peak condition is %d'%(nn)


        ### equal proximity coarse search
        # in 5 pixel steps
        h = np.zeros((100,100), dtype=np.float32)
        for i in range (100) :
            print i
            for j in range (100) :
                dist = self.compdist (self.ff, [i*5,j*5])
                mx = int(dist.max())+1
                mn = int(dist.min())

                #nbins = int(dist.max() - dist.min()+1)
                histo,edges = np.histogram(dist, range=[mn,mx],bins=(mx-mn))
                h[i,j] = np.max (histo)
        maxsub = np.argmax(h)
        maxrow = maxsub / 100
        maxcol = maxsub - maxrow * 100
        print maxsub, maxrow, maxcol

        self.eqprox[0]=maxrow/100.
        self.eqprox[1]=maxcol/100.

        # is this even being used
        dist = self.compdist (self.ff, [maxrow, maxcol])
        nbins = int (dist.max()-dist.min()+1)
        h = np.histogram(dist, bins=nbins)

        ### equal proximity seach fine (in 500 space)
        h = np.zeros((11,11),dtype=np.float32)
        for i in range (-5,6) :
            for j in range(-5,6) :
                # note in gse_ada , there is a 5 + in the index calculation
                dist = self.compdist(self.ff, [5.*maxrow+i, 5.*maxcol+j])
                nbins = int(dist.max() - dist.min() +1)
                mx = int(dist.max()+1)
                mn = int(dist.min())
                histo, edges = np.histogram(dist, range=[mn,mx],bins=mx-mn)
                h[i+5][j+5]=np.max(histo)
        maxsub = np.argmax (h)

        # then back in 100 space
        xy = self.xy_from_ind (11,11,maxsub)
        maxrow = maxrow + (xy[0] - 5)/5.
        maxcol = maxcol + (xy[1] - 5) / 5.
        xy0 = [maxrow, maxcol]
        self.eqproxfine[0]=maxrow/100.
        self.eqproxfine[1]=maxcol/100.

        self.beamx = xy0[0]/100. * self.nopixx
        self.beamy = xy0[1]/100. * self.nopixy
        xy0[0]*=5.
        xy0[1]*=5.
        dist = self.compdist (self.ff, xy0)
        mn = int(dist.min())
        mx = int(dist.max()+1)
        nbins = mx-mn
        h,edges = np.histogram (dist, range=[mn,mx],bins=nbins)
        h1 = np.copy(h)
        #h = h[0]
        numH = len(h)

        while (np.max(h1)>cut) :
            i = np.argmax (h1)
            m = np.max(h1)
            h1[i] = 0.
            if (i > 0 and i < numH-1) :
                j = i - 1
                while (j >= 0) :
                    if (h1[j] > cut/2.) :
                        h[i] += h[j]
                        h[j] =0.
                        h1[j]=0.
                    else :
                        j = 0
                    j=j-1

                j=i+1
                while (j <= numH-1) :
                    if (h1[j]>cut/2.) :
                        h[i]+=h[j]
                        h[j]=0
                        h1[j]=0
                    else :
                        j=numH-1
                    j=j+1
        # NOTE - should be cut not cut/2.
        fh = np.where (h > cut)[0]
        numB = len(fh)
        # number of different rings with sufficient number of points
        rings = np.zeros(nn, dtype=np.int64)
        for i in range (nn) :
            c = np.absolute (np.subtract(dist[i],edges[fh]))
            ri = np.min (c)
            kk = np.argmin (c)
            if (ri < dist_tol) :
                rings[i] = kk
            else :
                rings[i] = -1


        nr = np.zeros(numB, dtype=np.int64)
        ds = np.zeros (numB, dtype=np.float32)
        for k in range (numB) :
            r = np.where(rings == k)[0]
            nr[k]= len(r)
        print "Classes Done ...\r\n"
        m = np.max(nr)
        print 'Max of nr is : %d'%(m)

        # x,y coords of points in ring
        self.rgx = np.zeros((numB,m), dtype=np.float32)
        self.rgy = np.zeros((numB,m), dtype=np.float32)
        self.rgN = np.zeros (numB,dtype=np.uint16)

        self.numRings = numB
        for k in range (numB) :
            r = np.where (rings == k)[0]
            ds[k] = np.mean(dist[r])*self.nopixx/500. * self.psizex
            print 'ds of %d is : %f'%(k, ds[k])
            # xya=self.xy_from_indArr (500,500,self.ff[r])
            self.rgy[k,0:nr[k]] = self.ff[0][r]
            self.rgx[k,0:nr[k]] = self.ff[1][r]
            self.rgN[k] = len(r)

        step = (end_dist - start_dist) / 1000.
        ddists = np.zeros((2,1000), dtype = np.float32)
        for i in range (1000) :
            thisstep = start_dist + i * step
            ddists[0][i] = thisstep
            ddists[1][i] = self.sum_closest_refs (ds, thisstep)
        aa=np.argmin (ddists[1][:])
        dst = ddists[0][aa]

        print 'Coarse estimated detector distance : %f'%(dst)


        # fine tune detector distance
        start_dist = dst- step*5.
        end_dist = dst + step * 5.
        step = (end_dist-start_dist) / 1000.
        for i in range (1000):
            ddists[0][i] = start_dist + i * step
            ddists[1][i] = self.sum_closest_refs (ds, ddists[0][i])
        aa=np.argmin (ddists[1][:])
        dst = ddists[0][aa]
        print 'Refined estimated detector distance : %f'%(dst)


        # use only peaks which match standard and are unique
        cr = np.zeros ((2,numB), dtype=np.float32)
        omissions = np.zeros (numB, dtype=np.int32)
        for i in range (numB) :
            cr[0][i]= self.closest_ref (ds[i], dst)
            cr[1][i]= self.closest_ref_d(ds[i], dst)
            if (cr[0][i] > .2) :
                omissions[i] = 1

        rrr=0
        X = self.rgx[0][0:nr[0]]*self.nopixx/500.
        Y = self.rgy[0][0:nr[0]]*self.nopixx/500.
        Z = np.zeros(nr[0],dtype=np.float32)
        crval = cr[1][0]
        dspcc = np.ones(nr[0]) * crval
        nus = np.zeros(nr[0],dtype=np.float32)
        tths = np.zeros(nr[0],dtype=np.float32)
        tthval = tth_from_en_and_d (en, crval)
        tths = np.ones (nr[0])*tthval

        for rrr in range (1, numB) :
            if (omissions[rrr]==0) :
                pos = len (X)
                X=np.concatenate ((X, self.rgx[rrr][0:nr[rrr]]))
                Y=np.concatenate ((Y, self.rgy[rrr][0:nr[rrr]]))
                crval = cr[1][rrr]
                newcr = np.ones(nr[rrr],dtype=np.float32)*crval
                dspcc = np.concatenate ((dspcc, newcr))
                tt = np.zeros(nr[rrr], dtype=np.float32)
                nu = np.zeros(nr[rrr], dtype=np.float32)
                tths = np.concatenate ((tths, tt))
                nus=np.concatenate ((nus, nu))
                newlen = pos+nr[rrr]
                print 'RRR is ', rrr
                for i in range (pos, pos+nr[rrr]) :
                    print i

                    tths [i] = tth_from_en_and_d (en, dspcc[i])
                    nus[i]=self.get_nu_from_pix([X[i],Y[i]])

        p = np.zeros(6,dtype=np.float32)
        p[0] = self.dist
        p[1] = self.beamx
        p[2] = self.beamy
        print 'Starting calibration refinement'

        pars = {'value':0.,'fixed':0,'limited':[0,0],'limits':[0.,0]}
        parinfo = []
        for i in range (6) :
            parinfo.append (pars.copy())

        NNN = len(X)
        arr1 = self.nopixx
        arr2 = self.nopixy
        imdat = myim.imArray
        for i in range (NNN) :
            if not (X[i]<5 or X[i] > (arr1 - 6) or Y[i] < 5 or Y[i] > (arr2-6))  :
                if (imdat[X[i],Y[i]]< imdat[X[i]-1,Y[i]]):
                    X[i] = X[i]-1
                if (imdat[X[i],Y[i]]< imdat[X[i]+1,Y[i]]):
                    X[i] = X[i]+1
                if (imdat[X[i],Y[i]]< imdat[X[i],Y[i]-1]):
                    Y[i] = Y[i]-1
                if (imdat[X[i],Y[i]]< imdat[X[i],Y[i]+1]):
                    Y[i] = Y[i]+1

                if (imdat[X[i],Y[i]]< imdat[X[i]-1,Y[i]]):
                    X[i] = X[i]-1
                if (imdat[X[i],Y[i]]< imdat[X[i]+1,Y[i]]):
                    X[i] = X[i]+1
                if (imdat[X[i],Y[i]]< imdat[X[i],Y[i]-1]):
                    Y[i] = Y[i]-1
                if (imdat[X[i],Y[i]]< imdat[X[i],Y[i]+1]):
                    Y[i] = Y[i]+1

                if (imdat[X[i],Y[i]]< imdat[X[i]-1,Y[i]]):
                    X[i] = X[i]-1
                if (imdat[X[i],Y[i]]< imdat[X[i]+1,Y[i]]):
                    X[i] = X[i]+1
                if (imdat[X[i],Y[i]]< imdat[X[i],Y[i]-1]):
                    Y[i] = Y[i]-1
                if (imdat[X[i],Y[i]]< imdat[X[i],Y[i]+1]):
                    Y[i] = Y[i]+1

            if not (X[i]<5 or X[i] > (arr1 - 6) or Y[i] < 5 or Y[i] > (arr2-6))  :
                xxx = np.arange(-5,6,1)
                a=np.zeros(3, dtype=np.float32)
                nus[i]= self.get_nu_from_pix((X[i],Y[i]))
                if (nus[i]>45. and nus[i]<135.):
                    ix = int (round(X[i],0))
                    iy = int (round(Y[i],0))
                    sec = myim.imArray[iy,ix-5:ix+6]
                    a[0] = np.max(sec)-np.min(sec)
                    a[1]= 0
                    a[2] =2
                    #res = gaussfit (sec, xxx, a, nterms=4)
                    res =  gaussfit1d(xxx, sec, a)
                    #print res
                else :
                    ix = int (round(X[i],0))
                    iy = int (round(Y[i],0))
                    sec = myim.imArray[iy-5:iy+6,ix]

                    #res = gaussfit (sec, xxx, a, nterms=4)
                    #res =  gauss_lsq(xxx, sec)
                    a[0] = np.max(sec)-np.min(sec)
                    a[1]= 0
                    a[2] =2
                    res =  gaussfit1d(xxx, sec, a)
                    #print res
        er = 1./dspcc
        Z = np.zeros (NNN, dtype=np.float32)
        parinfo[:].value = [P]


        self.calPeaks.emit()



    ## testCalibration
    # function called when Detector -> Test calibration button
    # is clicked.
    # @param - myImage as displayed calibration image is used for input
    def testCalibration (self, myim) :
    #def detector_calibration_test_points (self) :
        en = 37.077
        cut = 30.
        dist_tol = 1.8
        IovS = self.topLevel.ui.det_snrLE.text().toFloat()[0]
        start_dist = self.dist - self.dist * 0.5
        end_dist = self.dist + self.dist *.5
        im = myim.imArray.astype(np.int64)
        imarr = cgd.congrid (im, [500, 500], method='nearest',minusone=True).astype(np.int64)
        zarr = np.zeros ((500,500),dtype=np.uint8)

        bg = self.local_background (imarr)
        imarr.tofile ("/home/harold/imarr.dat")
        # only for debug

        hpf = imarr / bg.astype(np.int64)

        self.ff = np.where ((hpf > IovS) & (imarr>20.))

        nn = len(self.ff[0])
        print 'number of pixels meeting the peak condition is %d'%(nn)


        ### equal proximity coarse search
        # in 5 pixel steps
        h = np.zeros((100,100), dtype=np.float32)
        for i in range (100) :
            print i
            for j in range (100) :
                dist = self.compdist (self.ff, [i*5,j*5])
                mx = int(dist.max())+1
                mn = int(dist.min())

                #nbins = int(dist.max() - dist.min()+1)
                histo,edges = np.histogram(dist, range=[mn,mx],bins=(mx-mn))
                h[i,j] = np.max (histo)
        maxsub = np.argmax(h)
        maxrow = maxsub / 100
        maxcol = maxsub - maxrow * 100
        print maxsub, maxrow, maxcol

        self.eqprox[0]=maxrow/100.
        self.eqprox[1]=maxcol/100.

        # is this even being used
        dist = self.compdist (self.ff, [maxrow, maxcol])
        nbins = int (dist.max()-dist.min()+1)
        h = np.histogram(dist, bins=nbins)

        ### equal proximity seach fine (in 500 space)
        h = np.zeros((11,11),dtype=np.float32)
        for i in range (-5,6) :
            for j in range(-5,6) :
                # note in gse_ada , there is a 5 + in the index calculation
                dist = self.compdist(self.ff, [5.*maxrow+i, 5.*maxcol+j])
                nbins = int(dist.max() - dist.min() +1)
                mx = int(dist.max()+1)
                mn = int(dist.min())
                histo, edges = np.histogram(dist, range=[mn,mx],bins=mx-mn)
                h[i+5][j+5]=np.max(histo)
        maxsub = np.argmax (h)

        # then back in 100 space
        xy = self.xy_from_ind (11,11,maxsub)
        maxrow = maxrow + (xy[0] - 5)/5.
        maxcol = maxcol + (xy[1] - 5)/5.
        xy0 = [maxrow, maxcol]
        self.eqproxfine[0]=maxrow/100.
        self.eqproxfine[1]=maxcol/100.

        self.beamx = xy0[0]/100. * self.nopixx
        self.beamy = xy0[1]/100. * self.nopixy
        xy0[0]*=5.
        xy0[1]*=5.
        dist = self.compdist (self.ff, xy0)
        mn = int(dist.min())
        mx = int(dist.max()+1)
        nbins = mx-mn
        h,edges = np.histogram (dist, range=[mn,mx],bins=nbins)
        h1 = np.copy(h)
        #h = h[0]
        numH = len(h)

        while (np.max(h1)>cut) :
            i = np.argmax (h1)
            m = np.max(h1)
            h1[i] = 0.
            if (i > 0 and i < numH-1) :
                j = i - 1
                while (j >= 0) :
                    if (h1[j] > cut/2.) :
                        h[i] += h[j]
                        h[j] =0.
                        h1[j]=0.
                    else :
                        j = 0
                    j=j-1

                j=i+1
                while (j <= numH-1) :
                    if (h1[j]>cut/2.) :
                        h[i]+=h[j]
                        h[j]=0
                        h1[j]=0
                    else :
                        j=numH-1
                    j=j+1
        # NOTE - should be cut not cut/2.
        fh = np.where (h > cut)[0]
        numB = len(fh)
        # number of different rings with sufficient number of points
        rings = np.zeros(nn, dtype=np.int64)
        for i in range (nn) :
            c = np.absolute (np.subtract(dist[i],edges[fh]))
            ri = np.min (c)
            kk = np.argmin (c)
            if (ri < dist_tol) :
                rings[i] = kk
            else :
                rings[i] = -1


        nr = np.zeros(numB, dtype=np.int64)
        ds = np.zeros (numB, dtype=np.float32)
        for k in range (numB) :
            r = np.where(rings == k)[0]
            nr[k]= len(r)
        print "Classes Done ...\r\n"
        m = np.max(nr)
        print 'Max of nr is : %d'%(m)

        # x,y coords of points in ring
        self.rgx = np.zeros((numB,m), dtype=np.float32)
        self.rgy = np.zeros((numB,m), dtype=np.float32)
        self.rgN = np.zeros (numB,dtype=np.uint16)

        self.numRings = numB
        for k in range (numB) :
            r = np.where (rings == k)[0]
            ds[k] = np.mean(dist[r])*self.nopixx/500. * self.psizex
            print 'ds of %d is : %f'%(k, ds[k])
            #xya=self.xy_from_indArr(500,500,self.ff[r])
            self.rgy[k,0:nr[k]] = self.ff[0][r]/500.
            self.rgx[k,0:nr[k]] = self.ff[1][r]/500.
            self.rgN[k] = len(r)

        step = (end_dist - start_dist) / 1000.
        ddists = np.zeros((2,1000), dtype = np.float32)
        for i in range (1000) :
            thisstep = start_dist + i * step
            ddists[0][i] = thisstep
            ddists[1][i] = self.sum_closest_refs (ds, thisstep)
        aa=np.argmin (ddists[1][:])
        dst = ddists[0][aa]

        print 'Coarse estimated detector distance : %f'%(dst)


        # fine tune detector distance
        start_dist = dst- step*5.
        end_dist = dst + step * 5.
        step = (end_dist-start_dist) / 1000.
        for i in range (1000):
            ddists[0][i] = start_dist + i * step
            ddists[1][i] = self.sum_closest_refs (ds, ddists[0][i])
        aa=np.argmin (ddists[1][:])
        dst = ddists[0][aa]
        print 'Refined estimated detector distance : %f'%(dst)


        # use only peaks which match standard and are unique
        cr = np.zeros ((2,numB), dtype=np.float32)
        for i in range (numB) :
            cr[0][i]= self.closest_ref (ds[i], dst)
            cr[1][i]= self.closest_ref_d(ds[i], dst)

        X = self.rgx[0][0:nr[0]]*self.nopixx/500.
        Y = self.rgy[0][0:nr[0]]*self.nopixx/500.

        dspcc = np.ones(nr[0]) * cr[1][0]

        self.calPeaks.emit()

    def local_background (self, myarr) :
        # scale this to a 1000 by 1000 grid but return an array in original format
        # the returned array is the median on a 10x10 blocksize
        s = myarr.shape
        myarr0 = cgd.congrid (myarr, (1000, 1000) , method='nearest', minusone=True)
        #myarr0 = imresize(myarr, (1000,1000))
        n = int (math.sqrt(s[0]*s[1]))
        out=np.zeros(myarr0.shape,myarr0.dtype)
        for i in range (100) :
            for j in range (100) :
                box = myarr0[i*10:(i+1)*10, j*10:(j+1)*10]
                nz = np.where (box != 0)
                npts = len(nz[0])
                if (npts == 0) :
                    m = 1
                else :
                    m = np.median(box[nz[0],nz[1]])
                out[i*10:(i+1)*10, j*10:(j+1)*10]=m
        outnew = cgd.congrid (out, s, method='nearest', minusone=True)
        #outnew = imresize (out, s)
        return outnew

    def setRefineTwist(self, flag):
        self.refineTwistFlag = flag

    ###
    #compdist - function to return  something from the other
    # pos is two element vector
    # ff is array of tuples, being coords of calib marks
    # returns an npt array with each element being the distance of that
    # point from that specified by pos
    ###

    def compdist (self, ff, pos) :
        npts = len(ff[0])
        b = np.zeros (npts, dtype=np.float32)
        c = np.zeros ((2,npts),dtype=np.float32)
        c[0] = ff[0] - pos[0]
        c[1] = ff[1] - pos[1]

        b = np.sqrt(c[0]**2+c[1]**2)
        return b



    def xy_from_ind (self, nx, ny, ind) :
        y = ind / ny
        x = ind - y * ny
        return ((y,x))


    def xy_from_indArr (self,nx, ny, indArr):
        xys = np.zeros((len(indArr),2))
        count = 0
        for ia in indArr :
            a = self.xy_from_ind (nx, ny, ia)
            xys[count] = a

        return xys

    ##
    # get_nu_from_pix
    # method calculates the detector out of horiz. plane
    # angle for a reflection from the Cartesian
    # coordinates of reciprocal vector
    # @param pix is 2 element list , x, y
    # returns the angle
    def get_nu_from_pix (self, pix) :
        gonio = np.zeros(6, dtype=np.float32)
        nn = len (pix) / 2
        y = np.zeros(nn)
        for i in range (nn) :
            sd = self.calculate_sd_from_pixels(pix, gonio)
            sd[0] = 0
            nu = ang_between_vecs (sd, [0.,-1.,0.])
            y[i] = nu
            if (sd[2] >= 0.) :
                y[i]*= (-1.)
        return y



    def sum_closest_refs (self, rads, dst):
        n = len(rads)
        sum = 0.
        for i in range (n) :
            sum += self.closest_ref(rads[i], dst)
        return sum

    def closest_ref (self, rad, dst) :
        ref = self.which_calibrant (dst, 0)

        dr = np.min (np.absolute(ref-rad))
        return dr

    def closest_ref_d (self, rad, dst):
        ref = self.which_calibrant (dst, 0)
        ds = self.which_calibrant (dst,1)
        kk = np.argmin (np.absolute(ref - rad))
        return ds[kk]


    def setCalibrant (self, ind) :
        self.calibrant = ind

    def which_calibrant (self, dst, cflag) :

        if (self.calibrant == 0) :
            r = CeO2 (dst, cflag, self.wavelength)
            return r
        if (self.calibrant ==1) :
            r = LaB6 (dst, cflag, self.wavelength)
            return r
        if (self.calibrant ==2) :
            r = Neon (dst, cflag, self.wavelength)
            return r
        if (self.calibrant ==3) :
            r = CO2 (dst, cflag, self.wavelength)
            return r




    def radius_differences ( X,Y,P) :
        newdet = myDetector  ()
        newdet.dist = P[0]
        newdet.beamx = P[1]
        newdet.beamy = P[2]
        newdet.angle = P[3]
        newdet.tiltom = P[4]
        newdet.tiltch = P[5]
        n = len(X)
        rado = math.sqrt(((X-newdet.beamx))**2. +((Y-newdet.beamy))**2)*newdet.psizex
        pix = np.zeros ((2,n))
        pix[0,:]=X
        pix[1,:]=Y


