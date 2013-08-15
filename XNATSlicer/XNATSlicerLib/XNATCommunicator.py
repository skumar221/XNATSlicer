from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import time
import math
import urllib2
import string    
import httplib
from os.path import abspath, isabs, isdir, isfile, join
from base64 import b64encode
import json

from XNATUtils import *


#********************************************************************************
# XNATCommunicator uses PyXNAT to send/receive commands and files to an XNAT host
# Since input is usually string-based, there are several utility methods in this
# class to clean up strings for input to PyXNAT. 
#
#
#  The Neuroinformatics Research Group
#  Author: Sunil Kumar (kumar.sunil.p@gmail.com)
#  Date: 8/2013
#
#********************************************************************************

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

        self.userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
        self.authenticationHeader = { 'Authorization' : 'Basic %s' %(self.userAndPass) }

        self.fileDict = {};


    def setup(self):
        pass



    
    def getFiles_URL(self, srcDstMap, withProgressBar = True, fileOrFolder = None): 

        
        #--------------------
        # Get total size of downloads for all files
        #-------------------------
        self.totalDLSize = 0
        self.downloadedBytes = 0
        downloadFolders = []

        
        
        #-------------------------
        # Remove existing dst files
        #-------------------------
        for src, dst in srcDstMap.iteritems(): 
            if os.path.exists(dst): 
                self.utils.removeFile(dst)
        timeStart = time.time()

        
        
        #-------------------------
        # Download files
        #-------------------------
        if fileOrFolder == "file":
            for src, dst in srcDstMap.iteritems():
                #print("FILE DOWNLOAD src:%s\tdst:%s"%(src, dst))
                self.totalDLSize = int(self.XNAT.select(self.cleanSelectString(src)).size())
                if withProgressBar: self.urllib2GetWithProgress(self.cleanSelectString(src), dst)
                else: f.get(dst)                 
        elif fileOrFolder == "folder":
            import tempfile
            xnatFileFolders = []

            
            #
            # Determine source folders, create new dict based on basename
            #
            for src, dst in srcDstMap.iteritems():
                #print("FOLDER D/L src:%s\tdst:%s"%(src, dst))
                srcFolder = os.path.dirname(src)
                if not srcFolder in xnatFileFolders:
                    xnatFileFolders.append(srcFolder)

                    
            #
            # Get the 'fileobjects'
            #
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



    
    def upload(self, localSrc, xnatDst, delExisting = True):

        # Read file to data
        f=open(localSrc, 'rb')
        filebody = f.read()
        f.close()

        # Delete existing
        if delExisting:
            self.httpsRequest('DELETE', xnatDst, '')

        # Request
        r = self.httpsRequest('PUT', 
                          xnatDst, 
                          body=b64encode(filebody).decode("base64"), 
                          headerAdditions = {'content-type': 'application/octet-stream'})



        
        
    def httpsRequest(self, restMethod, xnatSelector, body='', headerAdditions={}):
        """ Description
        """

        # Clean REST method
        restMethod = restMethod.upper()

        # Clean url
        url =  self.server.encode("utf-8") + '/data' +  xnatSelector.encode("utf-8")

        # Get request
        req = urllib2.Request (url)

        # Get connection
        connection = httplib.HTTPSConnection (req.get_host ()) 

        # Merge the authentication header with any other headers
        header = dict(self.authenticationHeader.items() + headerAdditions.items())

        # REST call
        connection.request (restMethod, req.get_selector (), body=body, headers=header)

        print self.utils.lf() + "XNAT request - %s %s"%(restMethod, url)
        # Return response
        return connection.getresponse ()



    
    def delete(self, selStr):
        print "%s DELETING: %s"%(self.utils.lf(), selStr)
        self.httpsRequest('DELETE', selStr, '')


    
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



    def getFile(self, srcDstMap, withProgressBar = True):
        return self.getFiles_URL(srcDstMap, fileOrFolder = "file")



    
    def getFiles(self, srcDstMap, withProgressBar = True):
        return self.getFiles_URL(srcDstMap, fileOrFolder = "folder")
    


    
    def urllib2GetWithProgress(self, XNATSrc, dst, groupSize = None, sizeTracker = 0):
        
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



        
    def getJson(self, url):
        
        if (('/scans/' in url) and len(url.split('/scans/')[1])>0):
            if (not url.endswith('/')):
                url += '/'
            url += "files"

        response = self.httpsRequest('GET', url).read()
        #print "GET JSON RESPONSE: %s"%(response)
        return json.loads(response)['ResultSet']['Result']


    
    def getLevel(self, url, level):
        
        if not level.startswith('/'):
            level = '/' + level

        if (level) in url:
            return  url.split(level)[0] + level
        else:
            raise Exception("%s invalid get level '%s' parameter: %s"%(self.utils.lf(), url, level))

        

        
    def fileExists(self, fileUrl):
        """ Descriptor
        """
        
        # Clean string
        parentDir = self.getLevel(selStr, 'files');


        # Parse result dictionary
        for i in self.getJson(parentDir):
            if os.path.basename(selStr) in i['Name']:
                return True   
        return False
    


    
    def getSize(self, selStr):
        """ Descriptor
        """
        
        bytes = 0
       
        
        if (os.path.basename(selStr) in self.fileDict):
            print("\n%s in file dict!")%(selStr)
            for fDict in self.fileDict[os.path.basename(selStr)]:
                print fDict
                selSplit = selStr.split("/")
                searchStr = selSplit[-2]  + "/" + selSplit[-1]
                print "SEARCH STR: ", searchStr
                print "UR: ", fDict['URI'] 
                if searchStr in fDict['URI']:
                    print "FOUNND IT! ", fDict['Size']
                    bytes = int(fDict['Size'])
                    break

        else:
            print("**************%s in NOT file dict!")%(selStr)
            print self.fileDict
            parentDir = self.getLevel(selStr, 'files');
            
            # Parse result dictionary
            
            for i in self.getJson(parentDir):
                if os.path.basename(selStr) in i['Name']:
                    bytes = int(i['Size'])

        mb = str(bytes/(1024*1024.0)).split(".")[0] + "." + str(bytes/(1024*1024.0)).split(".")[1][:2]
        
        return {"bytes": str(bytes), "mb" : str(mb)}



    
    def getFolderContents(self, folderName):   
        """ Descriptor
        """
        #try:
        print "getContents: ", folderName
        getContents =  self.getJson(folderName)

        print getContents
        
        if str(getContents).startswith("<?xml"): 
            return [] # We don't want text values

        key = 'ID'
        if folderName.endswith('subjects'):
            key = 'label'
        elif ('/scans/') in folderName or folderName.endswith('/files'):
            key = 'Name'
            for content in getContents:
                self.fileDict[content['Name']] = []
                self.fileDict[content['Name']].append(content)

        print "************ Using key '%s'"%(key)
        return [ content[key] for content in getContents ]
    #except Exception, e:
    #        print self.utils.lf() +  "CANT GET FOLDER CONTENTS OF '%s'"%(folderName) + " " + str(e)



    def getResources(self, folder):
        
        #try:
        if not '/scans/' in folder:
            folder += "/resources"
            
        resources = self.getJson(self.cleanSelectString(folder))
        print self.utils.lf() + " Got resources: '%s'"%(str(resources))
        resourceNames = []
        
        for r in resources:
            if 'label' in r:
                resourceNames.append(r['label'])
                print (self.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['label']))
            elif 'Name' in r:
                resourceNames.append(r['Name'])
                print (self.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['Name']))                
            
            return resourceNames
        
    #except Exception, e:
    #       print (self.utils.lf() +  "GetResources error.  It likely did not like the path:\n%s"%(str(e)))


            


    def getItemValue(self, XNATItem, attr):
        #print "%s %s %s",%(self.utils.lf(), XNATItem, attr)

        XNATItem = self.cleanSelectString(XNATItem)

        for i in self.getJson(os.path.dirname(XNATItem)):
            for key, val in i.iteritems():
                if val == os.path.basename(XNATItem):
                    if len(attr)>0 and (attr in i):
                        return i[attr]
                    elif 'label' in i:
                        return i['label']
                    elif 'Name' in i:
                        return i['Name']
 



                    
    def cleanSelectString(self, selStr):
        if not selStr.startswith("/"):
            selStr = "/" + selStr
        selStr = selStr.replace("//", "/")
        if selStr.endswith("/"):
            selStr = selStr[:-1]
        return selStr

        
    def makeDir(self, XNATPath):  
        r = self.httpsRequest('PUT', XNATPath)
        print "%s Put Dir %s \n%s"%(self.utils.lf(), XNATPath, r)
        return r








            



            





        



