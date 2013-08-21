from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys



comment = """
XNATTimer manages time logging for performance testing.

Usage as follows:

>>> from XNATTimer import *
>>> timer = XNATTimer(writePath = "./", writeFileName = "timelog.txt")
>>> timer.start(processName = "Download", debugStr = "Downloading...")
Download
2013-08-21 09:27:11.673000 <--Start timer before Downloading....


>>> # Download code here

>>> timer.stop()
2013-08-21 09:27:18.396000 <---Stop timer after Downloading....
TOTAL TIME ELAPSED FOR Download: 		0:00:06.723000

"""


                
class XNATTimer(object):
    """ Class name
    """



    
    def __init__(self, writePath = './', writeFileName = 'timerlog.txt', fileOverWrite = False):
        """ Descriptor
        """

        self.prev = None
        self.curr = None
        self.debugStr = None
        self.processName = None
        self.timerStrs = []
        self.writePath = writePath
        
        if not writeFileName: self.writeFileName = os.path.join(self.writePath, 'timerLog.txt')
        else: self.writeFileName = os.path.join(self.writePath, writeFileName)
        self.fileOverWrite = fileOverWrite 
        self.startCalled = False



        
    def start(self, processName = None, debugStr = None):       
        """ Descriptor
        """
        self.startCalled = True
        currStr = ""
        self.debugStr = debugStr        
        self.prev = datetime.datetime.now() 
        if processName:
            self.processName = processName
            self.timerStrs.append('\n' + processName + '\n') 
            print('\n' + processName)
        if self.debugStr: 
            currStr = "before " + self.debugStr + "."
        str  = ("%s <--Start timer %s"%(self.prev, currStr))
        self.timerStrs.append(str + '\n')
        print str


        
            
    def stop(self, fileWrite = True, printTimeDiff = True):
        """ Descriptor
        """
        if self.startCalled:
            currStr = ""
            elapseStr = ""
            
            self.curr = datetime.datetime.now() 
            if self.debugStr: 
                currStr = "after " + self.debugStr + "."
            if self.processName: elapseStr = "FOR " + self.processName
            
            str1  = ("%s <---Stop timer %s"%(self.curr, currStr))
            self.timerStrs.append(str1 + '\n')
            print str1

            if printTimeDiff:
                str2 =  ("TOTAL TIME ELAPSED %s: \t\t%s"%(elapseStr, (self.curr-self.prev)))
                self.timerStrs.append(str2 + '\n')
                print str2
            
            if fileWrite: self.write()
            self.clear()



            
    def write(self):
        """ Descriptor
        """
        if self.writeFileName:
            f = open(self.writeFileName, 'a')
            f.writelines(self.timerStrs)            
            f.close()



            
    def clear(self):
        """ Descriptor
        """
        self.curr = None
        self.prev = None
        self.debugStr = None
        self.processName = None
        del self.timerStrs[:]
        self.startCalled = False
