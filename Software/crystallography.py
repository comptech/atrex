import math
import numpy as np
import vector_math

DTOR = math.pi / 180.
radeg = 180. / math.pi

def A_to_kev (la):
    # avoid divide by zero condition
    if (la < 1.E-9) :
        la = 1.E-9
    val = 12.39842/la
    return val

def kev_to_A (E) :
    val = 12.39842/E
    return val

def tth_from_xyz (xyz) :
    if xyz[0] > 0.:
        return (0.)
    e1=[-1.,0.,0.]
    a1 = ang(xyz,e1)
    tth = 2.*(90.-a1)
    return tth


def en_from_tth_and_d( atth, d) :
    tth=atth * DTOR
    #calculates energy from bragg angle and d-spc
    la=2.0*d*math.sin(tth/2.0)
    return A_to_kev(la)

def en_from_xyz (xyz):
    tth = tth_from_xyz (xyz)
    d = 1./vlength(xyz)
    return en_from_tth_and_d(tth, d)

def d_from_tth_and_en (atth, en) :
    tth=atth * DTOR
    # calculated d from braggg angle and energy
    la=A_to_kev(en)
    return (la/(2.0*math.sin(tth/2.0)))

def tth_from_en_and_d (en, d) :
    #calculates bragg angle from energy and d-spc
    la=kev_to_A(en)
    argVal = la / (2. * d)
    if abs(argVal) > 1.0:
        return 999
    return 2.0*math.asin(la/(2.0*d))*radeg

def tth_from_hkl_and_lp  (hkl, lp, wv) :
  B=b_from_lp(lp)
  xyz=B ## hkl
  d=1./vlength(xyz)
  return tth_from_en_and_d(A_to_kev(wv),d)



def d_from_lp_and_hkl (lp, hkl) :
    #calculates d-spc from lattice parameters and Miller indices
    b=b_from_lp(lp)
    hklArr = np.asarray (hkl)
    xyz=hkl * b
    len_xyz = vlength(xyz)
    if (len_xyz < 1.E-8) :
        len_xyz = 1.E-8
    return 1./len_xyz



def equivalent (hkl1, hkl2, exti) :
    res = 0
    if exti == 'CUBIC' :
        if ((abs(hkl1[0]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[1])) and (abs(hkl1[2]) == abs(hkl2[2]))) :
            res = 1
        elif ((abs(hkl1[0]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[2])) and (abs(hkl1[2]) == abs(hkl2[1]))) :
            res = 1
        elif ((abs(hkl1[0]) == abs(hkl2[1])) and (abs(hkl1[1]) == abs(hkl2[0])) and (abs(hkl1[2]) == abs(hkl2[2]))) :
            res = 1
        elif ((abs(hkl1[0]) == abs(hkl2[1])) and (abs(hkl1[1]) == abs(hkl2[2])) and (abs(hkl1[2]) == abs(hkl2[0]))) :
            res = 1
        elif ((abs(hkl1[0]) == abs(hkl2[2])) and (abs(hkl1[1]) == abs(hkl2[1])) and (abs(hkl1[2]) == abs(hkl2[0]))) :
            res = 1
        elif ((abs(hkl1[0]) == abs(hkl2[2])) and (abs(hkl1[1]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[1]))) :
            res = 1
        elif ((hkl1[0] == -hkl2[0]) and (hkl1[1] == -hkl2[1]) and (hkl1[2] == -hkl2[2])) :
            res = 1
    if exti == 'HEXAGONAL' :
        if ((abs(hkl1[0]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[1])) and (abs(hkl1[2]) == abs(hkl2[2]))) :
            res = 1
        elif ((hkl1[0] == -hkl2[1]) and (hkl1[1] == hkl2[0]-hkl2[1]) and (hkl1[2] == hkl2[2])) :
            res = 1
        elif ((hkl1[0] == -hkl2[0]+hkl2[1]) and (hkl1[1] == -hkl2[0]) and (hkl1[2] == hkl2[2])) :
            res = 1
        elif ((hkl1[0] == -hkl2[0]) and (hkl1[1] == -hkl2[1]) and (hkl1[2] == -hkl2[2])) :
            res = 1
    if exti == 'TETRAGONAL' :
        if  (abs(hkl1[0]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[1])) and (abs(hkl1[2]) == abs(hkl2[2]))  :
            res = 1
        elif (abs(hkl1[0]) == abs(hkl2[1])) and (abs(hkl1[1]) == abs(hkl2[0])) and (abs(hkl1[2]) == abs(hkl2[2])) :
            res = 1
        elif  ((hkl1[0] == -hkl2[0]) and (hkl1[1] == -hkl2[1]) and (hkl1[2] == -hkl2[2])) :
            res=1
    if exti == 'ORTHORHOMBIC' :
        if  (abs(hkl1[0]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[1])) and (abs(hkl1[2]) == abs(hkl2[2])) :
            res = 1
        elif (hkl1[0] == -hkl2[0]) and (hkl1[1] == -hkl2[1]) and (hkl1[2] == -hkl2[2]) :
            res=1
    if exti == 'MONOCLINIC' :
        if  (abs(hkl1[0]) == abs(hkl2[0])) and (abs(hkl1[1]) == abs(hkl2[1])) and (abs(hkl1[2]) == abs(hkl2[2])) :
            res = 1
        elif  ((hkl1[0] == -hkl2[0]) and (hkl1[1] == -hkl2[1]) and (hkl1[2] == -hkl2[2])) :
            res=1
    if exti == 'TRICLINIC' :
        if (hkl1[0] == -hkl2[0]) and (hkl1[1] == -hkl2[1]) and (hkl1[2] == -hkl2[2]) :
            res = 1
        elif (hkl1[0] == hkl2[0]) and (hkl1[1] == hkl2[1]) and (hkl1[2] == hkl2[2]) :
            res = 1

    return res




