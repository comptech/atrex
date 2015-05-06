

from PyQt4 import QtCore, QtGui, uic
from myDetector import *
import numpy as np



class simulateDlg (QtGui.QDialog) :


    detect = myDetector()

    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("simulateDlg.ui", self)


