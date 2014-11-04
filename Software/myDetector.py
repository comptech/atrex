import os
import pickle

class myDetector:

    def __init__(self):
        self.dist   = 0.0
        self.beamx  = 0.0
        self.beamy  = 0.0
        self.psizex = 0.0
        self.psizey = 0.0
        self.nopixx = 0
        self.nopixy = 0
        self.twist  = 0.0
        self.tiltom = 0.0
        self.tiltch = 0.0
        self.ttheta = 0.0
        self.wavelength = 0.0

    def getdist(self):
        return self.dist

    def setdist(self, d):
        self.dist=d

    def getwavelength(self):
        return self.wavelength

    def setwavelength(self, d):
        self.wavelengtht=d

    def gettiltom(self):
        return self.tiltom

    def settiltom(self, d):
        self.tiltom=d

    def gettiltch(self):
        return self.tiltch

    def settiltch(self, d):
        self.tiltch=d

    def getttheta(self):
        return self.ttheta

    def setttheta(self, d):
        self.ttheta=d

    def gettwist(self):
        return self.twist

    def settwist(self, d):
        self.ttwist=d

    def getbeamXY(self):
        return [self.beamx, self.beamy]

    def setbeamXY(self, xy):
        self.beamx=xy[0]
        self.beamy=xy[1]

    def getpsizeXY(self):
        return [self.psizex, self.psizey]

    def setpsizeXY(self, xy):
        self.psizex=xy[0]
        self.psizey=xy[1]

    def getnopixXY(self):
        return [self.nopixx, self.nopixy]

    def setnopixXY(self, xy):
        self.nopixx=xy[0]
        self.nopixy=xy[1]

    def write_to_file(self, filename):
        pickle.dump( self, open( filename, "wb" ))

    def read_from_file(self, filename):
        a=pickle.load( open( filename, "rb" ) )
        self.dist   = a.dist
        self.beamx  = a.beamx
        self.beamy  = a.beamy
        self.psizex = a.psizex
        self.psizey = a.psizey
        self.nopixx = a.nopixx
        self.nopixy = a.nopixy
        self.twist  = a.twist
        self.tiltom = a.tiltom
        self.tiltch = a.tiltch
        self.ttheta = a.ttheta
        self.wavelength = a.wavelength

    def read_from_text_file (self, filename) :
        fil = open (filename, 'r')
        flist =[]
        linebreak = '\n'
        for fline in fil :
            flist.append (fline.replace(linebreak,""))

        self.psizex = float(flist[0])
        self.psizey = float(flist[1])
        self.dist = float(flist[2])
        self.wavelength = float(flist[3])
        self.beamx = float (flist[4])
        self.beamy = float(flist[5])
        self.twist = float (flist[6])
        self.tiltom = float (flist[7])
        self.ttheta = float (flist[8])
        self.tiltch = float (flist[9])
        fil.close()


    def write_to_text_file (self, filename) :
        fil = open(filename,'w')
        fil.write (str(self.psizex)+'\n')
        fil.write (str(self.psizey)+'\n')
        fil.write (str(self.dist)+'\n')
        fil.write (str(self.wavelength)+'\n')
        fil.write (str(self.beamx)+'\n')
        fil.write (str(self.beamy)+'\n')
        fil.write (str(self.twist)+'\n')
        fil.write (str(self.tiltom)+'\n')
        fil.write (str(self.ttheta)+'\n')
        fil.write (str(self.tiltch)+'\n')
        fil.close ()


