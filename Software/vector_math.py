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
    vec1 = np.asarray(vec1).reshape(3)
    vec2 = np.asarray(vec2).reshape(3)
    #v1 = vec1.reshape(3)
    #v2 = vec2.reshape(3)
    #a = np.dot(vec1, vec2)
    a=np.dot(vec1, vec2)/(vlength(vec1)*vlength(vec2))
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

