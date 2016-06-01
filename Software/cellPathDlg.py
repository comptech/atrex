from PyQt4 import QtGui, QtCore, uic

class cellPathDlg (QtGui.QDialog) :



    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("cellPathDlg.ui", self)
        self.path = ""
        self.ui.cellPathLE.setText ("")
        self.ui.browseButton.clicked.connect (self.browse)
        self.ui.cancelButton.clicked.connect (self.cancelThis)
        self.ui.okButton.clicked.connect (self.okThis)
        self.status = False

    ###
    #   browse for the path to cell_now.exe
    ###
    def browse(self):
        self.path = QtGui.QFileDialog.getExistingDirectory(self, 'Define Cell Now Directory',
                                                                     "",
                                                                     QtGui.QFileDialog.ShowDirsOnly)
        self.ui.cellPathLE.setText (self.path)

    def okThis (self) :
        temps = self.ui.cellPathLE.text()

        self.path = temps
        self.accept()

    def cancelThis (self) :
        self.status = False
        self.reject()






