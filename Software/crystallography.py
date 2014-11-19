import math
import numpy as np

DTOR = math.pi  / 180.


def A_to_kev (la):
    val = 12.39842/la
    return val

def en_from_tth_and_d( atth, d) :
    tth=atth * DTOR
    #calculates energy from bragg angle and d-spc
    la=2.0*d*math.sin(tth/2.0)
    return A_to_kev(la)


def d_from_lp_and_hkl (lp, hkl) :
    #calculates d-spc from lattice parameters and Miller indices
    b=b_from_lp(lp)
    np
    xyz=hkl * b
    return 1./vlength(xyz)




def b_from_lp (lp):
     #calculates metric matrix from lattice paramteres
    as0=lp[0]
    bs=lp[1]
    cs=lp[2]
    al=lp[3]*DTOR
    be=lp[4]*DTOR
    ga=lp[5]*DTOR
    
    b = np.zeros ((3,3), dtype=np.float32)
    
    b[0,0]=as0
    b[0,1]=0.0
    b[0,2]=0.0
    b[1,0]=bs*math.cos(ga)
    b[1,1]=bs*math.sin(ga)
    b[1,2]=0.0
    b[2,0]=cs*math.cos(be)
    b[2,1]=cs*(math.cos(al)-math.cos(be)*math.cos(ga))/math.sin(ga)
    b[2,2]=cs*sqrt(math.sin(ga)**2-(math.cos(al)**2+math.cos(be)**2-\
            2.0*math.cos(al)*math.cos(be)*math.cos(ga)))/math.sin(ga)
    binv = np.invert (b)
    bs = np.transpose (binv)
    return bs


def dotprod (v, w):
    l = len (v)
    tot=0.
    for i in range (l):
        tot += v[i] * w[i]
    return tot

def vlength (v):
    val = dotprod (v, v)
    return math.sqrt(val)