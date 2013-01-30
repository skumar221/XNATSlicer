from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys

#########################################################
#
# 
comment = """
  XNATTimer

# TODO : 
"""
#
#########################################################
                
class XNATTimer(object):
    def __init__(self, utils, writeFileName = None, fileOverWrite = False):
        self.utils = utils
        self.prev = None
        self.curr = None
        self.debugStr = None
        self.processName = None
        self.timerStrs = []
        
        if not writeFileName: self.writeFileName = os.path.join(self.utils.homePath, 'timerLog.txt')
        else: self.writeFileName = os.path.join(self.utils.homePath, writeFileName)
            
        self.fileOverWrite = fileOverWrite
        
        self.startCalled = False

    def start(self, processName = None, debugStr = None):
        
        self.startCalled = True
        currStr = ""
        self.debugStr = debugStr        
        self.prev = datetime.datetime.now() 
        
        if processName:
            self.processName = processName
            self.timerStrs.append('\n' + processName + '\n') 
            print('\n' + processName)
        if self.debugStr: currStr = "before " + self.debugStr + "."
        
        str  = ("%s <--Start timer %s"%(self.prev, currStr))
        self.timerStrs.append(str + '\n')
        print str
        
            
    def stop(self, fileWrite = True, printTimeDiff = True):
        
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
        if self.writeFileName:
            f = open(self.writeFileName, 'a')
            f.writelines(self.timerStrs)            
            f.close()

        
    def clear(self):
        self.curr = None
        self.prev = None
        self.debugStr = None
        self.processName = None
        del self.timerStrs[:]
        self.startCalled = False