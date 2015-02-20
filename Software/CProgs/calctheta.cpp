#include <math.h>
#include <stdio.h>

#ifdef __linux__
#define PI M_PI
extern "C" {
void testPyth (int *, int) ;
int create_theta_array (int *sizeArr, float detDist, float *beam, float *psize, 
	float *tiltmtx, float *tth, float *gonio,  float *outTheta, float minBin, float binsize,
	unsigned short *outThetaBin) ;
    void integrate (int *sizeArr, unsigned short *inarr, float *tthetaArr, float *histo, float *histoParams, float *beam) ;
    void integrate_cake (int *sizeArr, float *beam, unsigned short *inarr, float *tthetaArr,float *cakeArr, float *histoParams) ;
}

#else
#define PI  3.14149265359
extern "C" {
__declspec(dllexport) void testPyth (int *, int) ;
__declspec(dllexport) int create_theta_array (int *sizeArr, float detDist, float *beam, float *psize, 
	float *tiltmtx, float *tth, float *gonio,  float *outTheta, float minBin, float binsize,
	unsigned short *outThetaBin) ;
__declspec(dllexport) void integrate (int *sizeArr, unsigned short *inarr, float *tthetaArr, float *histo, float *histoParams, float *beam) ;
__declspec(dllexport) void integrate_cake (int *sizeArr, float *beam, unsigned short *inarr, float *tthetaArr,float *cakeArr, float *histoParams) ;
}

#endif
#define rad2deg 180./PI


/* for debugging tests

int main (int argc, char *argv[]) {
	float tiltmtx[] = {.993, .035, .000071, -.03, 
		.993, .00001, 7.E-5, 1.3E-6, .9999} ;
	float tth[] = {1,0,0,0,1,0,0,0,1} ;
	int sizeArr[]= {2048,2048} ;
	float gonio[] = {0.,0.,0} ;
	float beamXY[] = {1021.01,1024.69} ;
	float psizeXY[] = {.079, .079} ;

	float *outTheta = new float [2048*2048] ;
	unsigned short *outBin = new unsigned short [2048 * 2048] ;


	create_theta_array (sizeArr, 207., beamXY, psizeXY, tiltmtx, tth, gonio, outTheta, 0., .1, outBin) ;

	FILE *fout = fopen ("testtth","w") ;
	fwrite ((char *)outTheta, 4, 2048 * 2048, fout) ;
	fclose (fout) ;

	delete [] outBin ;
	delete [] outTheta ;

}
*/


int create_theta_array (int *sizeArr, float detDist, float *beam, float *psize, float *tiltmtx, float *tth, float *gonio,
    float *outTheta, float minBin, float binsize, unsigned short *outThetaBin) {


    int binval ;
	int i, j, is, js, xsize, ysize, x2, y2 ;
	float fval, beamX, beamY, psizeX, psizeY, xdist2, ydist2, dist, xrel, yrel, sum;
	float sd0[] = {1., 0., 0.} ;
	float vec1[] = {0.,0.,0.} ;
	float vec2[] = {0.,0.,0.} ;
	float vec3[] = {0.,0.,0.} ;
	float len0, len1, dotsum ;

	//float *tiltmtx = new float [3 * 3] ;
	xsize = sizeArr[0] ;
	ysize = sizeArr[1] ;
	beamX = beam[0] ;
	beamY = beam[1] ;
	psizeX = psize[0] ;
	psizeY = psize[1] ;

	// size in pixels from center to edge 
	x2 = xsize / 2 ;
	y2 = ysize / 2 ;

	printf ("sizeArr : %d %d\r\n", xsize, ysize) ;
	printf ("detDist : %f\r\n", detDist) ;
	printf ("beam : %f %f\r\n", beamX, beamY) ;
	printf ("psize : %f %f\r\n", psizeX, psizeY) ;
	

	for (i=0; i<xsize; i++) {
			ydist2 = ((i-beamY)*(i-beamY)) ;
		for (j=0; j<ysize; j++) {
			outTheta[i*xsize+j] = 0. ;
			outThetaBin[i*xsize+j]=0 ;
			xdist2 = ((j-beamX)*(j-beamX)) ;
			dist = sqrt (xdist2 + ydist2) ;
			if (dist > y2) continue ;
			xrel = -1. * (j-beamX) * psizeX ;
			yrel = (i-beamY) * psizeY ;
			vec1[0] = 0. ;
			vec1[1] = xrel ;
			vec1[2] = yrel ;
			// 1x3  * 3x3 mat multiply
			for (is=0; is<3; is++) {
				sum = 0. ;
				for (js=0; js<3; js++) {
					sum += vec1[js] * tiltmtx[js * 3 + is] ;

				}
				vec2[is] = sum ;
			}
			vec2[0] += detDist ;
			for (is=0; is<3; is++) {
				sum = 0. ;
				for (js=0; js<3; js++) {
					sum += vec2[js] * tth[js * 3 + is] ;
				}
				vec3[is] = sum ;
			}
			// get the angle between vec3 and sd0
			len0= 0. ;
			len1 = 0. ;
			dotsum=0.;
			for (is=0; is<3; is++) {
				len0 += vec3[is]*vec3[is] ;
				len1 += sd0[is] * sd0[is] ;
				dotsum += vec3[is] * sd0[is] ;
			}
			len0 = sqrt(len0) * sqrt(len1) ;
			fval = fabs (acos(dotsum/len0)) * 180. / PI ;
			outTheta[i*xsize+j] = fval ;
			binval = (int)((fval - minBin) / binsize) ;
			if (binval < 0) binval = 0 ;
			outThetaBin[i*xsize+j] = (unsigned short) binval ;

		}


		 
	}
	return 1 ;
}


