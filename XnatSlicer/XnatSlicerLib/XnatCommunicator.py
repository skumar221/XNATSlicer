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
from multiprocessing import Pool

from XnatError import *



comment = """
XnatCommunicator uses httplib to send/receive commands and files to an Xnat host
Since input is usually string-based, there are several utility methods in this
class to clean up strings for input to httplib. 

TODO:
"""



class XnatCommunicator(object):
    """ Communication class to Xnat.  Urllib2 is the current library.
    """

        
    def setup(self, browser, host, user, password):

        self.projectCache = None
        self.browser = browser
        self.host = host
        self.user = user
        self.password = password


        self.downloadTracker = {
            'totalDownloadSize': {'bytes': None, 'MB': None},
            'downloadedSize': {'bytes': None, 'MB': None},
        }

        self.userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
        self.authenticationHeader = { 'Authorization' : 'Basic %s' %(self.userAndPass) }
        self.fileDict = {};



    
    def getFilesByUrl(self, srcDstMap, withProgressBar = True, fileOrFolder = None): 

        print self.browser.utils.lf(), srcDstMap

        timeStart = time.time()
        
        #--------------------
        # Reset total size of downloads for all files
        #-------------------------
        self.downloadTracker['totalDownloadSize']['bytes'] = 0
        self.downloadTracker['downloadedSize']['bytes'] = 0
        downloadFolders = []


        t = time.time()
        print (self.browser.utils.lf(), t, "Remove existing - start")
        #-------------------------
        # Remove existing dst files
        #-------------------------
        clearedDirs = []
        for src, dst in srcDstMap.iteritems(): 
            basename = os.path.basename(dst)
            if not any(basename in s for s in clearedDirs):
                if os.path.exists(basename):
                    self.browser.utils.removeFileInDir(basename)
                    clearedDirs.append(basename)
                    
        print (self.browser.utils.lf(), t-time.time(), "Remove existing - end")

        
        #-------------------------
        # Download files
        #-------------------------
        if fileOrFolder == "file":
            for src, dst in srcDstMap.iteritems():
                print("%s file download\nsrc: '%s' \ndst: '%s'"%(self.browser.utils.lf(), src, dst))

                fName = os.path.basename(src)
                fUri = "/projects/" + src.split("/projects/")[1]
                self.get(src, dst)

                                    
        elif fileOrFolder == "folder":
            import tempfile
            xnatFileFolders = []


            t = time.time()
            print (self.browser.utils.lf(), t, "Determine source folders - start")

            #---------------------
            # Determine source folders, create new dict based on basename
            #---------------------
            for src, dst in srcDstMap.iteritems():
                print("FOLDER D/L src:%s\tdst:%s"%(src, dst))
                srcFolder = os.path.dirname(src)
                if not srcFolder in xnatFileFolders:
                    xnatFileFolders.append(srcFolder)
                    
            print (self.browser.utils.lf(), t-time.time(), "Determine source folders - end")
                    
                    
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

        #-------------------- 
        # Clean REST method
        #-------------------- 
        restMethod = restMethod.upper()


        #-------------------- 
        # Clean url
        #-------------------- 
        prepender = self.host.encode("utf-8") + '/data'
        url =  prepender +  xnatSelector.encode("utf-8") if not prepender in xnatSelector else xnatSelector


        #-------------------- 
        # Get request
        #-------------------- 
        req = urllib2.Request (url)


        #-------------------- 
        # Get connection
        #-------------------- 
        connection = httplib.HTTPSConnection (req.get_host ()) 


        #-------------------- 
        # Merge the authentication header with any other headers
        #-------------------- 
        header = dict(self.authenticationHeader.items() + headerAdditions.items())


        #-------------------- 
        # REST call
        #-------------------- 
        connection.request(restMethod, req.get_selector (), body = body, headers = header)
        #print ('%s httpsRequest: %s %s')%(self.browser.utils.lf(), restMethod, url)


        #-------------------- 
        # Return response
        #-------------------- 
        return connection.getresponse ()



    
    def delete(self, selStr):
        """ Description
        """
        print "%s deleting %s"%(self.browser.utils.lf(), selStr)
        self.httpsRequest('DELETE', selStr, '')


        
        
    def cancelDownload(self):
        """ Set's the download state to 0.  The open buffer in the 'get' method
            will then read this download state, and cancel out.
        """
        print self.browser.utils.lf(), "Canceling download."
        self.browser.downloadPopup.window.hide()
        self.browser.downloadPopup.reset()
        self.downloadState = 0
        self.browser.XnatView.setEnabled(True)
        


        
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
        # Reset popup
        return self.getFilesByUrl(srcDstMap, fileOrFolder = "folder")
    


    
    def get(self, XnatSrc, dst, showProgressIndicator = True):
        """ Descriptor
        """

        self.downloadState = 1
        
        #-------------------- 
        # Set the path
        #-------------------- 
        XnatSrc = self.host + "/data/archive" + XnatSrc if not self.host in XnatSrc else XnatSrc

        

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
        errorString = ""
        try:
            print self.browser.utils.lf(), "XnatSrc: ", XnatSrc
            response = urllib2.urlopen(XnatSrc)
        except Exception, e:
            errorString += str(e) + "\n"

            #-------------------
            # If the urllib2 version fails, try the httplib version
            #-------------------
            try:
                print self.browser.utils.lf(), "urllib2 get failed.  Attempting httplib version."
                #------------
                # HTTP LIB VERSION
                #-----------

                #
                # Reset popup
                #
                self.browser.downloadPopup.reset()
                self.browser.downloadPopup.setDownloadFilename(XnatSrc) 
                self.browser.downloadPopup.show()
                #
                # Credentials
                #
                url = XnatSrc
                userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
                authenticationHeader = { 'Authorization' : 'Basic %s' %(userAndPass) }
                #
                # Clean REST method
                #
                restMethod = 'GET'
                #
                # Clean url
                #
                url = url.encode("utf-8")
                #
                # Get request
                #
                req = urllib2.Request (url)
                #
                # Get connection
                #
                connection = httplib.HTTPSConnection (req.get_host ()) 
                #
                # Merge the authentication header with any other headers
                #
                headerAdditions={}
                header = dict(authenticationHeader.items() + headerAdditions.items())
                #
                # REST call
                #
                connection.request (restMethod, req.get_selector (), body= '', headers=header)
                print "%s Xnat request - %s %s"%(self.browser.utils.lf(), restMethod, url)
                #
                # Return response
                #
                response = connection.getresponse()
                data = response.read()           
                XnatFile.close()
                #
                # write to file
                #
                with open(dst, 'wb') as f:
                    f.write(data)
                self.browser.XnatView.setEnabled(True)
                self.browser.downloadPopup.hide()
                return
                
            except Exception, e2:
                errorString += str(e2)
                qt.QMessageBox.warning( None, "Xnat Error", errorStrings)
                self.browser.XnatView.setEnabled(True)
                return


        
        #-------------------- 
        # Get the content size, first by checking log, then by reading header
        #-------------------- 
        self.downloadTracker['downloadedSize']['bytes'] = 0   
        self.downloadTracker['totalDownloadSize'] = self.getSize(XnatSrc)
  
        if not self.downloadTracker['totalDownloadSize']['bytes']:
          
            # If not in log, read the header
            if response.headers and "Content-Length" in response.headers:
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

            #-------------------- 
            # If a progress indicator is desired,
            # set the parameters of self.browser.downloadPopup.
            #-------------------- 
            if showProgressIndicator:
                #
                # Reset popup
                #
                self.browser.downloadPopup.reset()
                #
                # Set filename
                #
                self.browser.downloadPopup.setDownloadFilename(fileDisplayName) 
                self.browser.downloadPopup.show()
                #
                # Update the download popup file size
                #
                if self.downloadTracker['totalDownloadSize']['bytes']:
                    self.browser.downloadPopup.setDownloadFileSize(self.downloadTracker['totalDownloadSize']['bytes'])
                    #
                    # Wait for threads to catch up 
                    #
                    slicer.app.processEvents()


                    
            #--------------------
            # Disable view widget
            #--------------------
            self.browser.XnatView.viewWidget.setEnabled(False)


            
            #--------------------
            # Define the buffer read loop
            #--------------------
            while 1:            
                #
                # If download cancelled.
                #
                if self.downloadState == 0:
                    fileToWrite.close()
                    slicer.app.processEvents()
                    self.browser.utils.removeFile(fileToWrite.name)
                    break
                #
                # Read buffer
                #
                buffer = response.read(buffer_size)
                if not buffer: 
                    if self.browser.downloadPopup:
                        self.browser.downloadPopup.hide()
                        break 
                #    
                # Write buffer chunk to file
                #
                fileToWrite.write(buffer)
                #    
                # Update progress indicators
                #
                self.downloadTracker['downloadedSize']['bytes'] += len(buffer)
                if showProgressIndicator and self.browser.downloadPopup:
                    self.browser.downloadPopup.update(self.downloadTracker['downloadedSize']['bytes'])
                #   
                # Wait for threads to catch up      
                #
                slicer.app.processEvents()
                
            return self.downloadTracker['downloadedSize']['bytes']


        
        #-------------------- 
        # Read buffers (cyclical)
        #-------------------- 
        fileDisplayName = os.path.basename(XnatSrc) if not 'format=zip' in XnatSrc else XnatSrc.split("/subjects/")[1]  
        bytesRead = buffer_read(response = response, fileToWrite = XnatFile, 
                                buffer_size = 8192, currSrc = XnatSrc, fileDisplayName = fileDisplayName)


        
        #-------------------- 
        # When finished, reenable Viewer and close the file
        #-------------------- 
        self.browser.XnatView.setEnabled(True)
        XnatFile.close()

    
            
        
    def getJson(self, url):
        """ Returns a json object from a given URL using
            the internal method 'httpsRequest'.
        """

        #-------------------- 
        # Get the response from httpRequest
        #--------------------      
        response = self.httpsRequest('GET', url).read()
        print "%s %s"%(self.browser.utils.lf(), url)
        #print "Get JSON Response: %s"%(response)


        
        #-------------------- 
        # Try to load the response as a JSON...
        #-------------------- 
        try:
            return json.loads(response)['ResultSet']['Result']


        
        #-------------------- 
        # If that fails, kick back error...
        #-------------------- 
        except Exception, e:
            print "%s login error to host '%s'!"%(self.browser.utils.lf(), self.host)
            return XnatError(self.host, self.user, response)



    
    
    def getXnatUriAt(self, url, level):
        """ Returns the XNAT path from 'url' at 'level',
        """
        #print "%s %s"%(self.browser.utils.lf(), url, level)
        if not level.startswith('/'):
            level = '/' + level
        if level in url:
            return  url.split(level)[0] + level
        else:
            raise Exception("%s invalid get level '%s' parameter: %s"%(self.browser.utils.lf(), url, level))

        

        
    def fileExists(self, fileUri):
        """ Determines whether a file exists
            on an XNAT host based on the 'fileUri' argument.
        """
        #print "%s %s"%(self.browser.utils.lf(), fileUri)

        #-------------------- 
        # Query logged files before checking
        #-------------------- 
        if (os.path.basename(fileUri) in self.fileDict):
            return True
                

        
        #-------------------- 
        # Clean string
        #-------------------- 
        parentDir = self.getXnatUriAt(fileUri, 'files');

        

        #-------------------- 
        # Parse result dictionary
        #-------------------- 
        for i in self.getJson(parentDir):
            if os.path.basename(fileUri) in i['Name']:
                return True   
        return False
    


    
    def getSize(self, fileUri):
        """ Descriptor
        """
        #print "%s %s"%(self.browser.utils.lf(), fileUri)
        bytes = 0
       
        
        # Query logged files
        fileName = os.path.basename(fileUri)
        if fileName in self.fileDict:
            bytes = int(self.fileDict[fileName]['Size'])
            return {"bytes": (bytes), "MB" : self.browser.utils.bytesToMB(bytes)}

        return {"bytes": None, "MB" : None}

    

    @property
    def queryArguments(self):
        return {'accessible' : 'accessible=true',
                'imagesonly' : 'xsiType=xnat:imageSessionData',
                }


    


    
    
    def applyQueryArgumentsToUri(self, queryUri, queryArguments):
        """ Descriptor
        """
        queryArgumentstring = ''
        for i in range(0, len(queryArguments)):
            if i == 0:
                queryArgumentstring += '?'
            else:
                queryArgumentstring += '&'
                
            queryArgumentstring += self.queryArguments[queryArguments[i].lower()]
        
        return queryUri + queryArgumentstring
        



    
    def getFolderContents(self, queryUris, metadataTags, queryArguments = None):   
        """ Descriptor
        """

        returnContents = {}


        
        #-------------------- 
        # Differentiate between a list of paths
        # and once single path (string) -- make all a list
        #-------------------- 
        if isinstance(queryUris, basestring):
           queryUris = [queryUris]


           
        #-------------------- 
        # Differentiate between a list of queryArguments
        # and once single queryArguments (string) -- make all a list
        #-------------------- 
        if isinstance(queryArguments, basestring):
           queryArguments = [queryArguments]

           
           
        #-------------------- 
        # Acquire contents
        #-------------------- 
        contents = []
        for queryUri in queryUris:
            newQueryUri = queryUri
            if queryArguments:
                newQueryUri = self.applyQueryArgumentsToUri(queryUri, queryArguments)
            print "%s query path: %s"%(self.browser.utils.lf(), newQueryUri)
            #
            # Get the JSON
            #
            json = self.getJson(newQueryUri)
            #
            # If the class name of the Json is 'XnatError'
            # return out, with the error.
            #
            if json.__class__.__name__ == 'XnatError':
                return json
            #
            # Otherwise, concatenate to rest of contents.
            #
            contents =  contents + json
            #
            # Store projects in a dictionary. 'self.projectCache'
            # is reset if the user logs into a new host or 
            # logs in a again.
            #
            if queryUri.endswith('/projects'):
                self.projectCache = contents
        if str(contents).startswith("<?xml"): return [] # We don't want text values

        

        #-------------------- 
        # Get other attributes with the contents
        #-------------------- 
        for content in contents:
            for metadataTag in metadataTags:
                if metadataTag in content:
                    #
                    # Create the object attribute if not there.
                    #
                    if not metadataTag in returnContents:
                        returnContents[metadataTag] = []
                    returnContents[metadataTag].append(content[metadataTag])


                    
        #-------------------- 
        # Track projects and files in global dict
        #-------------------- 
        for queryUri in queryUris:
            if queryUri.endswith('/files'):
                for content in contents:
                    # create a tracker in the fileDict
                    self.fileDict[content['Name']] = content
                #print "%s %s"%(self.browser.utils.lf(), self.fileDict)
            elif queryUri.endswith('/projects'):
                self.projectCache = returnContents
                            
        #return childNames, (sizes if len(sizes) > 0 else None)
        return returnContents



    
    def getResources(self, folder):
        """ Gets the contents of a 'resources' folder
            in a given XNAT host.  'resources' folders 
            demand a bit mores specifity in the metadata manipulation.
            Furthermore, 'resources' folders are frequently accessed
            as part of the Slicer file location within an experiment.
        """

        #-------------------- 
        # Get the resource JSON
        #-------------------- 
        folder += "/resources"
        resources = self.getJson(folder)
        #print "%s %s"%(self.browser.utils.lf(), folder)
        #print self.browser.utils.lf() + " Got resources: '%s'"%(str(resources))


        
        #-------------------- 
        # Filter the JSONs
        #-------------------- 
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

        #-------------------- 
        # Clean string
        #-------------------- 
        XnatItem = self.cleanUri(XnatItem)
        #print "%s %s %s"%(self.browser.utils.lf(), XnatItem, attr)


        
        #-------------------- 
        # Parse json
        #-------------------- 
        for i in self.getJson(os.path.dirname(XnatItem)):
            for key, val in i.iteritems():
                if val == os.path.basename(XnatItem):
                    if len(attr)>0 and (attr in i):
                        return i[attr]
                    elif 'label' in i:
                        return i['label']
                    elif 'Name' in i:
                        return i['Name']
 



                    
    def cleanUri(self, fileUri):
        """ Removes any double-slashes
            with single slashes.  Removes the 
            last character if the string ends
            with a '/'
        """
        if not fileUri.startswith("/"):
            fileUri = "/" + fileUri
        fileUri = fileUri.replace("//", "/")
        if fileUri.endswith("/"):
            fileUri = fileUri[:-1]
        return fileUri



    
        
    def makeDir(self, XnatUri): 
        """ Makes a directory in Xnat via PUT.
        """ 
        result = self.httpsRequest('PUT', XnatUri)
        #print "%s Put Dir %s \n%s"%(self.browser.utils.lf(), XnatUri, r)
        return result

    

    def search(self, searchString, level = None):
        """ Utilizes the XNAT search query function
            to on all levels of xnat.
        """

        searchUris = []
        resultsDict = {}
        
 
        #-------------------- 
        # Projects, subjects, experiments
        #-------------------- 
        levelTags = {}
        levelTags['projects'] = ['ID', 'secondary_ID',	'name', 'pi_firstname', 'pi_lastname', 'description']
        levelTags['subjects'] = ['ID', 'label']
        levelTags['experiments'] = ['ID', 'label']

        levels = ['projects', 'subjects', 'experiments']

        for level in levels:
            resultsDict[level] = []
            for levelTag in levelTags[level]:
                searchStr = '/%s?%s=*%s*'%(level, levelTag, searchString)
                #
                # Experiments: only search folders with images
                #
                if level == 'experiments':
                    searchStr2 = searchStr + '&xsiType=xnat:mrSessionData'
                    searchStr = searchStr + '&xsiType=xnat:petSessionData'
                    resultsDict[level] = resultsDict[level] + self.getJson(searchStr2)
                resultsDict[level] = resultsDict[level] + self.getJson(searchStr)


        #-------------------- 
        # Scans
        #-------------------- 


        #-------------------- 
        # Slicer files
        #-------------------- 

        
        return resultsDict




