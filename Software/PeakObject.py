from PyQt4 import QtCore

class PeakObject :
    xloc = 0
    yloc = 0
    ident = QtCore.QString("")

    def __init__(self, x, y) :
        self.xloc = x
        self.yloc = y


    def x(self) :
        return self.xloc
    def y(self) :
        return self.yloc
