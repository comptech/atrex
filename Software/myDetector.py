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

import myPeakTable


class myDetector (QtCore.QObject):

    tDone = QtCore.pyqtSignal (int)
    tDoneAll = QtCore.pyqtSignal ()

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

        self.gonio = [0., 0., 0.]
        self.tthetaArr = np.zeros((2048,2048), dtype=np.float32)
        self.tthetaBin = np.zeros ((2048,2048), dtype=np.uint16)
        self.threadDone = [False, False, False, False, False, False, False, False]
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
        self.twist = float(flist[6])
        self.tiltom = float(flist[7])
        self.ttheta = float(flist[8])
        self.tiltch = float(flist[9])
        fil.close()


    def write_to_text_file(self, filename):
        fil = open(filename, 'w')
        fil.write(str(self.psizex) + '\n')
        fil.write(str(self.psizey) + '\n')
        fil.write(str(self.dist) + '\n')
        fil.write(str(self.wavelength) + '\n')
        fil.write(str(self.beamx) + '\n')
        fil.write(str(self.beamy) + '\n')
        fil.write(str(self.twist) + '\n')
        fil.write(str(self.tiltom) + '\n')
        fil.write(str(self.ttheta) + '\n')
        fil.write(str(self.tiltch) + '\n')
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
                                    refpeak.xyz = xyz
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
        kt = self.read_kappa_ttheta ()
        gonio = np.zeros(6, dtype=np.float32)
        # 2theta
        gonio[1] = kt[1]
        # kappa/chi
        gonio[4] = pred.chi
        a = self.read_box_change()

    def read_kappa_and_theta (self) :
        a=np.zeros(2,dtype=np.floatr32)
        return a