from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import numpy as np

class MyGLWindow (QOpenGLWidget) :


    def __init__(self,parent):
        QOpenGLWidget.__init__(self,parent)

        self.setpts = False
        self.rotx = 0.
        self.roty = 0.
        self.scalfac = 1.
        self.lastx = -10 #-10 for gluPerspective
        self.curpos =0.
        self.selFlag = False
        self.selx = 0
        self.sely = 0
        self.lookAxis = 0
        self.makearray()
        """ 
        boxSelectMode - 0-off, 1-active, loooking for upper left, 2 -looking to close
        """
        self.boxSelectMode = 0
        self.upleft = QPoint(0,0)
        self.botright= QPoint(0,0)
        self.boxRect = [0,0,0,0]




    def resizeGL (self, width, height) :
        super(MyGLWindow,self).resizeGL(width,height)
        glViewport (0,0,width,height)
        glMatrixMode (GL_PROJECTION)
        #glOrtho (-2, 2,-2, 2, -2,2)
        gluPerspective (45,float(width)/float(height),1.,20)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()
        #glPushMatrix()
        #gluLookAt (1.,0.,0.,0.,0.,0.,0,1,0)
        glDisable(GL_LIGHTING)
        glEnable (GL_DEPTH_TEST)
        glClearColor (0.1,0.1,.35,0)


    def initializeGL(self):
        super(MyGLWindow,self).initializeGL()
        #glClearColor (0,0,.4,0)


    def mousePressEvent (self, ev) :
        #print (ev.button())
        #print ("start the selection")
        x = ev.x()
        y = ev.y()
        if ev.button() == 2 :
            #a= (GLuint*10)(0)
            #glReadBuffer (GL_FRONT)
            #glPixelStorei (GL_PACK_ALIGNMENT,1)
            #glReadPixels (0, 0,1,1,GL_RGBA, GL_UNSIGNED_INT,a)
            #print (a[0])
            self.selFlag = True
            self.selx = x 
            self.sely = y
        else :
            if (self.boxSelectMode == 1) :
                self.upleft = QPoint (x,y)
                self.boxSelectMode = 2
                self.lastx = x
                self.lasty = y
            



    def mouseMoveEvent (self, ev):
        x = ev.pos().x()
        y = ev.pos().y()
        if (self.lastx > 0 and self.boxSelectMode ==0) :
            ydiff = y - self.lasty
            xdiff = x - self.lastx
            self.roty = self.roty + xdiff / 10.
            self.rotx = self.rotx + ydiff / 10.
        self.lastx = x
        self.lasty = y

    def makearray(self):
        xs = np.random.normal(0., .5, 10)
        ys = np.random.normal(0., 0.5, 10)
        zs = np.random.normal(0., 0.5, 10)
        print (xs[0], ys[0], zs[0])
        print(xs[1], ys[1], zs[1])
        self.setVals(xs, ys, zs)

    def mouseReleaseEvent (self,ev) :
        if (ev.button() != 1) :
            return
        x = ev.x()
        y = ev.y()
        x0 = self.upleft.x()
        w0 = x - x0
        if (w0 < 0) :
            x0 = x
            w0 = -1 * w0
        y0 = self.upleft.y()
        h0 =  y0 - y
        if (h0<0) :
            y0 = y
            h0 = -1 * h0

        if (self.boxSelectMode == 2):
            self.boxSelectMode = 0
            self.selFlag = True
            #self.setBoxExclude (self.upleft, self.botright)
            self.boxRect = [x0, y0, w0, h0]

        print x0,y0,w0,h0
            


    def wheelEvent (self, ev) :
        x = ev.angleDelta().y()

        self.curpos = float(x)/120  +  self.curpos
        print('angle :', float(x) / 120)


    def paintGL (self) :
        npts = self.myx.size
        
        q = gluNewQuadric()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if (self.selFlag) :
            ww = self.botright.x() - self.upleft.x()
            hh = self.botright.y() - self.upleft.y()
            #glScissor (self.upleft.x(),self.upleft.y(),ww, hh)
            glScissor (self.boxRect[0],self.height()-self.boxRect[1], self.boxRect[2], self.boxRect[3])
            #print self.boxRect[0],self.boxRect[1],self.boxRect[2], self.boxRect[3]
            glEnable (GL_SCISSOR_TEST)
            glDisable (GL_DEPTH_TEST)
            
            glGenQueries (npts,self.queryIDs)
            
            #glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)

        #glColor3f(1, 1, 0)
        myellow = [1,1.,0.,1.]
        mygreen = [0,1,0.,1.]
        #glEnable (GL_SCISSOR_TEST)
        
        glLoadIdentity()
        
        if (self.lookAxis==0) :
            gluLookAt (5.,0.,0.,0.,0.,0.,0.,1.,0.)
        if (self.lookAxis==1) :
            gluLookAt (0.,5.,0.,0.,0.,0.,1.,0,0.)
        if (self.lookAxis==2) :
            gluLookAt (0.,0.,5.,0.,0.,0.,0.,1.,0.)
        
        #glPushMatrix ()
        if (self.setpts) :
            npts = self.myx.size
            glTranslatef(0.0, 0.0, self.curpos)

            glRotatef(self.rotx, 1., 0., 0)
            glRotatef(self.roty, 0., 1., 0)
            #glColor3f(0.,0.,1.)
            #glScalef (self.scalfac, self.scalfac, self.scalfac)
            #glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1,0.,0,1])
            self.drawAxes()
            for i in range(npts) :
                #glPushMatrix()
                if (self.usePeaks[i] ==0) :
                    continue
                if (self.selFlag):
                    glBeginQuery (GL_SAMPLES_PASSED,self.queryIDs[i])
                #if i==1 :
                #     glColor3f(0.,1.,0)
                    #glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, mygreen)
                glTranslatef(self.myx[i], self.myy[i], self.myz[i])
                glLoadName (i)
                glColor3f(1.,1.,0.)
                gluSphere(q,.015,36,36)
                glTranslatef(-self.myx[i], -self.myy[i], -self.myz[i])
                #glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, myellow)
                if (self.selFlag):
                   glEndQuery (GL_SAMPLES_PASSED)
                #glPopMatrix()
                 #print queryIDs[i]
        else :
            glBegin(GL_TRIANGLES);
            glVertex3f(-0.5, -0.5, 0);
            glVertex3f(0.5, -0.5, 0);
            glVertex3f(0.0, 0.5, 0);
            glEnd()
            


        #glPopMatrix()
        #glLoadIdentity()
        """
        if (self.lookAxis==0) :
            gluLookAt (1.,0.,0.,0.,0.,0.,0.,1.,0.)
        if (self.lookAxis==1) :
            gluLookAt (0.,1.,0.,0.,0.,0.,0.,1.,0.)
        if (self.lookAxis==2) :
            gluLookAt (0.,0.,1.,0.,0.,0.,0.,1.,0.)
        """    
            
        #gluPerspective(45, float(self.width()) / self.height(), 0.1, 50.0)
        #glTranslatef(0.0,0.0, self.curpos)
        
       
        if (self.selFlag) :
            glDisable (GL_SCISSOR_TEST)
            self.selFlag = False
            for k in range (npts) :
                if (self.usePeaks[k] == 0) :
                    continue
                val = glGetQueryObjectiv(self.queryIDs[k], GL_QUERY_RESULT)
            
                
                if (val > 0) :
                    self.usePeaks[k] = 0
            glDeleteQueries (npts, self.queryIDs)

        if (self.boxSelectMode == 2) :         
            sx = self.upleft.x()
            sy = self.upleft.y()
            qp = QPainter ()
            qp.begin(self)
            qp.setPen (Qt.yellow)
            qp.drawRect (sx, sy, self.lastx-sx, self.lasty-sy)
            qp.end()



    def drawAxes (self) :
        glLineWidth (1.)
        glColor3f (0.,1.,1.)
        glBegin (GL_LINES)
        glVertex3f(0.,0.,0.)
        glVertex3f(0.,0.2,0.)
        glEnd()
        glBegin (GL_LINES)
        glColor3f (1.,1.,0.)
        glVertex3f(0.,0.,0.)
        glVertex3f(0.2,0.0,0.)
        glEnd()
        glBegin (GL_LINES)
        glColor3f (1.,0.,0.)
        glVertex3f(0.,0.,0.)
        glVertex3f(0.0,0.0,0.2)
        
        glEnd ()
        
    def setAxis (self, ax) :
        self.lookAxis = ax
        

    def setVals (self, xs, ys, zs) :
        self.myx = xs[:]
        self.myy = ys[:]
        self.myz = zs[:]
        self.setpts = True
        npts = self.myx.size
        self.usePeaks= np.ones(npts, dtype=np.uint16)
        self.queryIDs = (GLuint * npts)(0)
        
    def startSelectBox (self):
        self.boxSelectMode = 1 
    
    
        
        