def b_from_lp (lp):
     #calculates metric matrix from lattice paramteres
    as0=lp[0]
    bs=lp[1]
    cs=lp[2]
    al=lp[3]*DTOR
    be=lp[4]*DTOR
    ga=lp[5]*DTOR
    
    b = np.zeros ((3,3), dtype=np.float32)
    """
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
    """
    b[0,0]=as0
    b[0,1]=0.0
    b[0,2]=0.0
    b[1,0]=bs*math.cos(ga)
    b[1,1]=bs*math.sin(ga)
    b[1,2]=0.0
    b[2,0]=cs*math.cos(be)
    b[2,1]=cs*(math.cos(al)-math.cos(be)*math.cos(ga))/math.sin(ga)
    b[2,2]=cs* math.sqrt(math.sin(ga)**2-(math.cos(al)**2+math.cos(be)**2-\
            2.0*math.cos(al)*math.cos(be)*math.cos(ga)))/math.sin(ga)
    binv = np.linalg.inv (b)
    bs = np.transpose (binv)
    return bs


def dotprod (v, w):
    return np.vdot(v,w)


def vlength(v):
    vecv = np.asarray(v)
    val = np.vdot (vecv,vecv)
    return math.sqrt(val)

def ang (v,w) :
    # calculates  angle between two vectors
    # output in deg.
    return  math.acos(dotprod(w,v)/vlength(v)/vlength(w))*radeg

def lp_from_ub (ub) :
    # ub is a 3 x 3 np array->convert to matrix
    #calculates lattice paramters from ub matrix
    ub = np.asmatrix(ub)
    gs = np.transpose (ub)
    g = np.linalg.inv (gs)
    lp=np.zeros (6,dtype=np.float32)
    lp[0]=math.sqrt(g[0,0])
    lp[1]=math.sqrt(g[1,1])
    lp[2]=math.sqrt(g[2,2])
    lp[3]=math.acos(g[1,2]/(lp[1]*lp[2]))*radeg
    lp[4]=math.acos(g[0,2]/(lp[0]*lp[2]))*radeg
    lp[5]=math.acos(g[0,1]/(lp[0]*lp[1]))*radeg
    # return a 1-d 6 element numpy array
    return lp

# calc volume from lattice parameters
def V_from_lp (lp) :
    b=b_from_lp(lp)
    return V_from_ub(b)

# calc volume from ub matrix, note that ub is a np.matrix
def V_from_ub (ub):
    ub = np.asmatrix (ub, dtype=np.float32)
    gs =  np.transpose (ub) * ub
    g = np.linalg.inv (gs)
    return math.sqrt (np.linalg.det(g))