############################
# Static Vars
############################



XnatCommunicator.relevantMetadataDict = {

'LABELS' : [
    'ID',
    'id',
    'name',
    'Name',
    'label',
],



'projects' : [
      'last_accessed_497',
      'id'
      'ID'
#    'insert_user',
#    'pi',
#    'insert_date',
#    'description',
#    'secondary_ID',
#    'pi_lastname',
#    'pi_firstname',
#    'project_invs',	
#    'project_access_img',	
#    'user_role_497',	
#    'quarantine_status'
#    'URI',
],



'subjects' : [
     'ID',
     'label'
#    'insert_date',
#    'insert_user',
#    'totalRecords'
#    'project',
#    'URI',
],



'experiments' : [
    'ID',
    'label'
#    'insert_date',
#    'totalRecords',
#    'date',
#   'project',
#   'xsiType',
#   'ID',
#   'xnat:subjectassessordata/id',
#   'URI',
],



'scans' : [
    'series_description',
#    'note',
#    'type',
#   'xsiType',
#   'quality',
#   'xnat_imagescandata_id',
#   'URI',
],



'resources' : [
#    'element_name',
#    'category',
#    'cat_id',
#    'xnat_abstractresource_id',
#    'cat_desc'
],



'files' : [
    'Size',
#    'file_format',
#    'file_content',
#    'collection',
#    'file_tags',
#    'cat_ID',
#    'URI'
],



'slicer' : [
    'Size',
#    'file_format',
#    'file_content',
#    'collection',
#    'file_tags',
#    'cat_ID',
#    'URI'
]
        
}

            







        



