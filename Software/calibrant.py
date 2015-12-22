##
# calibrant.py
# contains the calibrant functions for generating the response based upon a calibrant powder
##
import math
import numpy as np

def LaB6 (dst, wh, wv) :
    N=48
    la=wv
    d = np.zeros (N, dtype=np.float32)
    tth = np.zeros(N, dtype=np.float32)
    rad = np.zeros (N, dtype=np.float32)
    
    d[0]=   4.1565  
    d[1]=   2.9391  #   0   1   1
    d[2]=   2.3997  #   1   1   1
    d[3]=   2.0782  #   0   0   2
    d[4]=   1.8588  #   0   1   2
    d[5]=   1.6969  #   1   1   2
    d[6]=   1.4695  #   0   2   2
    d[7]=   1.3855  #   0   0   3
    d[8]=   1.3855  #   1   2   2
    d[9]=   1.3144  #   0   1   3
    d[10]=  1.2532  #   1   1   3
    d[11]=  1.1999  #   2   2   2
    d[12]=  1.1528  #   0   2   3
    d[13]=  1.1109  #   1   2   3
    d[14]=  1.0391  #   0   0   4
    d[15]=  1.0081  #   0   1   4
    d[16]=  1.0081  #   2   2   3
    d[17]=  0.9797  #   1   1   4
    d[18]=  0.9797  #   0   3   3
    d[19]=  0.9536  #   1   3   3
    d[20]=  0.9294  #   0   2   4
    d[21]=  0.9070  #   1   2   4
    d[22]=  0.8862  #   2   3   3
    d[23]=  0.8484  #   2   2   4
    d[24]=  0.8313  #   0   0   5
    d[25]=  0.8313  #   0   3   4
    d[26]=  0.8152  #   0   1   5
    d[27]=  0.8152  #   1   3   4
    d[28]=  0.7999  #   1   1   5
    d[29]=  0.7999  #   3   3   3
    d[30]=  0.7718  #   0   2   5
    d[31]=  0.7718  #   2   3   4
    d[32]=  0.7589  #   1   2   5
    d[33]=  0.7348  #   0   4   4
    d[34]=  0.7235  #   2   2   5
    d[35]=  0.7235  #   1   4   4
    d[36]=  0.7128  #   0   3   5
    d[37]=  0.7128  #   3   3   4
    d[38]=  0.7026  #   1   3   5
    d[39]=  0.6927  #   0   0   6
    d[40]=  0.6927  #   2   4   4
    d[41]=  0.6833  #   0   1   6
    d[42]=  0.6743  #   1   1   6
    d[43]=  0.6743  #   2   3   5
    d[44]=  0.6572  #   0   2   6
    d[45]=  0.6491  #   1   2   6
    d[46]=  0.6491  #   0   4   5
    d[47]=  0.6491

    
    for i in range (N) :
        tth_rads= (2. * math.asin(la/(2. * d[i])))
        tth[i] = math.degrees (tth_rads)
        rad[i] = dst * math.tan(tth_rads)
    if (wh ==0) :
        return rad
    return d

def CeO2 (dst, wh, wv) :
    N=25
    la=wv
    d = np.zeros (N, dtype=np.float32)
    tth = np.zeros(N, dtype=np.float32)
    rad = np.zeros (N, dtype=np.float32)
    d[0] =3.12442
    d[1] =2.70583
    d[2] =1.91331
    d[3] =1.63167
    d[4] =1.56221
    d[5] =1.35291
    d[6] =1.24152
    d[7] =1.21008
    d[8] =1.10465
    d[9] =1.04147
    d[10]=0.95665
    d[11]=0.91474
    d[12]=0.90194
    d[13]=0.85566
    d[14]=0.82527
    d[15]=0.81584
    d[16]=0.78110
    d[17]=0.75778
    d[18]=0.75046
    d[19]=0.72316
    d[20]=0.70454
    d[21]=0.67646
    d[22]=0.66114
    d[23]=0.65626
    d[24]=0.63777

    for i in range (N) :
        tth_rads= (2. * math.asin(la/(2. * d[i])))
        tth[i] = math.degrees (tth_rads)
        rad[i] = dst * math.tan(tth_rads)
    if (wh ==0) :
        return rad
    return d

def CO2 (dst, wh, wv) :
    N=21
    la=wv
    d = np.zeros (N, dtype=np.float32)
    tth = np.zeros(N, dtype=np.float32)
    rad = np.zeros (N, dtype=np.float32)

    d[0]=2.87261
    d[1]=2.48775
    d[2]=2.22511
    d[3]=2.03124
    d[4]=1.7591
    d[5]=1.6585
    d[6]=1.4363
    d[7]=1.37996
    d[8]=1.32976
    d[9]=1.24388
    d[10]=1.20674
    d[11]=1.14146
    d[12]=1.08574
    d[13]=1.06078
    d[14]=1.01562
    d[15]=0.92393
    d[16]=0.9084
    d[17]=0.87955
    d[18]=0.84101
    d[19]=0.82925
    d[20]=0.80713

    for i in range (N) :
        tth_rads= (2. * math.asin(la/(2. * d[i])))
        tth[i] = math.degrees (tth_rads)
        rad[i] = dst * math.tan(tth_rads)
    if (wh ==0) :
        return rad
    return d


def Neon (dst, wh, wv) :
    N=11
    la=wv
    d = np.zeros (N, dtype=np.float32)
    tth = np.zeros(N, dtype=np.float32)
    rad = np.zeros (N, dtype=np.float32)

    d[0] =  2.10560
    d[1] =  1.82350
    d[2] =  1.28941
    d[3] =  1.09961
    d[4] =  1.05280
    d[5] =  0.91175
    d[6] =  0.83668
    d[7] =  0.81549
    d[8] =  0.74444
    d[9] =  0.70187
    d[10] = 0.64470

    for i in range (N) :
        tth_rads= (2. * math.asin(la/(2. * d[i])))
        tth[i] = math.degrees (tth_rads)
        rad[i] = dst * math.tan(tth_rads)
    if (wh ==0) :
        return rad
    return d