# calc orientation matrix from ub matrix
def U_from_ub (ub):
    ub= np.asmatrix(ub)
    lp = lp_from_ub(ub)
    B = b_from_lp(lp)
    Binv = np.linalg.inv (B)
    return ub * Binv

def hkl_from_ub_and_xyz (ub, xyz) :
    #calculates miller indices (floating point) from ub matrix and xyz coordinates
    iUB=np.linalg.inv(np.asmatrix(ub))

    hkl=iUB ## np.asmatrix(xyz)
    return hkl

def find_possible_hkls (d1,lp,dtol, hkl):
    il = 0
    res = [0,0,0]
    resArr=[]
    resArr.append(res)
    for i in range(-hkl[0], hkl[0]+1):
        for j in range(-hkl[1], hkl[1]+1):
            for k in range(-hkl[2], hkl[2]+1):
                if i == 0 and j == 0 and k==0 :
                    continue
                hkla = [i,j,k]
                dc = d_from_lp_and_hkl (lp, hkla)
                dd = abs(d1-dc)
                if (dd < dtol) :
                    il = il + 1
                    resArr[0][0] = il
                    resArr.append(hkla)
    return resArr



def flags_from_sym ( sym) :

# Creates a flag vector, based on symmetry for controlling refinement
# INPUT:
#    sym - symmetry code, as in
# OUTPUT:
#    refinement flag vector intarr(6)
#    0 means do not refine, 1 means refine
#------
# Symmetry codes
# 0  - triclinic
# 11 - monoclinic a
# 12 - monoclinic b
# 13 - monoclinic c
# 2  - orthorhombic
# 3  - tetragonal
# 4  - hexagonal
# 5  - cubic



    if sym == 0:
        flags=[0,0,0,0,0,0]
    elif sym == 11:
        flags=[0,0,0,0,1,1]
    elif sym == 12:
        flags=[0,0,0,1,0,1]
    elif sym == 13:
        flags=[0,0,0,1,1,0]
    elif sym == 2:
        flags=[0,0,0,1,1,1]
    elif sym == 3:
        flags=[1,0,1,1,1,1]
    elif sym == 4:
        flags=[1,0,1,1,1,1]
    elif sym == 5:
        flags=[1,0,0,1,1,1]
    else :
        flags =[0,0,0,0,0,0]

    return flags




def syst_extinction ( exti,hkl) :
    h=hkl[0]
    k=hkl[1]
    l=hkl[2]
    if  exti == 'P' or \
        (exti == 'Ro' and (long((-h+k+l)/3.0) == (-h+k+l)/3.0)) or \
        (exti == 'Rr' and (long((h-k+l)/3.0) == (h-k+l)/3.0)) or \
        (exti == 'F' and (long((h+k)/2.0) == (h+k)/2.0) and  (long((k+l)/2.0) == (k+l)/2.0) and  (long((h+l)/2.0) == (h+l)/2.0)) or \
        (exti == 'I' and (long((h+k+l)/2.0) == (h+k+l)/2.0)) or \
        (exti == 'A' and (long((k+l)/2.0) == (k+l)/2.0)) or \
        (exti == 'B' and (long((h+l)/2.0) == (h+l)/2.0)) or \
        (exti == 'C' and (long((h+k)/2.0) == (h+k)/2.0)) :
        return (1)
    return  (0)


def apply_symmetry_to_lp (lp, ch, sym) :
#
# Applies symmetry constraints to lattice parameters, based on change in lp index ch
# INPUT:
#    lp  - lattice parameters vector
#    ch  - index of the changing lp
#    sym - symmetry code
# OUTPUT:
#    lp values re changed to the new ones, compliant with the symmetry
#---------------
# Symmetry codes
# 0  - triclinic
# 11 - monoclinic a
# 12 - monoclinic b
# 13 - monoclinic c
# 2  - orthorhombic
# 3  - tetragonal
# 4  - hexagonal
# 5  - cubic
    lp1=lp[:]

    if sym == 11: # mono a
        lp1[4]=90.0
        lp1[5]=90.0

    if sym == 12: # mono b
        lp1[3]=90.0
        lp1[5]=90.0


    if sym == 13: #  mono c
        lp1[3]=90.0
        lp1[4]=90.0

    if sym == 2: # orthorhombic
        lp1[3]=90.0
        lp1[4]=90.0
        lp1[5]=90.0

    if sym == 3: # tetragonal
        if ch==0:
            lp1[1]=lp1[0]

        if ch == 1:
            lp1[0]=lp1[1]



        lp1[3]=90.0
        lp1[4]=90.0
        lp1[5]=90.0


    if sym == 4: # hexagonal

        if ch == 0:
            lp1[1]=lp1[0]
        if ch == 1:
            lp1[0]=lp1[1]


        lp1[3]=90.0
        lp1[4]=90.0
        lp1[5]=120.0


    if sym == 5: # cubic
        if ch == 0 :
            lp1[1]=lp1[0]
            lp1[2]=lp1[0]
    
        if ch == 1:
            lp1[0]=lp1[1]
            lp1[2]=lp1[1]

        if ch == 2:
            lp1[0]=lp1[2]
            lp1[1]=lp1[2]

        lp1[3]=90.0
        lp1[4]=90.0
        lp1[5]=90.0


    return lp1

