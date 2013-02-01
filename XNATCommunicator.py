from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import time
import math

from XNATUtils import *

#########################################################
#
# 
comment = """
  XNATCommunicator
  
# TODO : 
"""
#
#########################################################




class XNATCommunicator(object):
    def __init__(self, browser, 
                       server, 
                       user, 
                       password, 
                       cachedir):
        self.browser = browser
        self.server = server
        self.user = user
        self.password = password
        self.cachedir = cachedir
        self.utils = XNATUtils()
        self.XNAT = None
        self.progDialog = None
        self.setup()
    
        self.totalDLSize = 0
        self.downloadedBytes = 0
        
    def setup(self):
        pass
    
    def getFiles_URL(self, srcDstMap, withProgressBar = True, fileOrFolder = None):     
        #=======================================================================
        # GET TOTAL SIZE OF DOWNLOADS FOR ALL FILES
        #=======================================================================
        self.totalDLSize = 0
        self.downloadedBytes = 0
        downloadFolders = []
        #=======================================================================
        # REMOVE EXISTING DST FILES
        #=======================================================================
        for src, dst in srcDstMap.iteritems(): 
            if os.path.exists(dst): self.utils.removeFile(dst)
        timeStart = time.time()
        #=======================================================================
        # DOWNLOAD THE FILES
        #=======================================================================
        if fileOrFolder == "file":
            for src, dst in srcDstMap.iteritems():
                #print("FILE DOWNLOAD src:%s\tdst:%s"%(src, dst))
                self.totalDLSize = int(self.XNAT.select(self.cleanSelectString(src)).size())
                if withProgressBar: self.urllib2GetWithProgress(self.cleanSelectString(src), dst)
                else: f.get(dst)                 
        elif fileOrFolder == "folder":
            import tempfile
            xnatFileFolders = []
            #=======================================================================
            # DETERMINE SOURCE FOLDERS, CREATE NEW DICT BASED ON BASENAME
            #=======================================================================
            for src, dst in srcDstMap.iteritems():
                #print("FOLDER D/L src:%s\tdst:%s"%(src, dst))
                srcFolder = os.path.dirname(src)
                if not srcFolder in xnatFileFolders:
                    xnatFileFolders.append(srcFolder)
            #=======================================================================
            # GET THE 'FILEOBJECTS'
            #=======================================================================
            fObjs = []
            for f in xnatFileFolders:
                #print("FOLDER DOWNLOAD %s"%(f))
                fObjs = self.XNAT.select(self.cleanSelectString(os.path.dirname(f))).files().get('~/tmp/files')
                for fO in fObjs:
                    self.totalDLSize += int(fO.size())                    
            for f in xnatFileFolders:
                if withProgressBar: 
                    src = self.cleanSelectString(f + "?format=zip")                 
                    dst = tempfile.mktemp('', 'XNATDownload', self.utils.tempPath) + ".zip"
                    downloadFolders.append(self.utils.adjustPathSlashes(dst))
                    if os.path.exists(dst): self.utils.removeFile(dst)
                    #print("DOWNLOADING %s to %s"%(src, dst))
                    self.urllib2GetWithProgress(src, dst)
                   
        timeEnd = time.time()
        totalTime = (timeEnd-timeStart)
        bps = self.totalDLSize/totalTime

        #print "DOWNLOAD FOLDERS: " + str(downloadFolders)
        return downloadFolders
        #qt.QMessageBox.warning(None, "Time", "Total time: %s. Bps: %s"%(totalTime, str(bps)))
    
    def getFolderContents(self):
        pass
    
    def getItemValue(self):
        pass
    
    def makeDir(self):
        pass

    def upload(self):
        pass

    def delete(self):
        pass
    
    def getSize(self):
        pass
    
    def downloadFailed(self, windowTitle, msg):
            qt.QMessageBox.warning(None, windowTitle, msg)

    def buffer_read(self, response, fileToWrite, dialog=None, buffer_size=8192):
        try:
            itemSize = response.info().getheader('Content-Length').strip()
            itemSize = int(itemSize)
        except Exception, e:
            #print ("ITEM SIZE ERROR %s"%(e))
            pass
        while 1:
            buffer = response.read(buffer_size)
            self.downloadedBytes += len(buffer)
            fileToWrite.write(buffer)
            if not buffer:
                break 
            
            percent = (float(self.downloadedBytes) / self.totalDLSize)
            percent = round(percent*100, 2)
            if percent == 100:
                self.browser.updateStatus(["", "Loading, please wait...", ""])
                self.browser.generalProgressBar.setVisible(False)
            dialog.setValue(percent)
        
        return self.downloadedBytes
    
    def urllib2GetWithProgress(self, XNATSrc, dst, groupSize = None, sizeTracker = 0):
        import urllib2
        XNATSrc = self.server + "/data/archive" + XNATSrc
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, XNATSrc, self.user, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
        XNATFile = open(dst, "wb")
        print ("\nDownloading %s...\n"%(XNATSrc))
        self.browser.updateStatus(["Downloading '%s'."%(os.path.basename(XNATSrc)),"Please wait...", ""])
        response = urllib2.urlopen(XNATSrc)
        
        self.browser.generalProgressBar.setVisible(True)
        
        """
        mainWindow = slicer.util.mainWindow()
        screenMainPos = mainWindow.pos
        x = screenMainPos.x() + mainWindow.width/2 - self.browser.generalProgressBar.width/2
        y = screenMainPos.y() + mainWindow.height/2 - self.browser.generalProgressBar.height/2
        self.browser.generalProgressBar.move(qt.QPoint(x,y))
        """
        self.browser.XNATView.setEnabled(False)
        
        a = self.buffer_read(response = response, fileToWrite = XNATFile, 
                             dialog = self.browser.generalProgressBar, buffer_size=8192)
            
        self.browser.XNATView.setEnabled(True)
        XNATFile.close()
        
        #dlStr = "Downloaded '%s' to '%s'"%(XNATSrc, dst)
        #print(dlStr)

