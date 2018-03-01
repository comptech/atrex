
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *
from myGenSettingsDlg import *
from atrex_utils import *
from fnmatch import *
import os




class Project :
    """ Project.py
    Class containing utilities to get the image base from a input file name and to return a filename
    based upon the image base
    """






    def __init__(self):
        self.ubFlag = False
        self.calFlag = False
        self.projFile = ''
        self.ubFile = ''
        self.calFile = ''
        self.settingsArray = [0.,0.,0.,0.,0.,0.,0]
        self.filenum = 0
        self.curimage = ''
        self.projFlag = False
        self.numDigits = 3
        self.imFile =''
        self.omega0 = 0
        self.omegaR = 15
        self.expos = 10.
        self.chi = 0.
        self.detector = 0.
        self.base = ""
        self.h5Flag = False
        self.minImageNum =1E9
        self.maxImageNum =-1E9
        self.numImages = 0

    def getImageBase (self, filename) :
        """
        getImageBase returns the prefix which will be used for subsequent file naming based upon
        an input filename
        :param filename:
        :return:
        """
        self.imFile = filename
        ind_of_suffx = find_last_index_of (filename,'.')
        ind_of_start_num = find_last_index_of(filename,'_') +1
        extension = os.path.splitext(filename)[1]
        if "h5" in extension :
            self.h5Flag = True
        else :
            self.h5Flag = False

        newbase = filename[0:ind_of_start_num]
        if not self.h5Flag :
            imstringFilt = '%s*.tif'%newbase
        else :
            imstringFilt = '%s*.h5'%newbase
        curimage = filename
        self.filenum = self.getFileNumber (filename)
        #print 'Debug : %s'%self.filenum
        qfinfo = QFileInfo (filename)
        apath = qfinfo.absolutePath()
        fileonly = qfinfo.fileName ()
        tmpind = find_last_index_of(fileonly,'_')+1
        tmpbase = fileonly[0:tmpind]
        qd = QDir (apath)

        #qd.setNameFilters ([imstringFilt])
        imfiles0 = qd.entryList()
        imfiles = []
        for nm in imfiles0 :
            nm = '%s/%s'%(apath,nm)
            if fnmatch (nm, imstringFilt) :
                imfiles.append(nm)

        #print qd.entryList()
        n = len(imfiles)
        self.minImageNum = 1E10
        self.maxImageNum = -1
        for i in imfiles :
            if i.rfind(tmpbase) < 0 :
                continue
            #if (i.contains(tmpbase) == False) :
                #continue

            startInd = find_last_index_of(i,'_')+1
            endInd = find_last_index_of (i,'.')
            self.numDigits = endInd - startInd

            num = int(i[startInd:startInd+self.numDigits])
            print num, '   ',i
            if (num < self.minImageNum) :
                self.minImageNum = num
            if (num > self.maxImageNum) :
                self.maxImageNum = num
        print 'min image : ', self.minImageNum
        print 'max image : ', self.maxImageNum
        self.numImages = self.maxImageNum - self.minImageNum + 1
        print 'num images : ',self.numImages
        if (self.base != newbase) :
            self.base = newbase
            self.checkForFiles()

        else :
            setfile = filename+'.txt'
            qf = QFile (setfile)
            if (qf.exists()) :
                self.readFileSettings (setfile)
        return self.base

    def getFileNameFromNum (self, number) :
        if self.h5Flag :
            tempfile = '%s%0*d.h5'%(self.base,self.numDigits,number)
            #tempfile = QString('%1%2.h5').arg(self.base).arg(int(number), self.numDigits, 10, QChar('0'))
        else :
            tempfile = '%s%0*d.h5' % (self.base, self.numDigits,number)
            #tempfile = QString('%1%2.tif').arg(self.base).arg(int(number), self.numDigits, 10, QChar('0'))
        self.filenum = number
        #print 'debug :', tempfile
        return tempfile

    def getFileNumber (self, filename) :
        ind_of_suffix = find_last_index_of (filename, '.')
        ind_of_start_num = find_last_index_of (filename,'_')
        self.numDigits = ind_of_suffix - ind_of_start_num
        left = filename[ind_of_start_num+1:ind_of_start_num+self.numDigits]
        #left = filename.mid (ind_of_start_num, self.numDigits)
        self.filenum = int(left)
        #print "Debug : %d" % self.filenum
        return self.filenum

    def checkForFiles (self) :
        self.prjFile = '%s_projset.txt'%self.base
        self.ubFile = '%s_ub.txt'%self.base
        cFile = '%s.cal'%self.base
        qfil = QFile (self.prjFile)
        if (qfil.exists()==False) :
            print 'Debug : project settings file does not exist'
            self.projFlag = False
        else :
            self.projFlag = True
        print 'Project settings flag is : %r'%self.projFlag
        qfil = QFile (self.ubFile)
        if (qfil.exists()==False) :
            print 'Debug : ub file does not exist'
            self.ubFlag = False
        else :
            self.ubFlag = True
        print 'UB flag is : %r'%self.ubFlag

        qfil = QFile (cFile)

        if (qfil.exists()):
            self.calFile = cFile
            self.calFlag = True
        else :
            self.calFlag = False

        imsettingsFile ='%s.txt'%(self.imFile)
        qfil = QFile (imsettingsFile)
        if (qfil.exists()==False) :
            gsdlg = myGenSettingsDlg ()
            gsdlg.setInitialVals (0., 15., self.minImageNum, self.maxImageNum-self.minImageNum + 1, 5., 3., 10.)
            gsdlg.setArr (self.settingsArray)
            gsdlg.exec_()
            if (gsdlg.status > 0) :
                self.writeSettingsFiles()
            print self.settingsArray
            self.omega0 = self.settingsArray[0]
            self.omegaR = self.settingsArray[1]
            self.chi = self.settingsArray[4]
            self.detector = self.settingsArray[5]
            self.expos = self.settingsArray[6]

        else :
            qfil.close()
            self.readFileSettings(imsettingsFile)

    def readFileSettings (self, fname) :
        f = open (fname, 'r')
        str = f.readline()
        a = str.split('=')
        self.omega0 = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.omegaR = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.chi = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.detector = float(a[1])
        str = f.readline()
        a = str.split('=')
        self.expos = float(a[1])
        f.close()


    def writeSettingsFiles (self) :
        z = QChar ('0')
        for i in range (self.minImageNum, self.maxImageNum+1) :
            filename = QString("%1%2.tif.txt").arg(self.base).arg(i, self.numDigits, 10, z)
            outfil = file (filename.toLatin1().data(), 'w')
            om0 = self.settingsArray [0] + (i - self.minImageNum) * self.settingsArray[1]
            str = 'OMEGA0 = %f\r\n'%om0
            outfil.write (str)
            om1 = self.settingsArray[1]
            str = 'OMEGAR = %f\r\n'%om1
            outfil.write (str)
            expos = self.settingsArray[6]
            chi = self.settingsArray [4]
            detector = self.settingsArray[5]
            str = 'chi = %f\r\n'%chi
            outfil.write (str)
            str = 'detector = %f\r\n'%detector
            outfil.write (str)
            str = 'exp. time = %f\r\n'%expos
            outfil.write (str)
            outfil.close()






