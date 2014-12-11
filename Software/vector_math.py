from math import *
from crystallography import *



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
    a=dotprod(vec1, vec2)/(vlength(vec1)*vlength(vec2))
    a=abs(acos(a)*180.0/pi)
    return a
