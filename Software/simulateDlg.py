

from PyQt4 import QtCore, QtGui, uic
import myDetector
import myPeakTable
import numpy as np
from crystallography import *
import cellPathDlg
from myPredict import *
from Project import *
import vector_math
import subprocess



class simulateDlg (QtGui.QDialog) :

    updatePeaks = QtCore.pyqtSignal ()
    updateDisplay = QtCore.pyqtSignal ()


    def __init__(self) :
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi("simulateDlg.ui", self)

        self.sim_inc_omchiphi.clicked.connect (self.incVal)
        self.sim_dec_omchiphi.clicked.connect (self.decVal)
        self.sim_genBButton.clicked.connect (self.genB)
        self.sim_genButton.clicked.connect (self.generate)
        self.sim_changeBButton.clicked.connect (self.changeB)
        self.sim_assignHKLButton.clicked.connect (self.assignHKL)
        self.ui.sim_indexButton.clicked.connect (self.index)
        self.ui.sim_closeButton.clicked.connect (self.closeUp)
        self.ui.sim_resetOCPButton.clicked.connect (self.resetOCP)
        self.ui.sim_openUB.clicked.connect (self.openUB)
        self.ui.sim_saveUB.clicked.connect (self.saveUB)
        self.myDetect = myDetector.myDetector()
        self.dacOpen = 18.
        self.ub = np.zeros ((3,3),dtype=np.float64)
        self.myPredict = myPredict()
        self.myPeaks = myPeakTable.myPeakTable()
        self.bravType = 'P'
        self.setAttribute (QtCore.Qt.WA_DeleteOnClose, True)
        self.workdir = ''
        self.base = ''
        self.projFlag = False
        self.fillUp()


    def setWorkDir (self, d) :
        self.workdir = d

    def setBSizeControl (self, tl) :
        self.bsControl = tl

    def setExcludeControl (self, ec):
        self.excludeCBox = ec

    def setDetector (self, mydetect) :
        self.myDetect = mydetect

    def setPeakTable (self, ptable) :
        self.myPeaks = ptable

    def setPredict (self, myPredict) :
        self.myPredict = myPredict
        self.dacOpen = myPredict.dac_open

    def setProject (self, p) :
        self.project = p
        self.projFlag = True
        ubf = self.project.base+'.ub'
        fil = QtCore.QFile (ubf)
        if (fil.exists()) :
            fil.close()
            self.loadUB(ubf)
        else :
            fil.close()

    def fillUp(self) :
        self.ui.sim_aLE.setText( '3.')
        self.ui.sim_bLE.setText( '3.')
        self.ui.sim_cLE.setText( '3.')
        self.ui.sim_alphaLE.setText('90.')
        self.ui.sim_betaLE.setText('90.')
        self.ui.sim_gammaLE.setText('90.')
        str = '%f'%self.dacOpen
        self.ui.sim_DACOpenLE.setText(str)
        self.ui.sim_chiLE.setText('0.')
        self.ui.sim_phiLE.setText('0.')
        self.ui.sim_omegaLE.setText ('0.')
        self.ui.sim_incidRangeLowLE.setText ('5.')
        self.ui.sim_incidRangeHighLE.setText ('25.')
        self.ui.sim_incLE.setText('1.')
        self.ui.sim_scaleIncLE.setText('.002')

    def incVal (self):
        incValue = self.ui.sim_incLE.text().toFloat()[0]
        # check for which radiobutton is selected
        valType = self.radState ()
        if (valType == 0) :
            value = self.ui.sim_omegaLE.text().toFloat()[0] + incValue
            str = "%f"%value
            self.ui.sim_omegaLE.setText(str)
            return
        if (valType == 1) :
            value = self.ui.sim_chiLE.text().toFloat()[0] + incValue
            str = "%f"%value
            self.ui.sim_chiLE.setText(str)
        if (valType == 2) :
            value = self.ui.sim_phiLE.text().toFloat()[0] + incValue
            str = "%f"%value
            self.ui.sim_phiLE.setText(str)


    def decVal (self):
        incValue = self.ui.sim_incLE.text().toFloat()[0]
        # check for which radiobutton is selected
        valType = self.radState ()
        if (valType == 0) :
            value = self.ui.sim_omegaLE.text().toFloat()[0] - incValue
            str = "%f"%value
            self.ui.sim_omegaLE.setText(str)
            return
        if (valType == 1) :
            value = self.ui.sim_chiLE.text().toFloat()[0] - incValue
            str = "%f"%value
            self.ui.sim_chiLE.setText(str)
        if (valType == 2) :
            value = self.ui.sim_phiLE.text().toFloat()[0] - incValue
            str = "%f"%value
            self.ui.sim_phiLE.setText(str)

    def radState(self):
        ### checks to see which radio button is checked
        ### returns 0 for omega
        ### returns 1 for chi
        ### returns 2 for phi
        if self.ui.omRad.isChecked() :
            return (0)
        if self.ui.chiRad.isChecked() :
            return (1)
        return (2)

    def genB (self):
        lp = self.read_LP()
        self.ub = b_from_lp(lp)
        self.displayMatrix  (0)
        self.generate_laue()

    # presently this has the same functionality as genB
    def changeB (self):
        lp = self.read_LP()
        self.ub = b_from_lp(lp)
        self.displayMatrix  (0)
        self.generate_laue()

    def resetOCP (self):
        str = '0.0'
        self.sim_omegaLE.setText(str)
        self.sim_chiLE.setText(str)
        self.sim_phiLE.setText(str)


    def read_LP (self):
        a = self.sim_aLE.text().toFloat()[0]
        b = self.sim_bLE.text().toFloat()[0]
        c = self.sim_cLE.text().toFloat()[0]
        alpha = self.sim_alphaLE.text().toFloat()[0]
        gamma = self.sim_gammaLE.text().toFloat()[0]
        beta = self.sim_betaLE.text().toFloat()[0]
        lp = [a,b,c,alpha,beta,gamma]

        return lp


    def print_LP (self, lp):
        str=QtCore.QString.number (lp[0])
        self.sim_aLE.setText(str)
        str=QtCore.QString.number (lp[1])
        self.sim_bLE.setText(str)
        str=QtCore.QString.number (lp[2])
        self.sim_cLE.setText(str)
        str=QtCore.QString.number (lp[3])
        self.sim_alphaLE.setText(str)
        str=QtCore.QString.number (lp[4])
        self.sim_betaLE.setText(str)
        str=QtCore.QString.number (lp[5])
        self.sim_gammaLE.setText(str)

    ### open UB matrix
    def openUB (self) :
        if self.projFlag :
            suggFile = self.project.base+'.ub'
        else :
            suggFile = self.workdir
        ubFile = QtGui.QFileDialog.getOpenFileName(self, 'Open UB File for Reading ', suggFile)
        if (ubFile.length() < 2) :
            return


    def loadUB (self, fname) :
        self.ub = open_UB (fname)
        self.displayMatrix (0)


    def saveUB (self) :
        if self.projFlag :
            suggFile = self.project.base+'.ub'
        else :
            suggFile = self.workdir

        ubFile = QtGui.QFileDialog.getSaveFileName(self, 'Open UB File for Reading ', suggFile)
        if (ubFile.length() < 2) :
            return
        f = open (ubFile , 'w')
        for i in range (3) :
            str = '%f %f %f\r\n'%(self.ub[i][0],self.ub[i][1], self.ub[i][2])
            f.write (str)
        f.close()

    def displayMatrix (self, matType) :
        ### display in the matrixDispText Box matrix
        ### 0 - UB

        if (matType ==0) :
            l0 = '%10.5f\t%10.5f\t%10.5f\r\n%10.5f\t%10.5f\t%10.5f\r\n%10.5f\t%10.5f\t%10.5f'%(self.ub[0,0],self.ub[0,1],self.ub[0,2],self.ub[1,0],self.ub[1,1],self.ub[1,2],self.ub[2,0],self.ub[2,1],self.ub[2,2])
            self.sim_matrixDispText.setText(l0)
            return

    def assignHKL (self) :
        lp = self.read_LP()
        numpeaks = self.myPeaks.getpeakno()
        print 'number of peaks in assign hkl is ', numpeaks
        ds = np.zeros((numpeaks),dtype=np.float32)
        ipeak=0
        notSelected = 0
        w =[]
        for peakO in self.myPeaks.peaks :
            xyz = peakO.xyz
            #print ipeak, xyz
            ds[ipeak]= 1./vlength (xyz)
            hkls1 = find_possible_hkls (ds[ipeak],lp, 0.02, [10,10,10])
            print 'hkls : ',hkls1[0][0]
            if hkls1[0][0]==0 :
                peakO.clickSelected = True
            else :
                notSelected += 1
                w.append (ipeak)
            ipeak = ipeak + 1
        self.updateDisplay.emit()
        if (notSelected > 0) :
            s = np.argsort (ds[w])[::-1]
            succ = 0
            att0 = 0
            while succ==0 and att0 < notSelected-2 :
                x1 = self.myPeaks.peaks[w[s[att0]]].xyz
                att1 = att0 + 1
                while succ != 1 and att1 < notSelected -1 :
                    x2 = self.myPeaks.peaks[w[s[att1]]].xyz
                    a = vector_math.recognize_two_vectors (x1, x2, lp, 0.02, 0.02)
                    if (a[0] == 1) :
                        succ=1
                        self.myPeaks.peaks[w[s[att0]]].hkl = a[1]
                        self.myPeaks.peaks[w[s[att1]]].hkl = a[2]
                    else :
                        att1 = att1+1
                        lenw = len(w)
                        if (att1 == lenw) :
                            att0 = att0+1
        if (succ == 1) :
            ubSave = self.ub
            self.ub = vector_math.UB_from_two_vecs_and_lp (x1, x2, a[1], a[2], lp)
            self.displayMatrix(0)
            self.print_LP (lp)
            self.updatePeaks.emit()

    def generate (self) :
        polyFlag = self.ui.sim_polyRButton.isChecked() ;
        if (polyFlag) :
            self.generate_laue ()
        else :
            self.generate_mono()
        self.updatePeaks.emit()


    def index (self) :
        npeaks = self.myPeaks.getpeakno()
        if npeaks < 1 :
            return

        # get the location of the cell_now executable
        cellpathdlg = cellPathDlg.cellPathDlg ()
        status = cellpathdlg.exec_()
        if status != QtGui.QDialog.Accepted :
            return

        cell_now_dir = os.path.normpath(cellpathdlg.path.toLatin1().data())
        #cell_now_dir,ok = QtGui.QInputDialog.getText (self, "Path to cell_now executable",  "Enter directory")
        #if not ok :
        #    return
        cell_now = cell_now_dir + '/run_cellnow.cmd'
        print "Cell now command is : %s"%cell_now
        status = QtCore.QFile.exists(cell_now)
        if not status :
            print 'could not file cell_now executable'
            return

        # need to save the peak table in .p4p format
        p4pfil = cell_now_dir+'/xxx.p4p'
        self.myPeaks.save_p4p (p4pfil)


        #ab = cell_now_solution_n(1)

        subprocess.call (cell_now)





    def getBravaisType (self) :
        self.bravType = self.ui.sim_bravTypeCB.currentText().toLatin1().data()


    def generate_laue (self) :
        en0 = self.ui.sim_incidRangeLowLE.text().toFloat()[0]
        en1 = self.ui.sim_incidRangeHighLE.text().toFloat()[0]
        DAC_open = self.ui.sim_DACOpenLE.text().toFloat()[0]
        #updates the bravType member
        self.getBravaisType ()
        self.myDetect.generate_peaks_laue(self.ub, self.myPeaks, self.myPredict, [en0,en1],self.bravType, DAC_open)
        numpeaks = self.myPeaks.getpeakno ()
        print 'Numpeaks is now : ', numpeaks
        self.updatePeaks.emit()


    def generate_mono (self) :
        self.myPeaks.remove_all_peaks()
        en0 = self.ui.sim_incidRangeLowLE.text().toFloat()[0]
        en1 = self.ui.sim_incidRangeHighLE.text().toFloat()[0]
        DAC_open = self.ui.sim_DACOpenLE.text().toFloat()[0]
        wv = self.myDetect.getwavelength()
        #updates the bravType member
        self.getBravaisType ()
        #get from the predict tab in the Atrex class
        ## generate all peaks
        bx = self.read_box_size()
        self.myDetect.generate_all_peaks(self.ub, self.myPeaks, wv, self.myPredict, self.bravType,  DAC_open, bx)

        #check whether to exclude peaks at corners
        if (self.excludeCBox.isChecked()):
            self.myPeaks.remove_peaks_outside_aa (self.myDetect)
        # this is from the part/full overlap on the predict tab
        gg = [self.myPredict.fullOverlap, self.myPredict.partOverlap]
        self.myPeaks.select_close_overlaps (gg)
        self.updatePeaks.emit()



    # from the topLevel Peaks2 tab, get the box size....
    def read_box_size (self):
        val = self.bsControl.text().toInt()
        return [val[0],val[0]]



    def closeUp (self) :
        self.close ()
