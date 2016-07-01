#locmax.py 
# returns a local maxima image given an input numpy array 
import numpy as np

def imgfrm (img, vald) :
    val = vald
    nv = count (val)
    (ny,nx) = img.shape
    for i in range (nv) :
        T=np.zeros(nx-2*i) + val[i]



def locmax (img, mtp,  ix, iy, noedge=False, sort=False) :
    print 'MTP :', mtp
    fuzz = 1.E-8
    #fuzz = 300

    #dx1 = np.roll(img, 1, 1) + mtp
    #dx2 = np.roll(img, -1, 1) + mtp
    dx1 = np.roll (img, 1,1)
    dx2 = np.roll (img, -1,1)
    dy1 = np.roll(img, 1, 0)
    dy2 = np.roll(img, -1, 0)
    i0 = img > (dx1+mtp)
    i1 = img > (dx2+mtp)
    i2 = img > (dy1+mtp)
    i3 = img > (dy2+mtp)
    land = i0 * i1 * i2 * i3
    #landx = np.logical_and(img>dx1, img>dx2)
    #landy = np.logical_and(img>dy1, img>dy2)
    #land = np.logical_and (landx, landy)

    w = np.where (land > 0)
    nMax = w[0].size
    print "number of maxima : ",w[0].size

    if nMax > 0 :
        # get array of the max points
        fzz = img[w[0], w[1]]
        # find those less than fuzz
        wfzz = np.where (fzz < fuzz)
        #false them
        c = wfzz[0].size
        if (c > 0) :
            print c
            land[w[0][wfzz],w[1][wfzz]] = False
            w = np.where (land== True)
            nMax = w[0].size

	
    if nMax > 0 :
        v = img [w[0],w[1]]

    #if sort :
    #   isrt = np.argsort (v)
    #isrt = isrt[::-1]


    for i in range (w[0].size) :
        ix.append (w[1][i])
        iy.append (w[0][i])
    #iy = w[0]
    return v

		