void integrate (int *sizeArr, unsigned short *inarr, float *tthetaArr, float *histo, float *histoParams, float *beam) {

	int i, j, ns, nl, ns2, npix, bin, nbins ;
	ns = sizeArr[0] ;
	nl = sizeArr[1] ;
	ns2 = ns / 2 ;

	float minval, maxval, binsize ;
	float xdist, ydist, dist, fval ;

	

	minval = histoParams[0] ;
	maxval = histoParams[1] ;
	binsize = histoParams[2] ;


	nbins = histoParams[3] ;

    printf ("Integrating min max bin %f  %f %f",  minval, maxval, binsize) ;


	int *bincnt = new int [nbins] ;

	for (i=0; i<nbins; i++) {
		histo[i] = 0. ;
		bincnt[i] = 0 ;
	}

	for (i=0; i< nl; i++) {
		ydist = i - beam[1] ;
		for (j=0; j<ns; j++) {
			xdist = j - beam[0]  ;
			dist = sqrt (xdist * xdist + ydist * ydist) ;
			if (dist > ns2) continue ;
			fval = tthetaArr[i * ns+j] ;
			bin = (int)((fval - minval) / binsize) ;
			if (bin < 0) bin = 0 ;
			if (bin > nbins) bin=nbins-1 ;
			histo[bin] += inarr[i*ns+j] ;
			bincnt[bin]++ ;
		}
	}

	for (i=0; i<nbins; i++) histo[i] /= bincnt[i] ;

	delete [] bincnt ;
}


void integrate_cake (int *sizeArr, float *beam,  unsigned short *inarr, float *tthetaArr, float *cakeArr, float *histoParams) {

	int i, j, ns, nl, ns2, npix, bin, nbinsTth, nbinsAz, nbinsTot ;
	int azbin, tthbin, pixnum ;
	ns = sizeArr[0] ;
	nl = sizeArr[1] ;
	ns2 = ns / 2 ;

	// 2-theta min, max, spacing and binsize
	float minvalTth, maxvalTth, binsizeTth, binsizeAz ;
	// azimuth runs -180. to 180., we are given the number of azimuth bins

	float xdist, ydist, dist, tthval, azval ;



	minvalTth = histoParams[0] ;
	maxvalTth = histoParams[1] ;
	binsizeTth = histoParams[2] ;
	nbinsTth = histoParams[3] ;
    nbinsAz = (int) histoParams[4] ;
    binsizeAz = 360. / nbinsAz ;
	nbinsTot = (int) (nbinsAz * nbinsTth) ;

	int *bincnt = new int [nbinsTot] ;

    // initialize arrays to 0
	for (i=0; i<nbinsTot; i++) {
		cakeArr[i] = 0. ;
		bincnt[i] = 0 ;
	}

	for (i=0; i< nl; i++) {
		ydist = beam[1] - i;
		for (j=0; j<ns; j++) {
			xdist = j - beam[0] ;
			dist = sqrt (xdist * xdist + ydist * ydist) ;
			if (dist > ns2) continue ;
			tthval = tthetaArr[i * ns+j] ;
			tthbin = (int)((tthval - minvalTth) / binsizeTth) ;
			azval = atan2 (xdist, ydist) * rad2deg ;

		    if (azval > 0)
		    	azbin = (int)((azval) / binsizeAz) ;
		    else
		        azbin = (int)((azval+360.) / binsizeAz) ;
			if (tthbin < 0) tthbin = 0 ;
			if (tthbin > nbinsTth) tthbin=nbinsTth-1 ;
			if (azbin < 0) azbin = 0 ;
			if (azbin > nbinsAz) azbin=nbinsAz-1 ;

			pixnum = azbin * nbinsTth + tthbin ;
			bincnt[pixnum]++ ;
			cakeArr [pixnum] += inarr [ i * ns + j] ;

			if (i==500 && j==500){
			    printf ("%d  %d  : %f %f %d %d\r\n", i, j, tthval, azval, tthbin, azbin) ;
			}
			if (i==1500 && j==500){
			    printf ("%d  %d  : %f %f %d %d\r\n", i, j, tthval, azval, tthbin, azbin) ;
			}
			if (i==500 && j==1500){
			    printf ("%d  %d  : %f %f %d %d\r\n", i, j, tthval, azval, tthbin, azbin) ;
			}
			if (i==1500 && j==1500){
			    printf ("%d  %d  : %f %f %d %d\r\n", i, j, tthval, azval, tthbin, azbin) ;
			}
		}
	}

	for (i=0; i<nbinsTot; i++) {
	    if (bincnt[i]<1) continue ;
	    cakeArr[i] /= bincnt[i] ;
	}

	delete [] bincnt ;
}







extern "C" void testPyth(int *arrs, int num) {
	int i ;
	for (i=0; i<num; i++) {
		printf ("arrs %d : %d\r\n", i, arrs[i]) ;
	}

}

void generateR(int axis, float ang, float *arr){

	switch (axis) {
		case 1:
			arr[0] = 1. ;
			arr[1] = 0. ;
			arr[2] = 0. ;
			arr[3] = 0. ;
			arr[4] = cos(ang) ;
			arr[5] = -sin(ang) ;
			arr[6] = 0. ;
			arr[7] = sin(ang) ;
			arr[8] = cos(ang) ;
			break ;
		case 2:
			arr[0] = cos(ang) ;
			arr[1] = sin(ang) ;
			arr[2] = 0. ;
			arr[3] = -sin(ang) ;
			arr[4] = cos(ang) ;
			arr[5] = 0. ;
			arr[6] = 0. ;
			arr[7] = 0. ;
			arr[8] = 1. ;
			break ;
	}
}

	
	
	

	


