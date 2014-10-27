import myPeakTable
import numpy as np
from math import *

class myPeakSearch:

    def __init__(self):
        threshold = 0.0
        pbox      = 0
        bbox      = 0
        mindist   = 0L
        peaktable = myPeakTable()

    
    def execute (self, oimage, oad, excl, butt,  show_progress_bar):
        thr=self.threshold                       # 100:       raw counts threshold for locating peaks
        max_peak_size=self.mindist               # 10:        max allowed peak size with pixels above local background + Imin
        num_of_segments = [self.pbox,self.pbox]  # [50.,50.]: number of segments in X and Y for local labckground estimation
        perc=self.bbox                           # 1.0:       percent of median for background
        topX=long(im.sts.adet.nopixx/oimage.sts.binning)-1
        topY=long(im.sts.adet.nopixy/oimage.sts.binning)-1

        img1=congrid(im.img, 1000,1000)
        ff=where(img1 gt 10)
        ;h=histogram(img1, locations=xs, min=20, max=50000, nbins=1000)
        ;m=max(h,kk)
        ;print, 'histogram max: ', xs[kk]
        print, 'median: ', median(img1[ff])
        ; window
        ; plot, xs, h, xrange=[0,1000]

        bg=estimate_local_background(num_of_segments[0], num_of_segments[1], img1,  median(img1[ff]), 1.0)
        w=where(img1-bg gt 100.)
        paint_peaks, w, 1000, 1000
        w0=n_elements(w)
        if show_progress_bar then $
            begin
            cgProgressBar = Obj_New("CGPROGRESSBAR", /Cancel)
            cgProgressBar -> Start
        oo:
        w=where(img1-bg gt thr)
        if w[0] ne -1 then $
            XY=ARRAY_INDICES([1000,1000], w[0], /DIMENSIONS)
            aa=grow_peak(img1, bg, xy[0],xy[1], thr, 1000, 1000)
            if max([aa[1]-aa[0], aa[3]-aa[2]]) lt 10 then $
                ref_peak.DetXY=[aa[4]*topX/1000.,aa[5]*topY/1000.]
                ref_peak.IntAD[0]=img1[aa[4],aa[5]]
                ref_peak.gonio=im.sts.gonio
                ref_peak.Selected[1]=1
                ref_peak.Selected[0]=0
                pt->Appendpeak, ref_peak
            endif
            img1[aa[0]:aa[1],aa[2]:aa[3]]=0

    if show_progress_bar then $
    begin
        if cgProgressBar -> CheckCancel() THEN BEGIN
            ok = Dialog_Message('The user cancelled operation.')
            cgProgressBar -> Destroy
            RETURN
            endif
        ENDIF
        if show_progress_bar then cgProgressBar -> Update, 100.0-(n_elements(w)/float(w0))*100.0
        goto,oo
    end

    ptc=pt->get_object()
    self.peaktable=ptc
    obj_destroy, pt
    if show_progress_bar then $
        cgProgressBar -> Destroy
    print, 'Initial number of points:',w0
    print, 'Computation time: ',systime(/seconds)-t0
end



;---------------------------------------------------------------