class PyXNAT(XNATCommunicator):
    
    def setup(self):
        #=======================================================================
        # CLEAR THE PYXNAT CACHE
        #=======================================================================
        self.utils.removeFilesInDir(self.utils.pyXNATCache)
        import pyxnat
        #pyxnat.core.cache.CacheManager(self.XNAT).clear()
        from pyxnat import Interface  
        #=======================================================================
        # INITIALIZE PARENT
        #=======================================================================
        self.XNAT = Interface(server=self.server, 
                              user=self.user, 
                              password=self.password, 
                              cachedir=self.utils.pyXNATCache)
        
        
    
    def getFile(self, srcDstMap, withProgressBar = True):
        return self.getFiles_URL(srcDstMap, fileOrFolder = "file")
    
    def getFiles(self, srcDstMap, withProgressBar = True):
        return self.getFiles_URL(srcDstMap, fileOrFolder = "folder")
    
    def fileExists(self, XNATsrc):
        #print self.utils.lf() +  "Seeing if '%s' exists..."%(XNATsrc)
        return self.XNAT.select(self.cleanSelectString(XNATsrc)).exists()

    


    def makeDir(self, XNATPath):
        #print (self.utils.lf() + " MAING XNAT DIR: " + XNATPath)
        p = self.XNAT.select(self.cleanSelectString(XNATPath))
        try:
            if not p.exists():
                p.insert()
                return True
            else:
                return False
        except Exception, e:
            #print (self.utils.lf() + "ERROR CAUGHT: %s"%(str(e)))
            #print (self.utils.lf() + "PATH EXISTS! %s"%(XNATPath))
            return False
             
    def getResources(self, folder):
        try:
            folder += "/resources"
            #print self.utils.lf() + " Getting Resources: '%s'"%(folder)
            resources = self.XNAT.select(self.cleanSelectString(folder)).get()
            #print self.utils.lf() + " Got resources: '%s'"%(str(resources))
            resourceNames = []
            for r in resources:
                recVal = self.XNAT.select(self.cleanSelectString(folder + '/' + r)).label()
                resourceNames.append(recVal)
                #print (self.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, recVal))
            return resourceNames
        except Exception, e:
            print (self.utils.lf() + 
                   "GetResources error.  It likely did not like the path:\n%s"%(str(e)))
            #self.browser.updateStatus(["", "XNAT Error - getResources! (" + str(e) + ")", ""])
        
    def getFolderContents(self, folderName):      
        try:
            getContents = self.XNAT.select(self.cleanSelectString(folderName)).get()
            if str(getContents).startswith("<?xml"): return [] # We don't want text values
            return getContents
        except Exception, e:
            #print self.utils.lf() +  "CANT GET FOLDER CONTENTS OF '%s'"%(folderName) + " " + str(e)
            self.browser.updateStatus(["", "XNAT Error - getFolderContents! (" + str(e) + ")", ""])

    def getItemValue(self, XNATItem, attr):
        XNATItem = self.cleanSelectString(XNATItem)
        try:
            #print self.utils.lf() +  "GETTING By ATTRIB '%s': %s"%(attr, self.XNAT.select(XNATItem).attrs.get(attr))
            return self.XNAT.select(self.cleanSelectString(XNATItem)).attrs.get(attr)
        except:
            #print self.utils.lf() +  "ATTRIBUTE GET DID NOT WORK.  TRYNG LABEL() "
            return self.XNAT.select(self.cleanSelectString(XNATItem)).label()

    
    def cleanSelectString(self, selStr):
        if not selStr.startswith("/"):
            selStr = "/" + selStr
        selStr = selStr.replace("//", "/")
        if selStr.endswith("/"):
            selStr = selStr[:-1]
        return selStr

    
    def delete(self, selStr):
        print "DELETING: " + selStr
        self.XNAT.select(self.cleanSelectString(selStr)).delete()
    
    def getSize(self, selStr):
        #=======================================================================
        # GET THE TOTAL DOWNLOAD SIZE
        #=======================================================================
        bytes = int(self.XNAT.select(self.cleanSelectString(selStr)).size())
        mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
        return {"bytes": str(bytes), "mb" : str(mb)}

        
    def upload(self, localSrc, XNATDst, delExisting = True):
        #print self.utils.lf() +  "UPLOAD localSRC: %s\n\t\t\tXNATDst: %s"%(localSrc, XNATDst)
        #===================================================================
        # DERIVE XNAT PATH STRING, CLEANUP
        #===================================================================
        str1 = (os.path.dirname(os.path.dirname(XNATDst)))
        if not str1.startswith("/"):
            str1 = "/" + str1
        #===================================================================
        # CONSTUCT SELECT + INSERT STRINGS
        #===================================================================
        str2 = str(os.path.basename(XNATDst))
        str3 = self.utils.adjustPathSlashes(str(localSrc))
        #print self.utils.lf() + "STR1: "+  str1 + "\n\t\t\tSTR2: " +  str2 + "\n\t\t\tSTR3: " +  str3
        if delExisting and self.fileExists(XNATDst):
            #print "File appears to exist.  Trying to delete it..."
            try:
                self.XNAT.select(self.cleanSelectString(str1)).file(str2).delete()
                #print ("Successfully deleted the file")
            except Exception, e:
                print ("PyXNAT Error: %s"%(str(e)))
        #else:
        #    print "FILE DOES NOT EXIST"   
        #self.XNAT.select(self.cleanSelectString(str1)).file(str2).insert(str3)
        self.XNAT.select(self.cleanSelectString(str1)).file(str2).insert(str3)