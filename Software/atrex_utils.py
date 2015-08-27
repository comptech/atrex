from math import *
from PyQt4 import QtCore

def mySquare (val) :
    return (sqrt(val))

"""Function will take the name of an image file and then get
the range of images that associate with that image name. """
def getImageRange (imageDir, imstring) :
    # get the index of the start of the .txt suffix then
    # find the start of the _xxx where xxx are the image numbers
    
    qd = QtCore.QDir (imageDir)
    
    qd.setNameFilters (QtCore.QStringList()<<"*.tif")
    filelist = qd.entryList()
    nfiles = filelist.count()
    min = 1e6
    max = -1e6
    lastind = imstring.lastIndexOf('.tif')-3
    firstind = imstring.lastIndexOf ("/")
    if (firstind <0) :
        firstind = imstring.lastIndexOf('\\')
    firstind = firstind + 1
    matchstring = imstring.mid(firstind, lastind-firstind)
    print 'Debug : Matchstring = ',matchstring
    for i in range(nfiles) :
        print filelist[i]
        if not (filelist[i].contains(".tif")) :
            continue 
        if (filelist[i].contains (matchstring)) :
             
            print i, 'made it'
            tmpind = filelist[i].lastIndexOf (".tif")
            str = filelist[i].mid(tmpind-3,3)
            val = str.toInt()
            print val[0]
            if (val[0] > max) :
                max = val[0]
            if (val[0] < min) :
                min = val[0]
    print 'Min max are : ', min, max
    tmpind = imstring.lastIndexOf (".tif")
    str = imstring.mid(tmpind-3,3)
    val = str.toInt()
    minmax = [min, max, val[0]]
    return minmax




