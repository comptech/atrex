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
        self.nopixx = 0
        self.nopixy = 0
        self.twist = 0.0
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

    def calculate_sd_from_pixels(self, pix, gonio):
        xpix = pix[0]
        ypix = pix[1]

        # calculate relative coordinates
        xrel = -1. * (xpix - self.beamx) * self.psizex
        yrel = (ypix - self.beamy) * self.psizey

        # sd at 2theta 0
        vec1a = [0.,xrel, yrel]

        vec1a = np.asmatrix(vec1a)
        vec2 = vec1a * self.tiltmtx


        #vec2a = [self.dist, 0., 0.]
        #vec3 = vec2 + np.asmatrix(vec2a)
        vec2[0,0] += self.dist
        #tth = generate_rot_mat (3, -gonio[1])
        vec3 = vec2 * self.tth
        vec3 = np.asarray(vec3)
        #sd0 = vec3 / vlength(vec3)

        return vec3

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

        f = open ("/home/harold/ttheta", 'w')
        self.tthetaArr.tofile (f)
        f.close()

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

    def threadDoneSlot (self, tnum) :
        for i in range (8) :
            if self.threadDone[i] == False :
                done = False
                return

        print "TTheta calculation complete - writing output file"

# def thetaCalcThread (det, starts, stops):
