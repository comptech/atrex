from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
##
# mySessionLogWidget
# This class inherits QListWidget.
# The QListWidget on the "Session Log" tab is promoted to the class
# The add Event method is used to add a timestamped string to that list widget
class mySessionLogWidget (QListWidget) :

    ##
    # init fcn, upon startup will write to the widget todays date and the current time as the session start time
    def __init__(self, parent):
        QListWidget.__init__(self,parent)
        date = QDate.currentDate().toString()
        time = self.getTimeString()
        str = "%s\r\n%s : Session start time"%(date,time)
        self.addItem (str)


    ##
    # gets current time and returns in standard format as a QString
    def getTimeString (self) :
        t= QTime.currentTime()
        s = t.toString ()
        return s

    ##
    # writes a timestamped user provided string to the list widget
    def addEvent (self, str) :
        time = self.getTimeString()
        str = "%s : %s"%(time, str)
        self.addItem (str)


    ##
    # writes an indented user provided string to the list widget, used in conjunction with addEvent
    def addSubEvent (self, str) :
        str = "\t%s"%str
        self.addItem (str)
