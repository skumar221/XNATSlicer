from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys


comment = """
  XNATSessionManager

# TODO : 
"""

class XNATSessionArgs(dict):
    def __init__(self, browser, srcPath = None, useDefaultXNATSaveLevel = True):
        self.browser = browser
        self.inserting = True 
        self['host'] = None
        self['username'] = None
        self['saveLevel'] = None
        self['saveDir'] = None
        self['otherDirs'] = None
        self['sharedDir'] = None
        self['sharable'] = None
        self['fileName'] = None 
        self['sessionStart'] = str(datetime.datetime.now())
        self["sessionType"] = None
        self["XNATCommunicator"] = None
        self["metadata"] = None
        self.inserting = False
        
        #self.printAll("\nINIT SESSION ARGS===========================")   
        if srcPath:
            self.makeSessionArgs_byPath(srcPath)
            
        dict.__init__(self) 
        
    def __setitem__(self, key, value):
        if (key not in self) and (not self.inserting):
             raise KeyError("XNATSessionArgs is immutable -- you can't insert keys.")
        dict.__setitem__(self, key, value)
    
    def makeSessionArgs_byPath(self, filePath):
        saveLevelDir, slicerDir, sharedDir = self.browser.utils.getSaveTuple(filePath) 
        self['host'] = self.browser.XNATLoginMenu.hostDropdown.currentText
        self['username'] = self.browser.XNATLoginMenu.usernameLine.text        
        self['saveLevel'] = saveLevelDir
        self['saveDir'] = slicerDir
        self['sharedDir'] = sharedDir
        
        if os.path.basename(os.path.dirname(filePath)) == 'files':
            self["fileName"] = os.path.basename(filePath) 
        else:
            self["fileName"] = os.path.basename(saveLevelDir)         
        #self.printAll("\nSESSION ARGS BY SRC PATH===========================")     
            
    def printAll(self, prefStr=None):
        if prefStr: print (('%s')%(prefStr))
        for k,v in self.iteritems():
            print "[\'%s\']=\t%s"%(k,v)
            
class XNATSessionManager(object):
    def __init__(self, browser):
        
        self.browser = browser

        self.sessionFileName = os.path.join(self.browser.utils.utilPath, 'SessionLog.txt')
        
        self.sessionArgs = None
        self.saveItem = None
    
    def startNewSession(self, sessionArgs):
        if not sessionArgs.__class__.__name__ == "XNATSessionArgs":
            raise NameError("You can only use XNATSessionArgs to start a new session.")
        self.sessionArgs = sessionArgs
        self.writeSession()
        
    def clearCurrentSession(self):
        #print(self.browser.utils.lf() + "CLEARING CURRENT SESSION!")
        self.sessionArgs = None


    def writeSession(self):
        
        fileLines = []
        
        for item in self.sessionArgs:
            fileLines.append("%s:\t\t%s\n"%(item, self.sessionArgs[item]))
        
        fileLines.append("\n\n")
        print(self.browser.utils.lf() + "Session log file: %s"%(self.sessionFileName))
        f = open(self.sessionFileName, 'a')
        f.writelines(fileLines)            
        f.close()
        
        del fileLines

        
    
