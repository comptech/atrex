from math import *
import crystallography
import numpy as np




def generate_rot_mat (axis, angle) :
    dtor = pi / 180.
    s = angle * dtor
    mtx =[[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]]
    Mtx = np.asmatrix(mtx)

    if axis == 1 :
        Mtx[0,0] = 1.
        Mtx[1,1]=cos(s)
   
        Mtx[1,2]=-sin(s)
        Mtx[2,0]=0.0
        Mtx[2,1]=sin(s)
        Mtx[2,2]=cos(s)
          
    if axis ==  2:
        Mtx[0,0]=cos(s)
        Mtx[0,1]=0.0
        Mtx[0,2]=sin(s)
        Mtx[1,0]=0.0
        Mtx[1,1]=1.0
        Mtx[1,2]=0.0
        Mtx[2,0]=-sin(s)
        Mtx[2,1]=0.0
        Mtx[2,2]=cos(s)

    if axis == 3: 
        Mtx[0,0]=cos(s)
        Mtx[0,1]=sin(s)
        Mtx[0,2]=0.0
        Mtx[1,0]=-sin(s)
        Mtx[1,1]=cos(s)
        Mtx[1,2]=0.0
        Mtx[2,0]=0.0
        Mtx[2,1]=0.0
        Mtx[2,2]=1.0

    return Mtx

def ang_between_vecs (vec1, vec2) :
    vec1 = np.asarray(vec1).reshape(3)
    vec2 = np.asarray(vec2).reshape(3)
    #v1 = vec1.reshape(3)
    #v2 = vec2.reshape(3)
    #a = np.dot(vec1, vec2)
    v1 = crystallography.vlength(vec1)
    v2 = crystallography.vlength(vec2)

    a=np.dot(vec1, vec2)/(v1*v2)
    a=abs(acos(a)*180.0/pi)
    return a

### Calculate point of intersection define by point P0 and
### vector line u with a plane defined by a point V0 and vector
### normal n
def line_plane_intersection (u, n, P0, V0):
    P0 = np.asarray(P0)
    V0 = np.asarray(V0)
    u = np.asarray(u).squeeze()
    n = np.asarray(n).squeeze()
    if ang_between_vecs(u,n) == 0 :
        xyz=np.asarray([0.,0.,0.])
    if ang_between_vecs(u,n) == 180. :
        xyz=np.asarray([0.,0.,0.])

    w=P0-V0
    s=-np.dot(n,w)/np.dot(n,u)
    xyz=P0+s*u
    return xyz

def recognize_two_vectors (x1, x2, lp, dtol, angtol):
    d1 = 1./ crystallography.vlength(x1)
    d2 = 1./ crystallography.vlength(x2)
    hkls1 = crystallography.find_possible_hkls(d1,lp,dtol,[10,10,10])
    hkls2 = crystallography.find_possible_hkls(d2,lp,dtol, [10,10,10])
    meas_ang = ang_between_vecs(x1, x2)
    num_1 = hkls1[0][0]
    num_2 = hkls2[0][0]
    a = (num_1-1) * (num_2-1)
    ch = np.zeros(a, dtype=np.float32)
    ij = np.zeros((2,a), dtype=np.int16)
    if (num_1 !=0 and num_2 != 0) :
        for i in range (1, num_1-2) :
            for j in range (1, num_2-2) :
                ij[:, (i-1)* (num_2-1)+j-1]=[i,j]
                ch[(i-1)* (num_2-1)+j-1]= crystallography.angle_between_hkls(hkls1[:][i], hkls2[:][j], lp)
    ch1 = min (abs(ch-meas_ang))
    w = np.argmin (abs(ch-meas_ang))
    hkl1 = hkls1[:][ij[0,w]]
    hkl2 = hkls2[:][ij[1,w]]
    angerr = ch1
    if (angerr < angtol) :
        return [1,hkl1, hkl2]
    return [0,[0,0,0], [0,0,0]]



def UB_from_two_vecs_and_lp (x1, x2, hkl1, hkl2, lp) :
    B =crystallography.b_from_lp (lp)
    hkl3 = np.cross (hkl1, hkl2)

    x3 = np.cross (x1,x2)
    #x3 = np.asarray ((x3),dtype=np.float64)
    len_x3 = crystallography.vlength(x3)
    if (len_x3 < 1.E-8) :
        len_x3 = 1.E-8
    x3 /= len_x3
    d0 = crystallography.d_from_lp_and_hkl (lp, hkl3)
    x3 = x3 / d0
    xyzs = [np.asarray([x1]),np.asarray([x2]),np.asarray([x3])]
    hkls = [np.asarray([hkl1]), np.asarray([hkl2]), np.asarray([hkl3])]
    ub = crystallography.calc_ub_from_three (hkls, xyzs)
    return ub




