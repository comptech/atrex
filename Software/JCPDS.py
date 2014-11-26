__author__ = 'harold'
import os.path
import re
import math
import copy

dtor = math.pi / 180.

class Reflection :
    d0=0.
    d=0.
    inten=0.
    h=0.
    k=0.
    l=0.

    def parseVals (self, instr):
        tmpstr = instr.split()
        self.d0 = float (tmpstr[0])
        self.inten = float (tmpstr[1])
        self.h = float (tmpstr[2])
        self.k = float (tmpstr[3])
        self.l = float (tmpstr[4])

    def parseValsXPOW (self, instr):
        tmpstr = instr.strip().split()
        self.d0 = float (tmpstr[2])
        self.inten = float (tmpstr[1])
        self.h = float (tmpstr[3])
        self.k = float (tmpstr[4])
        self.l = float (tmpstr[5])


class JCPDS :

    a=0.
    b=0.
    c=0.
    d=0.
    a0=0.
    b0=0.
    c0=0.
    d0=0.
    comment=[]
    reflections=[]
    symmetry=''
    file = ''
    version = 0
    k0=0.
    k0p =0.
    dk0dt = 0.
    dk0pdt=0.
    alphat=0.
    dalphadt=0.
    alpha0=0.
    beta0=0.
    gamma0=0.
    alpha=0.
    beta=0.
    gamma=0.
    v0=0.
    v=0.



    def __init__(self) :
        self.a = 0.


    def read_file (self, filename):
        line = ''
        ncomments = 0
        numDIHKL = 0
        self.version = 0
        if (not os.path.isfile(filename)) :
            return
        f = open (filename, 'r')
        tag=""
        arr=[]
        num=0
        self.reflections[:]=[]
        self.comment[:]=[]
        line = f.readline ()
        strList = line.split (':')

        if "VERSION" in strList[0] :
            # need to supply feedback as this file is not supported
            self.version = int (strList[1].strip())

        if self.version > 0 :
            for line in f :

                line = line.strip()
                vals = re.findall('\w+', line)
                strList = line.split(':')
                tag = vals[0]

                if (tag == 'COMMENT') :
                    self.comment.append (strList[1])
                    ncomments += 1
                    continue
                if (tag=='K0') :
                    self.k0 = float(strList[1])
                if (tag=='K0P') :
                    self.k0p = float(strList[1])
                if (tag=='DK0DT'):
                    self.dk0dt = float(strList[1])
                if (tag=='DK0PDT'):
                    self.dk0pdt = float(strList[1])
                if (tag=='SYMMETRY') :
                    self.symmetry = strList[1].upper().strip()
                if (tag=='A') :
                    self.a0 = float(strList[1])
                if (tag=='B') :
                    self.b0 = float(strList[1])
                if (tag=='C') :
                    self.c0 = float(strList[1])
                if (tag=='ALPHA') :
                    self.alpha0 = float(strList[1])
                if (tag=='BETA') :
                    self.beta0 = float(strList[1])
                if (tag=='GAMMA') :
                    self.gamma0 = float(strList[1])
                if (tag=='VOLUME') :
                    self.v0 = float(strList[1])
                if (tag=='ALPHAT') :
                    self.alphat = float (strList[1])
                if (tag=='DALPHADT') :
                    self.dalphadt = float (strList[1])
                if (tag=='DIHKL') :
                    refl = Reflection ()
                    refl.parseVals (strList[1])
                    self.reflections.append(refl)
        else :
            self.version = 1
            self.comment.append (line)
            line = f.readline()
            line = line.strip()
            strList = line.split()
            #strList = re.findall ("\w+", line)
            if (int(strList[0])==1) : self.symmetry='CUBIC'
            if (int(strList[0])==2) : self.symmetry='HEXAGONAL'
            strList[1] = strList[1].strip (",")
            strList[3] = strList[3].strip (",")
            self.a0 = float(strList[1])
            self.k0 = float(strList[2])
            self.k0p = float(strList[3])
            c0a0 = float(strList[4])
            self.c0 = self.a0 * c0a0
            line = f.readline()
            for line in f :
                refl = Reflection ()
                refl.parseVals (line)
                self.reflections.append (refl)

        self.compute_v0()
        self.a = self.a0
        self.b = self.b0
        self.c = self.c0
        self.d = self.d0
        self.alpha = self.alpha0
        self.beta = self.beta0
        self.gamma = self.gamma0
        self.v = self.v0

        numRefl = len (self.reflections)
        print 'Number of reflections %d'%(numRefl)

        if numRefl > 0 :
            self.compute_D ()
            diff = []
            count =0
            for r in self.reflections :
                diff.append (math.fabs(r.d0 - r.d)/ r.d0)
            print diff
            print 'hello'

        for i in range (numRefl) :
            #if diff[i] < .001 : continue
            r= self.reflections[i]
            outstr = 'Reflect %f %f %f %f %f %f\r\n'%(r.inten, r.h, r.k, r.l, r.d, r.d0)
            print outstr

    def read_xpow (self, fname) :
        self.fname = fname

        lcount = 0
        self.symmetry = 'CUBIC'
        fil = open (fname, 'r')
        for line in fil :

            if lcount == 3 or lcount == 4 :
                self.comment.append (line.strip())
                lcount += 1
                continue
            if 'CELL' in line :
                strSplit = line.split (':')
                newline = strSplit[1].strip().split()
                self.a0 = float (newline[0])
                self.b0 = float (newline[1])
                self.c0 = float (newline[2])
                self.alpha0 = float (newline[3])
                self.beta0 = float (newline[4])
                self.gamma0 = float (newline[5])
            if '2-THETA' in line :
                # this will be the last line before the reflection lines....
                break

        # now read the reflections
        for line in fil :
            # check if end of list...
            if '===' in line : break
            #otherwise create next reflection
            refl = Reflection ()
            refl.parseValsXPOW (line)
            self.reflections.append (refl)



        self.compute_v0()
        self.a = self.a0
        self.b = self.b0
        self.c = self.c0
        self.d = self.d0
        self.alpha = self.alpha0
        self.beta = self.beta0
        self.gamma = self.gamma0
        self.v = self.v0

        numRefl = len (self.reflections)
        print 'Number of reflections %d'%(numRefl)

        if numRefl > 0 :
            self.compute_D ()
            diff = []
            count =0
            for r in self.reflections :
                diff.append (math.fabs(r.d0 - r.d)/ r.d0)
            print diff


        for i in range (numRefl) :
            #if diff[i] < .001 : continue
            r= self.reflections[i]
            outstr = 'Reflect %f %f %f %f %f %f\r\n'%(r.inten, r.h, r.k, r.l, r.d, r.d0)
            print outstr

    def write_file (self, fname):
        fil = open (fname, 'w')
        fil.write ("VERSION : %1\n"%(self.version))
        for icom in self.comment :
            fil.write ("COMMENT : %s\n"%(icom))
        fil.write ("K0: %10.3f\n"%self.k0)
        fil.write ("K0P: %10.3f\n"%self.k0p)
        fil.write ("DK0DT: %10.3f\n"%self.dk0dt)
        fil.write ("DK0PDT: %10.3f\n"%self.dk0pdt)
        fil.write ("SYMMETRY: %s\n"%self.symmetry)
        fil.write ("A: %10.4f\n"%self.a)
        fil.write ("B: %10.4f\n"%self.b)
        fil.write ("C: %10.4f\n"%self.c)
        fil.write ("ALPHA: %10.4f\n"%self.alpha0)
        fil.write ("BETA: %10.4f\n"%self.beta0)
        fil.write ("GAMMA: %10.4f\n"%self.gamma0)
        fil.write ("VOLUME: %10.4f\n"%self.v0)
        fil.write ("ALPHAT: %10.4f\n"%self.alphat)
        fil.write ("DALPHADT: %10.4f\n"%self.dalphadt)
        numRefl = len (self.reflectons)
        for r in self.reflections :
                str = "DIHKL: %7.4f %3.1f %d %dn"%(r.d0, r.inten, r.h, r.k, r.l)
                fil.write

        fil.close()


    def compute_D (self, Press=0, Temp=298) :
        ratio = (self.v/self.v0)**(1.0/3.0)
        self.a = self.a0 * ratio
        self.b = self.b0 * ratio
        self.c = self.c0 * ratio
        a=self.a
        b=self.b
        c=self.c
        alpha = self.alpha * dtor
        beta = self.beta * dtor
        gamma = self.gamma * dtor
        
        numRefl = len (self.reflections)
        for i in range (numRefl) :
            h = self.reflections[i].h
            k = self.reflections[i].k
            l = self.reflections[i].l
        
            if self.symmetry == 'CUBIC' :
                d2inv = (h**2 + k**2 + l**2)/ a**2 
            if self.symmetry == 'TETRAGONAL' :
                d2inv (h**2 + k**2) / a**2 + l**2/ c**2
            if self.symmetry == 'ORTHORHOMBIC' :
                d2inv = h**2 / a**2 + k**2 / b**2 + l**2 / c**2
            if self.symmetry == 'HEXAGONAL' :
                d2inv = (h**2 + h*k + k**2) * 4./3./a**2 + l**2/c**2
            if self.symmetry == 'RHOMBOHEDRAL' :
                d2inv = ((1. + math.cos(alpha)) * ((h**2 + k**2 + l**2) - \
                    (1 - math.tan(0.5*alpha)**2)*(h*k + k*l + l*h))) / \
                    (a**2 * (1 + math.cos(alpha) - 2*math.cos(alpha)**2))
            if self.symmetry == 'MONOCLINIC' :
                 d2inv = h**2 / math.sin(beta)**2 / a**2 + k**2 / b**2 + l**2 \
                    / math.sin(beta)**2 / c**2 + \
                    2 * h * l * math.cos(beta) / (a * c * math.sin(beta)^2)
            if self.symmetry == 'TRICLINIC' :
                V = a**2 * b**2 * c**2 * \
                            (1. - math.cos(alpha)**2 - math.cos(beta)**2 - math.cos(gamma)**2 + \
                            2 * math.cos(alpha) * math.cos(beta) * math.cos(gamma))
                s11 = b**2 * c**2 * math.sin(alpha)**2
                s22 = a**2 * c**2 * math.sin(beta)**2
                s33 = a**2 * b**2 * math.sin(gamma)**2
                s12 = a * b * c**2 * \
                        (math.cos(alpha) * math.cos(beta) - math.cos(gamma))
                s23 = a**2 * b * c * \
                        (math.cos(beta) * math.cos(gamma) - math.cos(alpha))
                s31 = a * b**2 * c * \
                        (math.cos(gamma) * math.cos(alpha) - math.cos(beta))
                d2inv = (s11 * h**2 + s22 * k**2 + s33 * l**2 + \
                     2.*s12*h*k + 2.*s23*k*l + 2.*s31*l*h) / V**2
            
            self.reflections[i].d = math.sqrt (1./ d2inv)
        
        


    def compute_v0(self):

        if self.symmetry.strip() == 'CUBIC' :
            self.b0 = self.a0
            self.c0 = self.a0
            self.alpha0 = 90.
            self.beta0 = 90.
            self.gamma0 = 90.

        if self.symmetry == 'TETRAGONAL':
            self.b0 = self.a0
            self.alpha0 = 90.
            self.beta0 = 90.
            self.gamma0 = 90.

        if self.symmetry =='ORTHORHOMBIC':
            self.alpha0 = 90.
            self.beta0 = 90.
            self.gamma0 = 90.

        if self.symmetry =='HEXAGONAL':
            self.b0 = self.a0
            self.alpha0 = 90.
            self.beta0 = 90.
            self.gamma0 = 120.

        if self.symmetry =='RHOMBOHEDRAL':
            self.b0 = self.a0
            self.c0 = self.a0
            self.beta0 = self.alpha0
            self.gamma0 = self.alpha0

        if self.symmetry =='MONOCLINIC':
            self.alpha0 = 90.
            self.gamma0 = 90.

        if self.symmetry == 'TRICLINIC':
            dummy = self.alpha0

        dtor = math.pi / 180.
        self.v0 = self.a0 * self.b0 * self.c0 * math.sqrt (1. - math.cos(self.alpha0 * dtor)**2 - \
            math.cos (self.beta0 * dtor)**2 - math.cos(self.gamma0 * dtor)**2) + 2. * math.cos(self.alpha0 * dtor) * \
            math.cos (self.beta0 * dtor)  * math.cos(self.gamma0 * dtor)

    def compute_v (self) :
        if self.symmetry == 'CUBIC' :
            self.b = self.a
            self.c = self.a
            self.alpha = 90.
            self.beta = 90.
            self.gamma = 90.

        if self.symmetry == 'TETRAGONAL':
            self.b = self.a
            self.alpha = 90.
            self.beta = 90.
            self.gamma = 90.

        if self.symmetry =='ORTHORHOMBIC':
            self.alpha = 90.
            self.beta = 90.
            self.gamma = 90.

        if self.symmetry =='HEXAGONAL':
            self.b = self.a
            self.alpha = 90.
            self.beta = 90.
            self.gamma = 120.

        if self.symmetry =='RHOMBOHEDRAL':
            self.b = self.a0
            self.c = self.a0
            self.beta = self.alpha
            self.gamma = self.alpha

        if self.symmetry =='MONOCLINIC':
            self.alpha = 90.
            self.gamma = 90.

        if self.symmetry == 'TRICLINIC':
            dummy = self.alpha

        self.v = self.a * self.b * self.c * math.sqrt (1. - math.cos(self.alpha * dtor)**2 - \
            math.cos (self.beta * dtor)**2 - math.cos(self.gamma * dtor)**2) + 2. * math.cos(self.alpha * dtor) * \
            math.cos (self.beta * dtor)  * math.cos(self.gamma * dtor)


    def compute_volume (self, pressure=0., temp=298.) :
        delT = temp - 298.
        k0 = self.k0
        alphat = self.alphat + self.dalphadt * delT
        k0p = self.k0 + self.dk0pdt * delT

        if pressure ==0. :
            self.v = self.v0 * (1 + alphat * delT)
        else :
            if k0 <= 0. :
                self.v = self.v0
                print "Pressure less than equal to zero, computing zero pressure volume"
            else :
                mod_pressure = pressure - alphat * k0 * delT
                # need to add in the fx_roots (idl) capability
                # for now though
                print "Fx_root not yet implemented ; using v0"
                self.v = self.v0

    def bm3_pressure (self) :
        self.compute_v0()
        self.compute_v()
        v0_v = self.v0 / self.v
        k0 = self.k0
        k0p = self.k0p

        val = 1.5*k0*(v0_v**(7./3.) - v0_v**(5./3.)) * \
            (1 + 0.75*(k0p - 4.) * (v0_v**(2./3.) - 1.0))
        return val


    def check_for_equivalents (self, refs, hkl, N, exti) :
        res = 0
        for j in range (N+1) :
            hk11 = [refs[j].h, refs[j].k, refs[j].l]
            # need equivalent function, imagine it checks to see if identical...
        return (0)

    def copy_object1 (self):
        re = JCPDS ()
        re.file=self.file
        re.version=self.version
        re.comment=self.comment
        re.symmetry=self.symmetry
        re.k0=self.k0
        re.k0p=self.k0p
        re.dk0dt=self.v
        re.dk0pdt=self.dk0pdt
        re.alphat=self.alphat
        re.dalphadt=self.dalphadt
        re.a0=self.a0
        re.b0=self.b0
        re.c0=self.c0
        re.alpha0=self.alpha0
        re.beta0=self.beta0
        re.gamma0=self.gamma0
        re.v0=self.v0
        re.a=self.a
        re.b=self.b
        re.c=self.c
        re.alpha=self.alpha
        re.beta=self.beta
        re.gamma=self.gamma
        re.v=self.v
        re.reflections=self.reflections
        return re

    def copy_object (self) :
        return copy.deepcopy(self)

    def generate_accessible_peaks (self, dbounds, exti) :
        newref = Reflection ()

        refs =[]
        i = 0
        for h in range (-10, 11):
            for k in range (-10, 11):
                for l in range (0, 11):
                    hkl = [h, k, l]
                    d = self.d_from_lp_and_hkl (self.get_lp(), hkl)
                    d0 = self.d_from_lp_and_hkl (self.get_lp0(), hkl)
                    if d >= dbounds[0] and d <= dbounds[1] and self.check_for_equivalents(refs, hkl, i, exti) == 0 :
                        jcpds_reflection = Reflection()
                        jcpds_reflection.d=d
                        jcpds_reflection.d0=d0
                        jcpds_reflection.inten=10
                        jcpds_reflection.h=h
                        jcpds_reflection.k=k
                        jcpds_reflection.l=l
                        refs.append(jcpds_reflection)
        self.reflections = refs


    def get_ks (self) :
        ks = [self.k0, self.k0p]
        return (ks)


    def set_ks (self, ks):
        self.k0 = ks[0]
        self.k0p = ks[1]

    """ lattice parameters
    """
    def get_lp (self) :
        abc =[]
        abc.append (self.a)
        abc.append (self.b)
        abc.append (self.c)
        abc.append (self.alpha)
        abc.append (self.beta)
        abc.append (self.gamma)
        return abc

    def get_lp0 (self) :
        abc =[]
        abc.append (self.a0)
        abc.append (self.b0)
        abc.append (self.c0)
        abc.append (self.alpha0)
        abc.append (self.beta0)
        abc.append (self.gamma0)
        return abc


    def calculate_abc (self, p, T) :
        if self.k0 == 0 :
            p = 0

        self.compute_volume (p,T)
        l = (self.v/self.v0)**(1./3.)
        self.a = l * self.a0
        self.b = l * self.b0
        self.c = l * self.c0


    def set_lp (self, abc) :
        self.a=abc[0]
        self.b=abc[1]
        self.c=abc[2]
        self.alpha=abc[3]
        self.beta=abc[4]
        self.gamma=abc[5]

    def set_lp0 (self, abc) :
        self.a0=abc[0]
        self.b0=abc[1]
        self.c0=abc[2]
        self.alpha0=abc[3]
        self.beta0=abc[4]
        self.gamma0=abc[5]


    def get_symmetry (self) :
        return self.symmetry

    def set_symmetry (self, sym):
        self.symmetry = sym

    def set_comment (self, str) :
        self.comment = []
        self.comment.append(str)

    def get_comment (self):
        return self.comment

    def set_reflections (self, reflec) :
        self.reflections = reflec

    def get_reflections_PC (self, ttheta_range, wv) :


        if len(self.reflections) == 0 : return -1
        temparr = []
        en = A_to_kev (wv)
        count = 0
        for r in self.reflections :
            tth = tth_from_en_and_d(en, r.d)
            if tth > ttheta_range[0] and tth < ttheta_range[1] :
                temparr.append (r)
                count += 1
        if count >0 :
            return temparr
        else :
            return (-1)


    def getParamString (self) :
        outstring = []
        outstring.append("VERSION")
        outstring.append (self.version)
        for icom in self.comment :
            outstring.append ("COMMENT")
            outstring.append (icom)
        outstring.append ("K0")
        outstring.append ("%10.3f"%self.k0)
        outstring.append ("K0P")
        outstring.append ("%10.3f"%self.k0p)
        outstring.append ("DK0DT")
        outstring.append ("%10.3f"%self.dk0dt)
        outstring.append ("DK0PDT")
        outstring.append ("%10.3f"%self.dk0pdt)
        outstring.append ("SYMMETRY")
        outstring.append (self.symmetry)
        outstring.append ("A")
        outstring.append ("%10.4f"%self.a)
        outstring.append ("B")
        outstring.append ("%10.4f"%self.b)
        outstring.append ("C")
        outstring.append ("%10.4f"%self.c)
        outstring.append ("ALPHA")
        outstring.append ("%10.4f"%self.alpha0)
        outstring.append ("BETA")
        outstring.append ("%10.4f"%self.beta0)
        outstring.append ("GAMMA")
        outstring.append ("%10.4f"%self.gamma0)
        outstring.append ("VOLUME")
        outstring.append ("%10.4f"%self.v0)
        outstring.append ("ALPHAT")
        outstring.append ("%10.4f"%self.alphat)
        outstring.append ("DALPHAT")
        outstring.append ("%10.4f"%self.dalphadt)

        #for r in self.reflections :
        #        outstring.append("DIHLK")
        #        outstring.append("%7.4f %3.1f %d %d %d"%(r.d0, r.inten, r.h, r.k, r.l))


        """
        fil.write ("SYMMETRY: %s\n"%self.symmetry)
        fil.write ("A: %10.4f\n"%self.a)
        fil.write ("B: %10.4f\n"%self.b)
        fil.write ("C: %10.4f\n"%self.c)
        fil.write ("ALPHA: %10.4f\n"%self.alpha0)
        fil.write ("BETA: %10.4f\n"%self.beta0)
        fil.write ("GAMMA: %10.4f\n"%self.gamma0)
        fil.write ("VOLUME: %10.4f\n"%self.v0)
        fil.write ("ALPHAT: %10.4f\n"%self.alphat)
        fil.write ("DALPHADT: %10.4f\n"%self.dalphadt)

        numRefl = len (self.reflectons)
        for r in self.reflections :
                str = "DIHKL: %7.4f %3.1f %d %dn"%(r.d0, r.inten, r.h, r.k, r.l)
                fil.write

        """
        return outstring

#jcpds = JCPDS()
#jcpds.read_file ('/home/harold/workdir/jcpds_reader/Examples/cao.jcpds')
