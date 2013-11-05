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
XnatIo uses httplib to send/receive commands and files to an Xnat host
Since input is usually string-based, there are several utility methods in this
class to clean up strings for input to httplib. 

TODO:
"""



class XnatIo(object):
    """ Communication class to Xnat.  Urllib2 is the current library.
    """

        
    def setup(self, MODULE, host, user, password):
        """ Setup function.  Initializes the internal variables. 
            A 'setup' paradigm is employed, as opposed
            to an 'init' paradim, because the XnatIo object is created, but
            not logged into until the user enters the relvant information.
        """

        #-------------------
        # Set relevant variables (all required)
        #-------------------
        self.projectCache = None
        self.MODULE = MODULE
        self.host = host
        self.user = user
        self.password = password


        
        #-------------------
        # Tracking dictionary for download modal.
        #-------------------
        self.downloadTracker = {
            'totalDownloadSize': {'bytes': None, 'MB': None},
            'downloadedSize': {'bytes': None, 'MB': None},
        }


        #-------------------
        # Relevant objects for httpsRequests
        #-------------------        
        self.userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
        self.authenticationHeader = { 'Authorization' : 'Basic %s' %(self.userAndPass) }
        self.fileDict = {};



    
    def getFilesByUrl(self, srcDstMap, withProgressBar = True, fileOrFolder = None): 
        """ Returns a list of files provided but the URLs contianed within
            the 'srcDstMap' argument.  Other arguments are self-explanatory.
        """

        #--------------------
        # Reset total size of downloads for all files
        #-------------------------
        self.downloadTracker['totalDownloadSize']['bytes'] = 0
        self.downloadTracker['downloadedSize']['bytes'] = 0
        downloadFolders = []


        
        #-------------------------
        # Remove existing dst files from their local URL
        #-------------------------
        clearedDirs = []
        for src, dst in srcDstMap.iteritems(): 
            basename = os.path.basename(dst)
            if not any(basename in s for s in clearedDirs):
                if os.path.exists(basename):
                    self.MODULE.utils.removeFileInDir(basename)
                    clearedDirs.append(basename)
                    
       
        
        #-------------------------
        # If we're downloading a single file...
        #-------------------------
        if fileOrFolder == "file":
            for src, dst in srcDstMap.iteritems():
                print("%s file download\nsrc: '%s' \ndst: '%s'"%(self.MODULE.utils.lf(), src, dst))
                fName = os.path.basename(src)
                fUri = "/projects/" + src.split("/projects/")[1]
                self.get(src, dst)


                
        #-------------------------
        # Otherwise download folder...
        #-------------------------                                   
        elif fileOrFolder == "folder":
            import tempfile
            xnatFileFolders = []
            #
            # Determine source folders from XNAT host, 
            # add them to the list 'xnatFileFolders'
            #
            for src, dst in srcDstMap.iteritems():
                srcFolder = os.path.dirname(src)
                if not srcFolder in xnatFileFolders:
                    xnatFileFolders.append(srcFolder)                 
            #
            # Loop through folders to create a dictionary
            # that maps the remote URIs with local URIs 
            # for downloading.
            #
            for xnatFileFolder in xnatFileFolders:
                if withProgressBar: 
                    #
                    # Create src, dst strings.
                    #
                    src = (xnatFileFolder + "?format=zip")                 
                    dst = tempfile.mktemp('', 'XnatDownload', self.MODULE.GLOBALS.LOCAL_URIS['downloads']) + ".zip"
                    downloadFolders.append(self.MODULE.utils.adjustPathSlashes(dst))
                    #
                    # Remove existing dst files, if they exist.
                    #
                    if os.path.exists(dst): 
                        self.MODULE.utils.removeFile(dst)
                    # 
                    # Begin the download process.
                    #
                    print("%s folder downloading %s to %s"%(self.MODULE.utils.lf(), src, dst))
                    self.get(src, dst)


                    
        #-------------------------
        # Return 'downloadFolders'.
        #------------------------- 
        return downloadFolders



    
    @property
    def queryArguments(self):
        """ For appending to a URL when querying for metadata.
        """
        return {'accessible' : 'accessible=true',
                'imagesonly' : 'xsiType=xnat:imageSessionData',
                }


    
    
    def upload(self, localSrcUri, remoteDstUri, delExisting = True):
        """ Upload a file to an XNAT host using Python's 'urllib2' library.
            The argument 'localSrcUri' provides the relvant path to
            the file that will be uploaded.  The argument 'remoteDstUri'
            provides the relevant path to the destination on a given
            XNAT host.  
        """

        
        #-------------------- 
        # Read 'localSrcUri'
        #-------------------- 
        f = open(localSrcUri, 'rb')
        filebody = f.read()
        f.close()



        #-------------------- 
        # Delete existing remoteDstUri from XNAT host.
        #-------------------- 
        if delExisting:
            self.httpsRequest('DELETE', remoteDstUri, '')
        print "%s Uploading\nsrc: '%s'\nremoteDstUri: '%s'"%(self.MODULE.utils.lf(), localSrcUri, remoteDstUri)


        
        #-------------------- 
        # Clean 'remoteDstUri' string and endcode
        #-------------------- 
        if not remoteDstUri.startswith(self.host + '/data'):
            remoteDstUri = self.host + '/data' + remoteDstUri
        print remoteDstUri
        remoteDstUri = str(remoteDstUri).encode('ascii', 'ignore')


        
        #-------------------- 
        # Get request and connection from XNAT host using
        # the URIs provided and the methods of urllib2
        #-------------------- 
        req = urllib2.Request(remoteDstUri)
        connection = httplib.HTTPSConnection (req.get_host())  



        #-------------------- 
        # Make the authentication header to 
        # pass to the connection.
        #-------------------- 
        userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")       
        header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}    



        #-------------------- 
        # Do 'PUT' REST call, providing the file
        # and the authentication header.
        #-------------------- 
        connection.request ('PUT', req.get_selector(), body = filebody, headers = header)



        #-------------------- 
        # Get and return the response from the connetion.
        #-------------------- 
        response = connection.getresponse()
        #print "response: ", response.read()  
        return response
        

        
        
    def httpsRequest(self, restMethod, xnatUri, body='', headerAdditions={}):
        """ Allows the user to make httpsRequests to an XNAT host
            using RESTful methods provided in the argument 'restMethod'.  The argument
            'xnatUri' is the URI that points to a given location to conduct the
            rest call.  This could be a file or filder using the compatible
            REST methods.
        """

        #-------------------- 
        # Clean REST method
        #-------------------- 
        restMethod = restMethod.upper()


        #-------------------- 
        # Clean URL
        #-------------------- 
        prepender = self.host.encode("utf-8") + '/data'
        url =  prepender +  xnatUri.encode("utf-8") if not prepender in xnatUri else xnatUri


        #-------------------- 
        # Get request using 'urllib2'
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
        # Conduct REST call
        #-------------------- 
        connection.request(restMethod, req.get_selector (), body = body, headers = header)
        #print ('%s httpsRequest: %s %s')%(self.MODULE.utils.lf(), restMethod, url)


        #-------------------- 
        # Return response
        #-------------------- 
        return connection.getresponse ()



    
    def delete(self, xnatUri):
        """ Deletes a given file or folder from an XNAT host
            based on the 'xnatUri' argument.  Calls on the internal
            'httpsRequest' RESTfully.
        """
        print "%s deleting %s"%(self.MODULE.utils.lf(), xnatUri)
        self.httpsRequest('DELETE', xnatUri, '')


        
        
    def cancelDownload(self):
        """ Set's the download state to 0.  The open buffer in the 'GET' method
            will then read this download state, and cancel out.
        """
        print self.MODULE.utils.lf(), "Canceling download."
        self.MODULE.XnatDownloadPopup.window.hide()
        self.MODULE.XnatDownloadPopup.reset()
        self.downloadState = 0
        self.MODULE.XnatView.setEnabled(True)
        


        
    def downloadFailed(self, windowTitle, msg):
        """ Opens a QMessageBox informing the user
            of the faile download.
        """
        qt.QMessageBox.warning(None, windowTitle, msg)


            

    def getFile(self, srcDstMap, withProgressBar = True):
        """ As stated.
        """
        return self.getFilesByUrl(srcDstMap, fileOrFolder = "file")



    
    def getFiles(self, srcDstMap, withProgressBar = True):
        """ As stated.
        """
        return self.getFilesByUrl(srcDstMap, fileOrFolder = "folder")
    


    
    def get(self, xnatSrcUri, localDstUri, showProgressIndicator = True):
        """ RESTfully calls on a 'GET' command to a given XNAT host and
            then downloads the response to the 'localDstUri' argument.
        """

        #-------------------- 
        # A download state of '1' indicates
        # that the user hasn't cancelled the download.
        #-------------------- 
        self.downloadState = 1

        
        
        #-------------------- 
        # Set the src URI based on the 
        # internal variables of XnatIo.
        #-------------------- 
        xnatSrcUri = self.host + "/data/archive" + xnatSrcUri if not self.host in xnatSrcUri else xnatSrcUri

        

        #-------------------- 
        # Construct the authentication handler
        #-------------------- 
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, xnatSrcUri, self.user, self.password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)


        
        #-------------------- 
        # Open the local destination file 
        # so that it can start reading in the buffers.
        #-------------------- 
        XnatFile = open(localDstUri, "wb")
      


        #-------------------- 
        # Get the response URL from the XNAT host.
        #-------------------- 
        errorString = ""
        try:
            print self.MODULE.utils.lf(), "xnatSrcUri: ", xnatSrcUri
            response = urllib2.urlopen(xnatSrcUri)

        #
        # If the urllib2 version fails (some servers do not like
        # the communication method), then use httplib.
        #
        except Exception, e:
            errorString += str(e) + "\n"
 
            try:
                print self.MODULE.utils.lf(), "urllib2 get failed.  Attempting httplib version."
                #------------
                # HTTP LIB VERSION
                #-----------
                #
                # Reset popup
                #
                self.MODULE.XnatDownloadPopup.reset()
                self.MODULE.XnatDownloadPopup.setDownloadFilename(xnatSrcUri) 
                self.MODULE.XnatDownloadPopup.show()
                self.MODULE.XnatDownloadPopup.setDownloadFileSize(0)
                self.MODULE.XnatDownloadPopup.update(0)
                #
                # Establish Credentials
                #
                url = xnatSrcUri
                userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")
                authenticationHeader = { 'Authorization' : 'Basic %s' %(userAndPass) }
                #
                # Clean REST method string
                #
                restMethod = 'GET'
                #
                # Clean url
                #
                url = url.encode("utf-8")
                #
                # Begin request.
                #
                req = urllib2.Request (url)
                #
                # Get the connection
                #
                connection = httplib.HTTPSConnection (req.get_host ()) 
                #
                # Merge the authentication header with any other headers.
                #
                headerAdditions={}
                header = dict(authenticationHeader.items() + headerAdditions.items())
                #
                # Conduct the REST call.
                #
                connection.request (restMethod, req.get_selector (), body= '', headers=header)
                print "%s Xnat request - %s %s"%(self.MODULE.utils.lf(), restMethod, url)
                #
                # Return response
                #
                response = connection.getresponse()
                data = response.read()           
                XnatFile.close()
                #
                # Write the response data to file.
                #
                with open(localDstUri, 'wb') as f:
                    f.write(data)

                #
                # Enable the view widget.
                #
                self.MODULE.XnatView.setEnabled(True)
                self.MODULE.XnatDownloadPopup.hide()
                return
                
            except Exception, e2:
                errorString += str(e2)
                qt.QMessageBox.warning( None, "Xnat Error", errorStrings)
                self.MODULE.XnatView.setEnabled(True)
                return


        
        #-------------------- 
        # Get the content size, first by checking log, then by reading header
        #-------------------- 
        self.downloadTracker['downloadedSize']['bytes'] = 0   
        self.downloadTracker['totalDownloadSize'] = self.getSize(xnatSrcUri)
  
        if not self.downloadTracker['totalDownloadSize']['bytes']:
          
            # If not in log, read the header
            if response.headers and "Content-Length" in response.headers:
                self.downloadTracker['totalDownloadSize']['bytes'] = int(response.headers["Content-Length"])  
                self.downloadTracker['totalDownloadSize']['MB'] = self.MODULE.utils.bytesToMB(self.downloadTracker['totalDownloadSize']['bytes'])


            
        #-------------------- 
        # Adjust MODULE View UI.
        #-------------------- 
        self.MODULE.XnatView.setEnabled(False)

        

        #-------------------- 
        # Define buffer read function
        #-------------------- 
        def buffer_read(response, fileToWrite, buffer_size=8192, currSrc = "", fileDisplayName = ""):
            """Downloads files by a constant buffer size.
            """

            #-------------------- 
            # If a progress indicator is desired,
            # set the parameters of self.MODULE.XnatDownloadPopup.
            #-------------------- 
            if showProgressIndicator:
                #
                # Reset popup
                #
                self.MODULE.XnatDownloadPopup.reset()
                #
                # Set filename
                #
                self.MODULE.XnatDownloadPopup.setDownloadFilename(fileDisplayName) 
                self.MODULE.XnatDownloadPopup.show()
                self.MODULE.XnatDownloadPopup.setDownloadFileSize(0)
                self.MODULE.XnatDownloadPopup.update(0)
                #
                # Update the download popup file size
                #
                if self.downloadTracker['totalDownloadSize']['bytes']:
                    self.MODULE.XnatDownloadPopup.setDownloadFileSize(self.downloadTracker['totalDownloadSize']['bytes'])
                    #
                    # Wait for threads to catch up 
                    #
                    slicer.app.processEvents()


                    
            #--------------------
            # Disable view widget
            #--------------------
            self.MODULE.XnatView.setEnabled(False)


            
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
                    self.MODULE.utils.removeFile(fileToWrite.name)
                    break
                #
                # Read buffer
                #
                buffer = response.read(buffer_size)
                if not buffer: 
                    if self.MODULE.XnatDownloadPopup:
                        self.MODULE.XnatDownloadPopup.hide()
                        break 
                #    
                # Write buffer chunk to file
                #
                fileToWrite.write(buffer)
                #    
                # Update progress indicators
                #
                self.downloadTracker['downloadedSize']['bytes'] += len(buffer)
                if showProgressIndicator and self.MODULE.XnatDownloadPopup:
                    self.MODULE.XnatDownloadPopup.update(self.downloadTracker['downloadedSize']['bytes'])
                #   
                # Wait for threads to catch up      
                #
                slicer.app.processEvents()
                
            return self.downloadTracker['downloadedSize']['bytes']


        
        #-------------------- 
        # Read buffers (cyclical)
        #-------------------- 
        fileDisplayName = os.path.basename(xnatSrcUri) if not 'format=zip' in xnatSrcUri else xnatSrcUri.split("/subjects/")[1]  
        bytesRead = buffer_read(response = response, fileToWrite = XnatFile, 
                                buffer_size = 8192, currSrc = xnatSrcUri, fileDisplayName = fileDisplayName)


        
        #-------------------- 
        # When finished, reenable Viewer and close the file
        #-------------------- 
        self.MODULE.XnatView.setEnabled(True)
        XnatFile.close()

    
            
        
    def getJson(self, xnatUri):
        """ Returns a json object from a given XNATURI using
            the internal method 'httpsRequest'.
        """

        #-------------------- 
        # Get the response from httpRequest
        #--------------------      
        response = self.httpsRequest('GET', xnatUri).read()
        print "%s %s"%(self.MODULE.utils.lf(), xnatUri)
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
            print "%s login error to host '%s'!"%(self.MODULE.utils.lf(), self.host)
            return XnatError(self.host, self.user, response)



    
    
    def getXnatUriAt(self, xnatUri, level):
        """ Returns the XNAT path from 'xnatUri' at the 
            provided 'level' by splicing 'xnatUri' accordingly.
        """
        #print "%s %s"%(self.MODULE.utils.lf(), xnatUri, level)
        if not level.startswith('/'):
            level = '/' + level
        if level in xnatUri:
            return  xnatUri.split(level)[0] + level
        else:
            raise Exception("%s invalid get level '%s' parameter: %s"%(self.MODULE.utils.lf(), xnatUri, level))

        

        
    def fileExists(self, fileUri):
        """ Determines whether a file exists
            on an XNAT host based on the 'fileUri' argument.
        """
        #print "%s %s"%(self.MODULE.utils.lf(), fileUri)

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
        # Parse result dictionary and 
        # return the boolean.
        #-------------------- 
        for i in self.getJson(parentDir):
            if os.path.basename(fileUri) in i['Name']:
                return True   
        return False
    


    
    def getSize(self, fileUri):
        """ Retrieves a tracked file's size and 
            converts it to MB based on the 'self' variable
            'fileDict' which contains the raw byte size 
            of the given file.
        """
        #print "%s %s"%(self.MODULE.utils.lf(), fileUri)
        #--------------------
        # Query the tracked files by the name
        # of the fileUri.
        #--------------------
        bytes = 0
        fileName = os.path.basename(fileUri)
        if fileName in self.fileDict:
            bytes = int(self.fileDict[fileName]['Size'])
            return {"bytes": (bytes), "MB" : self.MODULE.utils.bytesToMB(bytes)}

        return {"bytes": None, "MB" : None}


    
    
    def applyQueryArgumentsToUri(self, queryUri, queryArguments):
        """ Using the static variable self.queryArguments dictionary,
            appends the relevant arguments to a given queryURI.
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
        """ Returns the contents of a given folder provided in the arguments
            'queryUris'.  Returns an object based on the 'metadataTags' argument
            that the 'queryUri' gets return.  The 'queryArguments' parameter
            deals generally with fitering certain contents within a given folder. 
            For instance, to get projects only the user has access to, the URI needs
            to be appended with '?accessible=True'.
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
        # Acquire contents via 'self.getJson'
        #-------------------- 
        contents = []
        for queryUri in queryUris:
            newQueryUri = queryUri
            #
            # Apply query arguments.
            #
            if queryArguments:
                newQueryUri = self.applyQueryArgumentsToUri(queryUri, queryArguments)
                
            print "%s query path: %s"%(self.MODULE.utils.lf(), newQueryUri)
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
            # If we want the projects, store projects in a dictionary. 
            # 'self.projectCache' is reset if the user logs into a new host or 
            # logs in a again.
            #
            if queryUri.endswith('/projects'):
                self.projectCache = contents


                
        #-------------------- 
        # Exit out if there are non-Json or XML values.
        #-------------------- 
        if str(contents).startswith("<?xml"): return [] # We don't want text values

        

        #-------------------- 
        # Get other attributes with the contents 
        # for metadata tracking.
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
                #print "%s %s"%(self.MODULE.utils.lf(), self.fileDict)
            elif queryUri.endswith('/projects'):
                self.projectCache = returnContents


                
        #-------------------- 
        # Return the contents of the folder as a
        # dictionary of arrays
        #-------------------- 
        return returnContents



    
    def getResources(self, folder):
        """ Gets the contents of a 'resources' folder
            in a given XNAT host.  'resources' folders 
            demand a bit mors specifity in the metadata manipulation.
            Furthermore, 'resources' folders are frequently accessed
            as part of the Slicer file location within an 'experiment'.
        """

        #-------------------- 
        # Get the resource JSON
        #-------------------- 
        folder += "/resources"
        resources = self.getJson(folder)
        #print "%s %s"%(self.MODULE.utils.lf(), folder)
        #print self.MODULE.utils.lf() + " Got resources: '%s'"%(str(resources))


        
        #-------------------- 
        # Filter the JSONs
        #-------------------- 
        resourceNames = []
        for r in resources:
            if 'label' in r:
                resourceNames.append(r['label'])
                #print (self.MODULE.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['label']))
            elif 'Name' in r:
                resourceNames.append(r['Name'])
                #print (self.MODULE.utils.lf() +  "FOUND RESOURCE ('%s') : %s"%(folder, r['Name']))                
            
            return resourceNames




    def getItemValue(self, XnatItem, attr):
        """ Retrieve an item by one of its attributes
        """

        #-------------------- 
        # Clean string
        #-------------------- 
        XnatItem = self.cleanUri(XnatItem)
        #print "%s %s %s"%(self.MODULE.utils.lf(), XnatItem, attr)


        
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
        """ Makes a directory in Xnat via a PUT command.
        """ 
        result = self.httpsRequest('PUT', XnatUri)
        #print "%s Put Dir %s \n%s"%(self.MODULE.utils.lf(), XnatUri, r)
        return result



            

    def search(self, searchString):
        """ Utilizes the XNAT search query function
            to on all levels of XNAT based on the provided
            searchString.  Searches through the available
            columns as described below.
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


        
        #-------------------- 
        # Looping through all of the levels,
        # constructing a searchQuery for each based
        # on the releant columns.
        #--------------------       
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


        
        return resultsDict

            



    def makeFolder(self, remoteDstUri):
        """ 
        """
        
        #-------------------- 
        # Clean 'remoteDstUri' string and endcode
        #-------------------- 
        if not remoteDstUri.startswith(self.host + '/data'):
            remoteDstUri = self.host + '/data' + remoteDstUri
        remoteDstUri = str(remoteDstUri).encode('ascii', 'ignore')


        
        #-------------------- 
        # Get request and connection from XNAT host using
        # the URIs provided and the methods of urllib2
        #-------------------- 
        req = urllib2.Request(remoteDstUri)
        connection = httplib.HTTPSConnection (req.get_host())  



        #-------------------- 
        # Make the authentication header to 
        # pass to the connection.
        #-------------------- 
        userAndPass = b64encode(b"%s:%s"%(self.user, self.password)).decode("ascii")       
        header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}    



        #-------------------- 
        # Do 'PUT' REST call, providing the file
        # and the authentication header.
        #-------------------- 
        connection.request ('PUT', req.get_selector(), headers = header)



        #-------------------- 
        # Get and return the response from the connetion.
        #-------------------- 
        response = connection.getresponse()
        print "MAKE FOLDER", response.read()
        return response





        



