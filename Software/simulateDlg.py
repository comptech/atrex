

from PyQt4 import QtCore, QtGui, uic
import numpy as np



class simulateDlg (QtGui.QDialog) :

   def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("simulateDlg.ui", self)