from XnatLoadWorkflow import *



comment = """
XnatSceneLoadWorkflow
"""


class XnatSceneLoadWorkflow(XnatLoadWorkflow):
    """ Descriptor
    """



    def initLoad(self, args):
        self.load(args)



        
    def load(self, args):
        """ Descriptor
        """

        #
        # Superclass call.
        #
        super(XnatSceneLoadWorkflow, self).load(args)

        
        #
        # Get scene package
        #
        self.browser.XnatCommunicator.getFile({self.xnatSrc : self.localDst})
        #print(self.browser.utils.lf() +  "Decompressing " + os.path.basename(self.xnatSrc))

        
        #    
        # If the package does not exist, then exit.
        # (This is the result of a Cancel) 
        #
        if not os.path.exists(self.localDst):
            print "%s exiting workflow..."%(self.browser.utils.lf())  
            self.browser.XnatView.setEnabled(True) 
            return False       

        
        #
        #  Analyze package to determine scene type
        #
        fileInfo = XnatFileInfo(remoteURI = self.xnatSrc, localURI = self.localDst)
        packageInfo = self.analyzePackage(fileInfo) 
        newMRMLFile = self.prepSelfContainedScene(packageInfo)

        
        #
        # Load is good if mrml file is returned
        #
        if newMRMLFile: 
            return self.loadFinish(newMRMLFile)    
        
        return False



    
    def decompressPackagedScene(self, packageFileName, destDir):
        """ Descriptor
        """
        fileURLs = []

        
        # Zip handling
        if packageFileName.endswith('zip'):
            z = zipfile.ZipFile(packageFileName)
            try:               
                z.extractall(destDir)
                for root, subFolders, files in os.walk(destDir):
                    for file in files:
                        fileURLs.append(self.utils.adjustPathSlashes(os.path.join(root,file)))
            except Exception, e:
                print ("Extraction error: %s"%(str(e)))

                
        # *.mrb handling
        elif packageFileName.endswith('mrb'):          
            logic = slicer.app.applicationLogic()
            if not os.path.exists(destDir):
                os.makedirs(destDir)
            logic.Unzip(packageFileName, destDir)
            mrbDir = os.path.join(destDir, os.path.basename(packageFileName).split(".")[0])
            # MRB files decompress to a folder of the same name.  
            # Need to move all the files back to destDir.
            fileURLs = self.utils.moveDirContents(mrbDir, destDir) 
        return fileURLs



    
    def analyzePackage(self, currXnatFileInfo):
        """ Checks downloaded scene file for its contents.  Delegates how to handle it accordingly.
        """
        

        # Decompress scene, get files
        extractDir = self.utils.tempPath
        tempUnpackDir = os.path.join(extractDir, currXnatFileInfo.basenameNoExtension)
        fileList = self.decompressPackagedScene(currXnatFileInfo.localURI, tempUnpackDir)

        
        # Return dictionary of useful params
        return {'basename': currXnatFileInfo.basename, 
                'unpackDir': tempUnpackDir, 
                'nameOnly': currXnatFileInfo.basenameNoExtension, 
                'remoteURI': currXnatFileInfo.remoteURI, 
                'localURI': currXnatFileInfo.localURI}



    
    def prepSelfContainedScene(self, packageInfo):
        """ Loads the scene package if the scene was created 
        outside of the module's packaging workflow (XnatScenePacakger)."""

        
        # Cache the scene     
        self.storeSceneLocally(packageInfo, False)    

        
        # Deconstruct package info
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']

        
        # Get mrmls and nodes within package
        fileList = []
        rootdir = self.cachePathDict['localFiles']
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                fileList.append(os.path.join(root,file))
        loadables = self.getLoadables_byList(fileList)
        imageFiles = loadables['ALLIMAGES']
        mrmlFiles = loadables['MRMLS']
        parseableFiles = loadables['ALLNONMRML']

        
        # define relevant paths
        newRemoteDir = self.utils.getParentPath(remoteURI, "resources")
        filePathsToChange = {}

        
        # Cache images and sharables
        for pFile in parseableFiles:
            pFileBase = os.path.basename(pFile)
            if os.path.basename(os.path.dirname(pFile)) == "Data":
                # special case for url encoding
                filePathsToChange[os.path.basename(urllib2.quote(pFileBase))] = "./Data/" + urllib2.quote(pFileBase)

                

        # Parse mrml, updating paths to relative
        newMRMLFile = self.utils.appendFile(mrmlFiles[0], "-LOCALIZED")       
        #
        # NOTE: Parsing of the MRML is needed because node filePaths are absolute, not relative.
        # TODO: Submit a change request for absolute path values to Slicer
        #
        mrmlParser = XnatMrmlParser(self.browser)
        mrmlParser.changeValues(mrmlFiles[0], newMRMLFile,  {},  None, True)
        return newMRMLFile



    
    
    def storeSceneLocally(self, packageInfo, cacheOriginalPackage = True):
        """ Creates a project cache (different from an image cache) based on
        """  
        

        # Init params         
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']

        

        # Establish caching directories
        sceneDir = os.path.join(self.utils.projectPath, sceneName)
        if not os.path.exists(sceneDir): os.mkdir(sceneDir)       
        self.cachePathDict = {'localFiles': os.path.join(sceneDir, 'localFiles'),
                              'cacheManager': os.path.join(sceneDir, 'cacheManagement'),
                              'originalPackage': os.path.join(sceneDir, 'originalPackage')}

        

        # Create relevant paths locally
        for value in self.cachePathDict.itervalues(): 
            if not os.path.exists(value):
                try: os.makedirs(value)
                except Exception, e: 
                    print("Couldn't make the following directory: %s\nRef. Error: %s"%(value, str(e)))# {} for some strange reason!").format(str(value))
            else:
                #print (self.utils.lf() + "REMOVING EXISTING FILES IN '%s'"%(value))
                self.utils.removeFilesInDir(value)

                
        # Move unpacked contents to new directory
        self.utils.moveDirContents(extractDir, self.cachePathDict['localFiles'])

        

        # Move package as well to cache, if desired 
        if cacheOriginalPackage:
            qFile = qt.QFile(localURI)
            qFile.copy(os.path.join(self.cachePathDict['originalPackage'], scenePackageBasename))
            qFile.close()

            
        # Delete package
        try:
            os.remove(localURI)
        except Exception, e:
            print "Can't remove the moved file -- a thread issue."



            
    def loadFinish(self, fileName, specialCaseFiles = None):
        """Loads a scene from a .mrml file.
           Also updates the UI locking and Status components.
           """

           
        # Call loadscene
        #print( "Loading '" + os.path.basename(self.xnatSrc) + "'")
        slicer.util.loadScene(fileName) 
        
        sessionArgs = XnatSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "scene download"
        self.browser.XnatView.startNewSession(sessionArgs)
        
        print( "\nScene '%s' loaded."%(os.path.basename(fileName.rsplit(".")[0])))  

        

        # Enable view in browser
        self.browser.XnatView.setEnabled(True)
        return True
