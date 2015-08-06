__author__ = 'harold'
from PyQt4 import QtCore, QtGui, uic

""" Project.py
    File containing utilities to get the image base from a input file name and to return a filename
    based upon the image base
"""


class Project :

    base = ''
    filenum = 0
    curimage = QtCore.QString('')

    def getImageBase (self, filename) :
        ind_of_suffx = filename.lastIndexOf ('.')
        self.base = filename.left(ind_of_suffx-3)
        curimage = filename
        self.filenum = self.getFileNumber (filename)
        return self.base



    def getFileNameFromNum (self, number) :
        tempfile = QtCore.QString('%1%2.tif').arg(self.base).arg(int(number), 3, 10, QtCore.QChar('0'))
        self.filenum = number
        #print 'debug :', tempfile
        return tempfile

    def getFileNumber (self, filename) :
        ind_of_suffix = filename.lastIndexOf ('.')
        left = filename.mid (ind_of_suffix - 3, 3)
        self.filenum = left.toInt()
        print 'Debug : %d', self.filenum
        return self.filenum
