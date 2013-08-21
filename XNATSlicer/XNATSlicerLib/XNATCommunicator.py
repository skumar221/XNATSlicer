from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import time
import math
import urllib2
import string    
import httplib
import codecs
from os.path import abspath, isabs, isdir, isfile, join
from base64 import b64encode
import json



comment = """
XNATCommunicator uses PyXNAT to send/receive commands and files to an XNAT host
Since input is usually string-based, there are several utility methods in this
class to clean up strings for input to PyXNAT. 


  The Neuroinformatics Research Group
  Author: Sunil Kumar (kumar.sunil.p@gmail.com)
  Date: 8/2013
"""



class XNATCommunicator(object):
    """ Communication class to XNAT.  Urllib2 is the current library.
    """


    
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


        self.setup()

        self.downloadTracker = {
            'totalDownloadSize': {'bytes': None, 'MB': None},
            'downloadedSize': {'bytes': None, 'MB': None},
        }

        self.userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
        self.authenticationHeader = { 'Authorization' : 'Basic %s' %(self.userAndPass) }
        self.fileDict = {};



        
    def setup(self):
        pass



    
    def getFiles_URL(self, srcDstMap, withProgressBar = True, fileOrFolder = None): 

        
        #--------------------
        # Get total size of downloads for all files
        #-------------------------
        self.downloadTracker['totalDownloadSize']['bytes'] = 0
        self.downloadTracker['downloadedSize']['bytes'] = 0
        downloadFolders = []

        
        
        #-------------------------
        # Remove existing dst files
        #-------------------------
        for src, dst in srcDstMap.iteritems(): 
            if os.path.exists(dst): 
                self.browser.utils.removeFile(dst)
        timeStart = time.time()

        
        
        #-------------------------
        # Download files
        #-------------------------
        if fileOrFolder == "file":
            for src, dst in srcDstMap.iteritems():
                print("FILE DOWNLOAD src:%s\tdst:%s"%(src, dst))

                fName = os.path.basename(src)
                fPath = "/projects/" + src.split("/projects/")[1]
                print fPath
                
                #self.downloadTracker['totalDownloadSize']['bytes'] = int(0)
                #if fName in self.fileDict and 'Size' in self.fileDict[fName]:
                #    print "GOT SIZE: ! %s"%(int(self.fileDict[fName]['Size']))
                #    self.downloadTracker['totalDownloadSize']['bytes'] = int(self.fileDict[fName]['Size'])
 
                if withProgressBar: 
                    self.getFileWithProgress(src, dst)
                else: 
                    f.get(dst) 
                                    
        elif fileOrFolder == "folder":
            import tempfile
            xnatFileFolders = []


            
            #---------------------
            # Determine source folders, create new dict based on basename
            #---------------------
            for src, dst in srcDstMap.iteritems():
                #print("FOLDER D/L src:%s\tdst:%s"%(src, dst))
                srcFolder = os.path.dirname(src)
                if not srcFolder in xnatFileFolders:
                    xnatFileFolders.append(srcFolder)


                    
            #--------------------
            # Get file with progress bar
            #--------------------
            for f in xnatFileFolders:
                if withProgressBar: 
                    
                    
                    # Sting cleanup
                    src = (f + "?format=zip")                 
                    dst = tempfile.mktemp('', 'XNATDownload', self.browser.utils.tempPath) + ".zip"
                    downloadFolders.append(self.browser.utils.adjustPathSlashes(dst))

                    
                    # remove existing
                    if os.path.exists(dst): 
                        self.browser.utils.removeFile(dst)

                        
                    # Init download
                    print("FOLDER DOWNLOADING %s to %s"%(src, dst))
                    self.getFileWithProgress(src, dst)

                    
                   
        timeEnd = time.time()
        totalTime = (timeEnd-timeStart)

        return downloadFolders



    
    def upload(self, localSrc, xnatDst, delExisting = True):
        """ Uploading using urllib2
        """

        #--------------------        
        # Encoding cleanup
        #-------------------- 
        xnatDst = str(xnatDst).encode('ascii', 'ignore')


        
        #-------------------- 
        # Read file
        #-------------------- 
        f = open(localSrc, 'rb')
        filebody = f.read()
        f.close()



        #-------------------- 
        # Delete existing
        #-------------------- 
        if delExisting:
            self.httpsRequest('DELETE', xnatDst, '')

            
        print "%s UPLOAD: localSrc: '%s'\n\txnatDst: '%s'"%(self.browser.utils.lf(), localSrc, xnatDst)



        #-------------------- 
        # Get request and connection
        #-------------------- 
        req = urllib2.Request(xnatDst)
        connection = httplib.HTTPSConnection (req.get_host())  



        #-------------------- 
        # Make authentication header
        #-------------------- 
        userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")       
        header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}    



        #-------------------- 
        # REST call
        #-------------------- 
        connection.request ('PUT', req.get_selector(), body = filebody, headers = header)



        #-------------------- 
        # Response return
        #-------------------- 
        response = connection.getresponse ()
        return response
        #print "response: ", response.read()   



        
        
    def httpsRequest(self, restMethod, xnatSelector, body='', headerAdditions={}):
        """ Description
        """

        
        # Clean REST method
        restMethod = restMethod.upper()

        
        # Clean url
        prepender = self.server.encode("utf-8") + '/data'
        url =  prepender +  xnatSelector.encode("utf-8") if not prepender in xnatSelector else xnatSelector

        
        # Get request
        req = urllib2.Request (url)

        
        # Get connection
        connection = httplib.HTTPSConnection (req.get_host ()) 

        
        # Merge the authentication header with any other headers
        header = dict(self.authenticationHeader.items() + headerAdditions.items())

        
        # REST call
        connection.request(restMethod, req.get_selector (), body = body, headers = header)

        print self.browser.utils.lf() + "XNAT request - %s %s"%(restMethod, url)


        # Return response
        return connection.getresponse ()



    
    def delete(self, selStr):
        """ Description
        """
        print "%s DELETING: %s"%(self.browser.utils.lf(), selStr)
        self.httpsRequest('DELETE', selStr, '')

        

    
    def downloadFailed(self, windowTitle, msg):
        """ Description
        """
        qt.QMessageBox.warning(None, windowTitle, msg)


            

    def getFile(self, srcDstMap, withProgressBar = True):
        """ Description
        """
        return self.getFiles_URL(srcDstMap, fileOrFolder = "file")



    
    def getFiles(self, srcDstMap, withProgressBar = True):
        """ Description
        """
        return self.getFiles_URL(srcDstMap, fileOrFolder = "folder")
    


    
    def getFileWithProgress(self, XNATSrc, dst, groupSize = None, sizeTracker = 0):
        """ Descriptor
        """

        
        #-------------------- 
        # Set the path
        #-------------------- 
        XNATSrc = self.server + "/data/archive" + XNATSrc if not self.server in XNATSrc else XNATSrc

        

        #-------------------- 
        # Authentication handler
        #-------------------- 
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, XNATSrc, self.user, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)


        
        #-------------------- 
        # Begin to open the file to read in bytes
        #-------------------- 
        XNATFile = open(dst, "wb")
        print ("\nDownloading %s...\n"%(XNATSrc))
      


        #-------------------- 
        # Get the response URL
        #-------------------- 
        response = urllib2.urlopen(XNATSrc)


        
        #-------------------- 
        # Get the content size, first by checking log, then by reading header
        #-------------------- 
        self.downloadTracker['downloadedSize']['bytes'] = 0   
        self.downloadTracker['totalDownloadSize'] = self.getSize(XNATSrc)
        if not self.downloadTracker['totalDownloadSize']['bytes']:

            
            # If not in log, read the header
            if "Content-Length" in response.headers:
                self.downloadTracker['totalDownloadSize']['bytes'] = int(response.headers["Content-Length"])  
                self.downloadTracker['totalDownloadSize']['MB'] = self.browser.utils.bytesToMB(self.downloadTracker['totalDownloadSize']['bytes'])


                
        #-------------------- 
        # Update the download popup
        #-------------------- 
        if self.downloadTracker['totalDownloadSize']['bytes'] and self.browser.downloadPopup:
            self.browser.downloadPopup.setDownloadFileSize(self.downloadTracker['totalDownloadSize']['bytes'])


            
        #-------------------- 
        # Adjust browser UI
        #-------------------- 
        self.browser.XNATView.setEnabled(False)
        


        # DEPRECATED: Window adjustments
        """
        mainWindow = slicer.util.mainWindow()
        screenMainPos = mainWindow.pos
        x = screenMainPos.x() + mainWindow.width/2 - self.browser.generalProgressBar.width/2
        y = screenMainPos.y() + mainWindow.height/2 - self.browser.generalProgressBar.height/2
        self.browser.generalProgressBar.move(qt.QPoint(x,y))
        """



        #-------------------- 
        # Read buffers (cyclical)
        #-------------------- 
        fileDisplayName = os.path.basename(XNATSrc) if not 'format=zip' in XNATSrc else XNATSrc.split("/subjects/")[1]
        a = self.buffer_read(response = response, 
                             fileToWrite = XNATFile, 
                             buffer_size = 8192, 
                             currSrc = XNATSrc,
                             fileDisplayName = fileDisplayName)


        
        #-------------------- 
        # Reenable Viewer and close the file
        #-------------------- 
        self.browser.XNATView.setEnabled(True)
        XNATFile.close()



        
    def buffer_read(self, response, fileToWrite, buffer_size=8192, currSrc = "", fileDisplayName = ""):
        """Descriptor
        """
        
        while 1:            

            
            # Read buffer
            buffer = response.read(buffer_size)
            if not buffer: 
                if self.browser.downloadPopup:
                    self.browser.downloadPopup.hide()
                break 
            
            
            # Write buffer to file
            fileToWrite.write(buffer)

            
            # Update progress indicators
            self.downloadTracker['downloadedSize']['bytes'] += len(buffer)
            if self.browser.downloadPopup:
                self.browser.downloadPopup.update(self.downloadTracker['downloadedSize']['bytes'])
            
        return self.downloadTracker['downloadedSize']['bytes']

    
            
        
    def getJson(self, url):
        """ Descriptor
        """
        print "%s %s"%(self.browser.utils.lf(), url)
        response = self.httpsRequest('GET', url).read()
        #print "GET JSON RESPONSE: %s"%(response)
        return json.loads(response)['ResultSet']['Result']


    
    
    def getLevel(self, url, level):
        """ Descriptor
        """
        print "%s %s"%(self.browser.utils.lf(), url, level)
        if not level.startswith('/'):
            level = '/' + level

        if (level) in url:
            return  url.split(level)[0] + level
        else:
            raise Exception("%s invalid get level '%s' parameter: %s"%(self.browser.utils.lf(), url, level))

        

        
    def fileExists(self, selStr):
        """ Descriptor
        """
        print "%s %s"%(self.browser.utils.lf(), selStr)

    
        # Query logged files before checking
        if (os.path.basename(selStr) in self.fileDict):
            return True
                
        
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
        print "%s %s"%(self.browser.utils.lf(), selStr)
        bytes = 0
       
        
        # Query logged files
        fileName = os.path.basename(selStr)
        if fileName in self.fileDict:
            bytes = int(self.fileDict[fileName]['Size'])
            return {"bytes": (bytes), "MB" : self.browser.utils.bytesToMB(bytes)}

        return {"bytes": None, "MB" : None}



    
    def getFolderContents(self, queryPaths, metadataTag = 'ID'):   
        """ Descriptor
        """


        #-------------------- 
        # Differentiate between a list of paths
        # and once single path (string) -- make all a list
        #-------------------- 
        if isinstance(queryPaths, basestring):
           queryPaths = [queryPaths]


           
        #-------------------- 
        # Acquire contents
        #-------------------- 
        contents = []
        for p in queryPaths:
            print "%s query path: %s"%(self.browser.utils.lf(), p)
            contents =  contents + self.getJson(p)
            
        if str(contents).startswith("<?xml"): return [] # We don't want text values

        

        #-------------------- 
        # Get other attributes with the contents
        #-------------------- 
        childNames = []
        sizes = []
        for content in contents:
            if metadataTag in content:
                childNames.append(content[metadataTag])
            else:
                print "%s NO METADATA %s %s"%(self.browser.utils.lf(), metadataTag, content)
                childNames.append(content['Name'])

                
            # Get size if applicable
            if ('Size' in content):
                sizes.append(content['Size'])



        #-------------------- 
        # Track files in global dict
        #-------------------- 
        for q in queryPaths:
            if q.endswith('/files'):
                for c in contents:
                    # create a tracker in the fileDict
                    self.fileDict[c['Name']] = c
                print "%s %s"%(self.browser.utils.lf(), self.fileDict)


                
        return childNames, (sizes if len(sizes) > 0 else None)




    def getResources(self, folder):
        """ Descriptor
        """

        
        print "%s %s"%(self.browser.utils.lf(), folder)

        
        # Get the resource Json
        folder += "/resources"
        resources = self.getJson(folder)
        print self.browser.utils.lf() + " Got resources: '%s'"%(str(resources))


        # Filter the Jsons
        resourceNames = []
        for r in resources:
            if 'label' in r:
                resourceNames.append(r['label'])
                print (self.browser.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['label']))
            elif 'Name' in r:
                resourceNames.append(r['Name'])
                print (self.browser.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['Name']))                
            
            return resourceNames




    def getItemValue(self, XNATItem, attr):
        """ Retrieve an item by one of its attributes
        """

        # Clean string
        XNATItem = self.cleanSelectString(XNATItem)
        print "%s %s %s"%(self.browser.utils.lf(), XNATItem, attr)


        # Parse json
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
        """ As stated
        """
        if not selStr.startswith("/"):
            selStr = "/" + selStr
        selStr = selStr.replace("//", "/")
        if selStr.endswith("/"):
            selStr = selStr[:-1]
        return selStr



    
        
    def makeDir(self, XNATPath): 
        """ Makes a directory in XNAT via PUT
        """ 
        r = self.httpsRequest('PUT', XNATPath)
        print "%s Put Dir %s \n%s"%(self.browser.utils.lf(), XNATPath, r)
        return r








            







        



