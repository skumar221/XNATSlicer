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
XnatCommunicator uses httplib to send/receive commands and files to an Xnat host
Since input is usually string-based, there are several utility methods in this
class to clean up strings for input to httplib. 
"""






class XnatCommunicator(object):
    """ Communication class to Xnat.  Urllib2 is the current library.
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



    
    def getFilesByUrl(self, srcDstMap, withProgressBar = True, fileOrFolder = None): 

        
        #--------------------
        # Reset total size of downloads for all files
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
                print("%s file download\nsrc: '%s' \ndst: '%s'"%(self.browser.utils.lf(), src, dst))

                fName = os.path.basename(src)
                fPath = "/projects/" + src.split("/projects/")[1]
                self.get(src, dst)

                                    
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
                    dst = tempfile.mktemp('', 'XnatDownload', self.browser.utils.tempPath) + ".zip"
                    downloadFolders.append(self.browser.utils.adjustPathSlashes(dst))

                    
                    # remove existing
                    if os.path.exists(dst): 
                        self.browser.utils.removeFile(dst)

                        
                    # Init download
                    print("%s folder downloading %s to %s"%(self.browser.utils.lf(), src, dst))
                    self.get(src, dst)

                    
                   
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

            
        print "%s Uploading\nsrc: '%s'\nxnatDst: '%s'"%(self.browser.utils.lf(), localSrc, xnatDst)



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
        #print ('%s httpsRequest: %s %s')%(self.browser.utils.lf(), restMethod, url)


        # Return response
        return connection.getresponse ()



    
    def delete(self, selStr):
        """ Description
        """
        print "%s deleting %s"%(self.browser.utils.lf(), selStr)
        self.httpsRequest('DELETE', selStr, '')

        

    
    def downloadFailed(self, windowTitle, msg):
        """ Description
        """
        qt.QMessageBox.warning(None, windowTitle, msg)


            

    def getFile(self, srcDstMap, withProgressBar = True):
        """ Description
        """
        return self.getFilesByUrl(srcDstMap, fileOrFolder = "file")



    
    def getFiles(self, srcDstMap, withProgressBar = True):
        """ Description
        """
        return self.getFilesByUrl(srcDstMap, fileOrFolder = "folder")
    


    
    def get(self, XnatSrc, dst, showProgressIndicator = True):
        """ Descriptor
        """

        
        #-------------------- 
        # Set the path
        #-------------------- 
        XnatSrc = self.server + "/data/archive" + XnatSrc if not self.server in XnatSrc else XnatSrc

        

        #-------------------- 
        # Authentication handler
        #-------------------- 
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, XnatSrc, self.user, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)


        
        #-------------------- 
        # Begin to open the file to read in bytes
        #-------------------- 
        XnatFile = open(dst, "wb")
      


        #-------------------- 
        # Get the response URL
        #-------------------- 
        response = urllib2.urlopen(XnatSrc)


        
        #-------------------- 
        # Get the content size, first by checking log, then by reading header
        #-------------------- 
        self.downloadTracker['downloadedSize']['bytes'] = 0   
        self.downloadTracker['totalDownloadSize'] = self.getSize(XnatSrc)
  
        if not self.downloadTracker['totalDownloadSize']['bytes']:
          
            # If not in log, read the header
            if "Content-Length" in response.headers:
                self.downloadTracker['totalDownloadSize']['bytes'] = int(response.headers["Content-Length"])  
                self.downloadTracker['totalDownloadSize']['MB'] = self.browser.utils.bytesToMB(self.downloadTracker['totalDownloadSize']['bytes'])


            
        #-------------------- 
        # Adjust browser UI
        #-------------------- 
        self.browser.XnatView.setEnabled(False)


        

        #-------------------- 
        # Define buffer read function
        #-------------------- 
        def buffer_read(response, fileToWrite, buffer_size=8192, currSrc = "", fileDisplayName = ""):
            """Downloads files by a constant buffer size.
            """

            
            if showProgressIndicator:
                
                # Reset popup
                self.browser.downloadPopup.reset()
                
                # Set filename
                self.browser.downloadPopup.setDownloadFilename(fileDisplayName) 
                
                # Update the download popup file size
                if self.downloadTracker['totalDownloadSize']['bytes']:
                    self.browser.downloadPopup.setDownloadFileSize(self.downloadTracker['totalDownloadSize']['bytes'])
                    # Wait for threads to catch up 
                    slicer.app.processEvents()

                    # show popup
                self.browser.downloadPopup.show()


                
            self.browser.XnatView.viewWidget.setEnabled(False)

        
            # Read loop
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
                if showProgressIndicator and self.browser.downloadPopup:
                    self.browser.downloadPopup.update(self.downloadTracker['downloadedSize']['bytes'])

                    
                # Wait for threads to catch up      
                slicer.app.processEvents()


                
            return self.downloadTracker['downloadedSize']['bytes']


        
        #-------------------- 
        # Read buffers (cyclical)
        #-------------------- 
        fileDisplayName = os.path.basename(XnatSrc) if not 'format=zip' in XnatSrc else XnatSrc.split("/subjects/")[1]  
        bytesRead = buffer_read(response = response, fileToWrite = XnatFile, 
                                buffer_size = 8192, currSrc = XnatSrc, fileDisplayName = fileDisplayName)


        
        #-------------------- 
        # Reenable Viewer and close the file
        #-------------------- 
        self.browser.XnatView.setEnabled(True)
        XnatFile.close()

    
            
        
    def getJson(self, url):
        """ Descriptor
        """
        #print "%s %s"%(self.browser.utils.lf(), url)
        response = self.httpsRequest('GET', url).read()
        #print "GET JSON RESPONSE: %s"%(response)
        return json.loads(response)['ResultSet']['Result']


    
    
    def getLevel(self, url, level):
        """ Descriptor
        """
        #print "%s %s"%(self.browser.utils.lf(), url, level)
        if not level.startswith('/'):
            level = '/' + level

        if (level) in url:
            return  url.split(level)[0] + level
        else:
            raise Exception("%s invalid get level '%s' parameter: %s"%(self.browser.utils.lf(), url, level))

        

        
    def fileExists(self, selStr):
        """ Descriptor
        """
        #print "%s %s"%(self.browser.utils.lf(), selStr)

    
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
        #print "%s %s"%(self.browser.utils.lf(), selStr)
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
            #print "%s query path: %s"%(self.browser.utils.lf(), p)
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
                #print "%s NO METADATA %s %s"%(self.browser.utils.lf(), metadataTag, content)
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
                #print "%s %s"%(self.browser.utils.lf(), self.fileDict)


                
        return childNames, (sizes if len(sizes) > 0 else None)




    def getResources(self, folder):
        """ Descriptor
        """

        
        #print "%s %s"%(self.browser.utils.lf(), folder)

        
        # Get the resource Json
        folder += "/resources"
        resources = self.getJson(folder)
        #print self.browser.utils.lf() + " Got resources: '%s'"%(str(resources))


        # Filter the Jsons
        resourceNames = []
        for r in resources:
            if 'label' in r:
                resourceNames.append(r['label'])
                #print (self.browser.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['label']))
            elif 'Name' in r:
                resourceNames.append(r['Name'])
                #print (self.browser.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['Name']))                
            
            return resourceNames




    def getItemValue(self, XnatItem, attr):
        """ Retrieve an item by one of its attributes
        """

        # Clean string
        XnatItem = self.cleanSelectString(XnatItem)
        #print "%s %s %s"%(self.browser.utils.lf(), XnatItem, attr)


        # Parse json
        for i in self.getJson(os.path.dirname(XnatItem)):
            for key, val in i.iteritems():
                if val == os.path.basename(XnatItem):
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



    
        
    def makeDir(self, XnatPath): 
        """ Makes a directory in Xnat via PUT
        """ 
        r = self.httpsRequest('PUT', XnatPath)
        #print "%s Put Dir %s \n%s"%(self.browser.utils.lf(), XnatPath, r)
        return r








            







        



