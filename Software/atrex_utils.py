from math import *
from fnmatch import *
from PyQt5.QtCore import *

def mySquare (val) :
    return (sqrt(val))

"""Function will take the name of an image file and then get
the range of images that associate with that image name. """
def getImageRange (imageDir, imstring) :
    # get the index of the start of the .txt suffix then
    # find the start of the _xxx where xxx are the image numbers
    
    qd = QDir (imageDir)
    tifstr = '*.tif'
    #qd.setNameFilters (QStringList()<<"*.tif")
    #filelist = qd.entryList()
    #qd.setNameFilters ([imstringFilt])
    imfiles0 = qd.entryList()
    filelist = []
    for nm in imfiles0 :
        #nm = '%s/%s'%(apath,nm)
        if fnmatch (nm, tifstr) :
            filelist.append(nm)
    
    
    nfiles = len(filelist)
    min = 1e6
    max = -1e6
    
    lastind = find_last_index_of (imstring,'.tif')-3
    firstind = find_last_index_of (imstring,'/')
    if (firstind <0) :
        firstind = find_last_index_of (imstring,'\\')
        
    firstind = firstind + 1
    matchstring = imstring[firstind: lastind]
    print 'Debug : Matchstring = ',matchstring
    for i in range(nfiles) :
        print filelist[i]
        loc = filelist[i].rfind('.tif')
        if (loc <0) :
            continue
        
        if (filelist[i].rfind(matchstring) >=0) :
             
            print i, 'made it'
            tmpind = find_last_index_of (filelist[i],".tif")
            str = filelist[i][tmpind-3:tmpind]
            val = int(str)
            print val
            if (val > max) :
                max = val
            if (val < min) :
                min = val
    print 'Min max are : ', min, max
    tmpind = find_last_index_of(imstring,'.tif')
    str = imstring[tmpind-3:tmpind]
    val = int(str)
    minmax = [min, max, val]
    return minmax




def find_last_index_of (s, t) :

    last_pos = -1
    while True:
        pos = s.find(t, last_pos + 1)
        if pos == -1:
            return last_pos
        else:
            last_pos = pos