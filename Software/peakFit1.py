
import numpy
import math
from scipy.optimize import curve_fit

def gaussfit1d (x,y,p):
    #coeff, cov = curve_fit (gauss, x,y,p)
    coeff,cov = curve_fit (gauss,x,y,p)
    return coeff

def gauss(x, A, mu, sigma):
   #print 'in gauss P is :', p
   A, mu, sigma = p
   return A*numpy.exp(-(x-mu)**2/(2.*sigma**2))


x = numpy.linspace(-5,5,11)
p=[1.,-3.,2.]
sec=gauss(x,*p)



#y=sec
#n=len(sec)
#mean = sum(x*y)                  #note this correction
#sigma = sum(y*(x-mean)**2)        #note this correctionmean = sum(x*y)/n
#p0=[1.,mean,sigma]
#p0=[1.,0.,0]
#popt = gaussfit1d (x,sec,p0)
#print popt
#newgauss = gauss (x, popt[0],popt[1], popt[2])
#print newgauss

#print popt