def angle_between_hkls (h1, h2, lp) :
    B = b_from_lp (lp)
    x1 = np.dot(h1, B)
    x2 = np.dot(h2, B)
    angle = vector_math.ang_between_vecs(x1, x2)
    return angle

def calc_ub_from_three (hkls, xyzs) :
    xyzs = np.asarray(xyzs).reshape(3,3)
    hkls = np.asarray(hkls).reshape(3,3)
    transH = np.transpose(hkls)
    transX = np.transpose (xyzs)
    x0 = np.dot (transH, xyzs).reshape((3,3))

    h0 = np.dot (transH, hkls).reshape((3,3))
    h0T = np.linalg.pinv (h0)
    x0 = np.dot (x0, h0T)
    return np.transpose (x0).reshape((3,3))


### get_omega -- From xyz and energy  calculates the omega angle (in deg) at which xyz will come
### into diffracting position during omega scan at chi 0
###if diffraction position inaccessible in omega scan returns [-1000,-1000]


def get_omega (en, xyz):
    errArr = [-1000,-1000]
    vlen = vlength (xyz)
    if vlen < 0.000001 :
        d = 1.E9
    else :
        d = 1./ vlength(xyz)
    tthe= tth_from_en_and_d(en, d)
    if tthe == 999 :
        return errArr
    xyz1 = xyz / vlen
    x = xyz1[0]
    y = xyz1[1]
    z = xyz1[2]



    tth = math.cos (math.radians(90. + tthe/2.))
    b1 = (x**2 * y**2 - y**2 * tth**2 + y**4)
    if (b1 < 0.) :
        return errArr
    b2 = (x**2 + y**2)

    a1 = -(x*(x*tth-math.sqrt(b1))/b2 - tth)/ y
    a2 = (x * tth - math.sqrt(b1))/b2
    om1 = math.atan2 (a1, a2)
    a1 = -(x*(x*tth+math.sqrt(b1))/b2 - tth)/ y
    a2 = (x * tth + math.sqrt(b1))/b2
    om2 = math.atan2 (a1, a2)
    return [math.degrees(om1), math.degrees(om2)]


def general_axis (A, vec, en):
    d = 1./vlength(vec)
    ttheta = tth_from_en_and_d(en,d)
    xyz = vec * d
    xyz1 = np.dot ([1,0,0],A)
    #sc = sincos ()

def solve_general_axis (en, xyz, gonio) :
    om = 0
    chi = gonio[4]
    om_mtx = vector_math.generate_rot_mat(3, om)
    chi_mtx = vector_math.generate_rot_mat(3, chi)
    A = np.dot (chi_mtx, om_mtx)
    newaxis = general_axis (np.linalg.inv(A), xyz, en)
    return newaxis


def sincos (a,b,c) :
    delval = -c**2+a**2+b**2
    if (delval < 0.) :
        res=[-1000,-1000]
    else :
        x1 = math.degrees(-2. * math.atan ((a+math.sqrt(delval))/(c-b)))
        x2 = math.degrees(-2. * math.atan ((a-math.sqrt(delval))/(c-b)))
        res =-[x1,x2]
    return res


def open_UB (infile):
    ub = np.zeros((3,3), dtype=np.float32)
    f = open (infile.toLatin1().data(), 'r')
    count = 0
    for line in f :
        vals = line.split ()
        ub[count] = vals
        count += 1
    print ub
    return ub

