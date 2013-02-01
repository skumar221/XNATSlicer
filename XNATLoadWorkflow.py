from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile
import urllib2
from datetime import datetime

from XNATFileInfo import *
from XNATMRMLParser import *
from XNATUtils import *
from XNATScenePackager import *
from XNATTimer import *
from XNATSessionManager import *
#########################################################
#
# 
comment = """
  
  
# TODO : 
"""
#
#########################################################

def getLoader(loaderType, browser):
    #print "GET LOADER: " + loaderType
    if   loaderType == "scene": return SceneLoader(browser)
    elif loaderType == "dicom": return DICOMLoader(browser)
    elif loaderType == "file":  return FileLoader(browser)
    elif loaderType == "mass_dicom":  return DICOMLoader(browser)

class XNATLoadWorkflow(object):
    def __init__(self, browser):
        """ Parent class of any load workflow
        """
        self.utils = XNATUtils()
        self.browser = browser       
        self.mrmlParser = XNATMRMLParser(self)
        self.stopwatch = XNATTimer(self.utils)
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None
        self.isSharable = False

    def load(self, args):
        self.XNATCommunicator =  args["XNATCommunicator"]
        self.xnatSrc = args["xnatSrc"]
        self.localDst = args["localDst"]
        
    def loadFinish(self):
        pass

    def terminateLoad(self, warnStr):
        qt.QMessageBox.warning( None, warnStr[0], warnStr[1])
        self.browser.XNATView.setEnabled(True)
        
    def cacheFile(self, remoteSrc, localSrc):
        """Caches the file to a local directory set in the XNATUtils
            class
        """
        #=======================================================================
        # INIT PARAMS
        #=======================================================================
        host = ""
        #print "PATH: " + remoteSrc
        #print "HOME: " + self.utils.homePath
        #=======================================================================
        # IF ITS URI IS REMOTE
        #=======================================================================
        if ("http://" in remoteSrc) or ("https://" in remoteSrc):
            host = qt.QUrl(remoteSrc).host()
            remoteSrc = qt.QUrl(remoteSrc).path()
        #=======================================================================
        # ELIF THE FILE IN A PROJECT/SCENE CACHE
        #=======================================================================
        elif str(self.utils.projectPath) in str(remoteSrc):
            #print "FOUND FILE IN PROJECT DIRECTORY:"
            remoteSrc = remoteSrc.split(self.utils.homePath)[1]
        #=======================================================================
        # DERIVE CACHED PATH
        #=======================================================================
        cachedPath = os.path.dirname("%s%s"%(self.utils.remoteFilePath, remoteSrc)) 
        #=======================================================================
        # CREATE PATH IF IT DOESN'T EXIST
        #=======================================================================
        if not os.path.exists(cachedPath):
            #print "making directory : %s"%(cachedPath)
            os.makedirs(cachedPath)
        #=======================================================================
        # DERIVE DST FILE PATH
        #=======================================================================
        newURL = "%s/%s"%(cachedPath, os.path.basename(localSrc))
        XNATFileInfo_forCache =  XNATFileInfo(remoteURI = remoteSrc, localURI = newURL)
        XNATFileInfo_forCache.remoteHost = host
        #=======================================================================
        # MOVE FILE TO DST
        #=======================================================================
        #print "LOCALSRC %s NEWURL %s"%(localSrc, newURL)
        shutil.move(localSrc, newURL)
        #=======================================================================
        # STORE IN IMAGE CACHE IF IMAGE
        #=======================================================================
        ext = remoteSrc.split(".")[1]
          
        return cachedPath

    def getLoadables_byDir(self, rootDir):
        """Returns the loadable filenames (determined by filetype) in a dir"""
        allImages = []
        mrmls = []
        dicoms = []
    
        for folder, subs, files in os.walk(rootDir):
            for file in files:
                extension =  os.path.splitext(file)[1].lower() 
                #print ("checking DICOM extensions: " + extension)
                if self.utils.isDICOM(ext = extension):
                    dicoms.append(os.path.join(folder,file))
                    
                if self.utils.isMRML(ext = extension): 
                    mrmls.append(os.path.join(folder,file))
                elif self.utils.isSharable(ext = extension): 
                   allImages.append(os.path.join(folder,file))
        
        #print "DICOMS: "
        #for file in dicoms: print file    
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms}
    
    def getLoadables_byList(self, fileList):
        """Returns the loadable filenames (determined by filetype) in filename list"""
        allImages = []
        mrmls = []
        dicoms = []
        others = []
    
        for file in fileList:
            file = str(file)
            #print "Checking file: %s "%(str(file))
            extension =  os.path.splitext(file)[1].lower() 
            if extension or (extension != ""):
                #print ("checking DICOM extensions: " + extension)
                if self.utils.isDICOM(ext = extension):
                    dicoms.append(file)                   
                if self.utils.isMRML(ext = extension): 
                    mrmls.append(file)
                elif self.utils.isSharable(ext = extension): 
                    allImages.append(file)
                else:
                    others.append(file)

  
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms, 'OTHERS': others, 'ALLNONMRML': allImages + dicoms + others}
   
class SceneLoader(XNATLoadWorkflow):
    
    def load(self, args):
        #=======================================================================
        # CALL PARENT
        #=======================================================================
        super(SceneLoader, self).load(args)
        
        #=======================================================================
        # SET TEMPORARY SCENETYPE
        #=======================================================================
        self.isSharable = False
        
        #=======================================================================
        # GET SCENE PACKAGE
        #=======================================================================
        self.XNATCommunicator.getFile({self.xnatSrc : self.localDst})
        self.browser.updateStatus(["", "Decompressing '" + os.path.basename(self.xnatSrc) + "'", ""])
        #print ("PATH SIZE: %s"%(str(os.path.getsize(self.localDst))))
        #=======================================================================
        # ANALYZE PACKAGE TO DETERMINE SCENE TYPE
        #=======================================================================
        #print "SCENE LOADER:" + self.xnatSrc + " " + self.localDst
        fileInfo = XNATFileInfo(remoteURI = self.xnatSrc, localURI = self.localDst)
        packageInfo = self.analyzePackage(fileInfo) 
        #print "FILE INFO   : " + str(fileInfo) 
        #print "PACKAGE INFO: " + str(packageInfo) 

        newMRMLFile = self.prepSelfContainedScene(packageInfo)
        #=======================================================================
        # LOAD IS GOOD IF MRML FILE IS RETURNED
        #=======================================================================
        if newMRMLFile: 
            return self.loadFinish(newMRMLFile)    
        return False
          
    def decompressPackagedScene(self, packageFileName, destDir):
        fileURLs = []
        #=======================================================================
        # ZIP HANDLING
        #=======================================================================
        if packageFileName.endswith('zip'):
            z = zipfile.ZipFile(packageFileName)
            try:               
                z.extractall(destDir)
                for root, subFolders, files in os.walk(destDir):
                    for file in files:
                        fileURLs.append(self.utils.adjustPathSlashes(os.path.join(root,file)))
            except Exception, e:
                print ("Extraction error: %s"%(str(e)))
        #=======================================================================
        # MRB HANDLING
        #=======================================================================
        elif packageFileName.endswith('mrb'):          
            logic = slicer.app.applicationLogic()
            if not os.path.exists(destDir):
                os.makedirs(destDir)
            logic.Unzip(packageFileName, destDir)
            #slicer.app.processEvents()
            #print (self.utils.lf() + " DECOMPRESSING " + packageFileName + " TO: " + destDir)
            mrbDir = os.path.join(destDir, os.path.basename(packageFileName).split(".")[0])
            # MRB files decompress to a folder of the same name.  
            # Need to move all the files back to destDir.
            fileURLs = self.utils.moveDirContents(mrbDir, destDir) 
            #slicer.app.processEvents()
        return fileURLs
        
    def analyzePackage(self, currXNATFileInfo):
        """ Checks downloaded scene file for its contents.  Delegates how to handle it accordingly.
        """
        #=======================================================================
        # DECOMPRESS SCENE, GET FILES
        #=======================================================================
        extractDir = self.utils.tempPath
        tempUnpackDir = os.path.join(extractDir, currXNATFileInfo.basenameNoExtension)
        fileList = self.decompressPackagedScene(currXNATFileInfo.localURI, tempUnpackDir)
        #print "FILE LIST: " + str(fileList)
        #=======================================================================
        # ANALYZE PACKAGE FILES
        #=======================================================================
        self.isSharable = False;
        #=======================================================================
        # RETURN DICTIONARY OF USEFUL PARAMS
        #=======================================================================
        return {'basename': currXNATFileInfo.basename, 
                'unpackDir': tempUnpackDir, 
                'nameOnly': currXNATFileInfo.basenameNoExtension, 
                'remoteURI': currXNATFileInfo.remoteURI, 
                'localURI': currXNATFileInfo.localURI}
            
    def prepSelfContainedScene(self, packageInfo):
        """ Loads the scene package if the scene was created outside of the module's packaging workflow (XNATScenePacakger)."""
        #=======================================================================
        # CACHE THE SCENE     
        #=======================================================================
        self.storeSceneLocally(packageInfo, False)    
        #=======================================================================
        # DECONSTRUCT PACKAGE INFO
        #=======================================================================
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']
        #=======================================================================
        # GET MRMLS AND NODES WITHIN PACKAGE
        #=======================================================================
        fileList = []
        rootdir = self.cachePathDict['localFiles']
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                fileList.append(os.path.join(root,file))
        loadables = self.getLoadables_byList(fileList)
        imageFiles = loadables['ALLIMAGES']
        mrmlFiles = loadables['MRMLS']
        parseableFiles = loadables['ALLNONMRML']
        #=======================================================================
        # DEFINE RELEVANT PATHS
        #=======================================================================
        newRemoteDir = self.utils.getParentPath(remoteURI, "resources")
        filePathsToChange = {}
        #=======================================================================
        # CACHE IMAGES AND SHARABLES
        #=======================================================================
        for pFile in parseableFiles:
            #print "PARSEABLE FILES: " + pFile
            pFileBase = os.path.basename(pFile)
            if os.path.basename(os.path.dirname(pFile)) == "Data":
                #===============================================================
                # SPECIAL CASE FOR URL ENCODING
                #===============================================================
                filePathsToChange[os.path.basename(urllib2.quote(pFileBase))] = "./Data/" + urllib2.quote(pFileBase)
        #=======================================================================
        # PARSE MRML, UPDATING PATHS TO RELATIVE
        #=======================================================================
        newMRMLFile = self.utils.appendFile(mrmlFiles[0], "-LOCALIZED")
        mrmlParser = XNATMRMLParser(self.browser)
        mrmlParser.changeValues(mrmlFiles[0], newMRMLFile,  {},  None, True)
        return newMRMLFile


    def storeSceneLocally(self, packageInfo, cacheOriginalPackage = True):
        """ Creates a project cache (different from an image cache) based on
        """  
        #=======================================================================
        # INIT PARAMS         
        #=======================================================================
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']
        #=======================================================================
        # ESTABLISH CACHING DIRECTORIES
        #=======================================================================
        sceneDir = os.path.join(self.utils.projectPath, sceneName)
        if not os.path.exists(sceneDir): os.mkdir(sceneDir)       
        self.cachePathDict = {'localFiles': os.path.join(sceneDir, 'localFiles'),
                              'cacheManager': os.path.join(sceneDir, 'cacheManagement'),
                              'originalPackage': os.path.join(sceneDir, 'originalPackage')}
        #=======================================================================
        # CREATE RELEVANT PATHS LOCALLY
        #=======================================================================
        for value in self.cachePathDict.itervalues(): 
            if not os.path.exists(value):
                try: os.makedirs(value)
                except Exception, e: 
                    print("Couldn't make the following directory: %s\nRef. Error: %s"%(value, str(e)))# {} for some strange reason!").format(str(value))
            else:
                #print (self.utils.lf() + "REMOVING EXISTING FILES IN '%s'"%(value))
                self.utils.removeFilesInDir(value)
        #=======================================================================
        # MOVE UNPACKED CONTENTS TO NEW DIRECTORY
        #=======================================================================
        self.utils.moveDirContents(extractDir, self.cachePathDict['localFiles'])
        #=======================================================================
        # MOVE PACKAGE AS WELL TO CACHE, IF DESIRED 
        #=======================================================================
        if cacheOriginalPackage:
            qFile = qt.QFile(localURI)
            qFile.copy(os.path.join(self.cachePathDict['originalPackage'], scenePackageBasename))
            qFile.close()
        #=======================================================================
        # DELETE PACKAGE
        #=======================================================================
        try:
            os.remove(localURI)
        except Exception, e:
            print "Can't remove the moved file -- a thread issue."
            
    def loadFinish(self, fileName, specialCaseFiles = None):
        """Loads a scene from a .mrml file.
           Also updates the UI locking and Status components.
           """
        #=======================================================================
        # CHANGE SPECIAL CASE FILENAMES
        #=======================================================================
        if specialCaseFiles:   
            for sc_filename in specialCaseFiles: 
                if (self.utils.isDecompressible(sc_filename)):       
                     ############################################################
                     # SPECIAL CASE: .raw.gz files
                     # TODO: Class or Method in case there are more files like this
                     ############################################################
                     fnOnly = os.path.basename(sc_filename).rsplit(".")
                     self.utils.decompressFile(sc_filename)
        #slicer.app.processEvents()
        #=======================================================================
        # CALL LOADSCENE
        #=======================================================================
        self.browser.updateStatus(["", "Loading '" + os.path.basename(self.xnatSrc) + "'", ""])
        slicer.util.loadScene(fileName) 
        #slicer.app.processEvents()
        sharable = False
        
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sharable'] = self.isSharable
        sessionArgs['sessionType'] = "scene download"
        self.browser.XNATView.startNewSession(sessionArgs)
        
        self.browser.updateStatus_Locked(["", "Scene '%s' loaded."%(os.path.basename(fileName.rsplit(".")[0])), ""])  
        self.browser.generalProgressBar.setVisible(False)
        #=======================================================================
        # ENABLE VIEW IN BROWSER
        #=======================================================================
        self.browser.XNATView.setEnabled(True)
        return True

class FileLoader(XNATLoadWorkflow):
        
    def setup(self):
        pass
    
    def load(self, args):
        """Iterates through the various types of Slicer nodes by attempting to load fileName
           and reading whether or not the loadNodeFromFile method returns True or False.  
           Also updates the UI locking and Status components."""
        #=======================================================================
        # CALL PARENT
        #=======================================================================
        super(FileLoader, self).load(args)
        #=======================================================================
        # GET THE FILE
        #=======================================================================
        self.XNATCommunicator.getFile({self.xnatSrc: self.localDst})
        #slicer.app.processEvents()
        #=======================================================================
        # OPEN FILE
        #=======================================================================
        a = slicer.app.coreIOManager()
        t = a.fileType(self.localDst)
        nodeOpener = slicer.util.loadNodeFromFile(self.localDst, t)
        #=======================================================================
        # UPDATE STATUS BAR
        #=======================================================================
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sharable'] = self.isSharable
        sessionArgs['sessionType'] = "scene download"
        self.browser.XNATView.startNewSession(sessionArgs)
        
        if nodeOpener: 
            self.browser.updateStatus(["", "'%s' successfully loaded."%(os.path.basename(self.localDst)),""]) 
        else: 
            errStr = "Could not load '%s'!"%(os.path.basename(self.localDst))
            self.browser.updateStatus(["", errStr,""])
            qt.QMessageBox.warning( None, "Load Failed", errStr) 
        return nodeOpener
    
class DICOMLoader(XNATLoadWorkflow):
        
    def setup(self):
        pass
        
    def load(self, args):
        self.browser.updateStatus_Locked(["", "Downloading DICOMS...", ""]) 
        #=======================================================================
        # CALL PARENT
        #=======================================================================
        super(DICOMLoader, self).load(args)
        #=======================================================================
        # DEFINE GLOBALS
        #=======================================================================
        self.XNATLevel = os.path.basename(os.path.dirname(os.path.dirname(self.xnatSrc)))
        self.folderName = os.path.basename(os.path.dirname(self.xnatSrc))
        self.downloadables = []
        self.DICOMWidget = None
        self.newDBFile = None
        self.prevDBFile = None
        #=======================================================================
        # IS THE USER DOWNLOADING MULTIPLE FOLDERS?
        #=======================================================================
        if self.xnatSrc.endswith("files"):
            #===================================================================
            # IF NOT, PROCEED WITH LOAD
            #===================================================================
            self.proceedWithLoad('yes')
        else:
            #=======================================================================
            # If SO, THEN SETUP+SHOW DIALOG ASKING USER TO PROCEED
            #=======================================================================
            self.areYouSureDialog = qt.QMessageBox()
            self.areYouSureDialog.setIcon(4)
            #print "XNATSRC: " + self.xnatSrc
            self.areYouSureDialog.setText("You are about to load all of " +   
                                          self.folderName + "'s "+  
                                          #"(" + self.XNATLevel[:len(self.XNATLevel)-1] + ") " + 
                                          "DICOMs.\n" + 
                                          "This may take several minutes.\n" +
                                          "Are you sure you want to continue?")
            self.areYouSureDialog.addButton(qt.QMessageBox.Yes)
            self.areYouSureDialog.addButton(qt.QMessageBox.No)
            self.areYouSureDialog.connect('buttonClicked(QAbstractButton*)', self.proceedWithLoad)
            self.areYouSureDialog.show()
    
    def checkForResourceDICOMS(self, parentXNATPath):#, fileNames, XNATPath):
        """Checks if DICOM files exist at the 'resources' level.
        """
        #print ("\n\n" + self.utils.lf() + "FINDING RESOURCES IN: '%s'\n"%(parentXNATPath))
        resources = self.XNATCommunicator.getResources(parentXNATPath)      
        for res in resources:
            filePath =  "%s/resources/%s/files"%(parentXNATPath,res) 
            self.vetDICOMs(filePath, self.XNATCommunicator.getFolderContents(filePath))
    
    def vetDICOMs(self, filePath, fileNames):
        for filename in fileNames:
            try:
                ext = filename.split(".")[1]
                if self.utils.isDICOM(ext.lower()):
                    if not filePath.endswith("/"): 
                        filePath +="/"
                    #print (self.utils.lf() + " ADDING TO DICOM DOWNLOAD: '%s'"%(filePath + filename))
                    self.downloadables.append(filePath + filename)
                else:
                    print (self.utils.lf() + " NOT A DICOM: '%s'"%(filePath + filename))
            except Exception, e:
                print self.utils.lf() + "LIKELY NOT A USEABLE FILE: '%s' "%(filePath + filename) + str(e)
        
    def proceedWithLoad(self, button): 
        if ((str(button) == 'yes') or 
            (('yes' in button.text.lower()))):
            #===================================================================
            # INIT PARAMS
            #===================================================================
            experimentsList = []
            scansList = []   
            self.browser.updateStatus(["", "Downloading DICOMS in '%s'."%(os.path.dirname(self.xnatSrc)),"Please wait."])
            #print (self.utils.lf() + "Inventorying the DICOMS in '%s'."%(self.xnatSrc))            
            #===================================================================
            # REMOVE EXISTING FILES    
            #===================================================================
            if os.path.exists(self.localDst):
                self.utils.removeFilesInDir(self.localDst)
            if not os.path.exists(self.localDst): 
                os.mkdir(self.localDst)
            #slicer.app.processEvents()
            #===================================================================
            # DICOMS
            #===================================================================
            if self.XNATLevel == 'subjects':
                #print "GETTING SUBJECT DICOMS"
                # Get 'resources' at the 'experiment' level.
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc)) 
                # Get 'experiments'.                                 
                experimentsList = self.XNATCommunicator.getFolderContents(self.xnatSrc)
                # Check for DICOMs (via 'resources') at the 'experiments' level.
                for expt in experimentsList:
                    self.checkForResourceDICOMS(self.xnatSrc + "/" + expt)
                # Get 'scans'
                for expt in experimentsList:
                    parentScanFolder = self.xnatSrc + "/" + expt + "/scans"
                    scanList = self.XNATCommunicator.getFolderContents(parentScanFolder)
                    for scan in scanList:
                        self.checkForResourceDICOMS(parentScanFolder + "/" + scan)
            #===================================================================
            # CHECK FOR DICOMS AT EXPERIMENTS LEVEL
            #===================================================================
            elif self.XNATLevel == 'experiments':
                #print "GETTING EXPERIMENT DICOMS"
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc)) 
                scansList = self.XNATCommunicator.getFolderContents(self.xnatSrc)
                for scan in scansList:
                    self.checkForResourceDICOMS(self.xnatSrc + "/" + scan)
            #===================================================================
            # CHECK FOR DICOMS AT THE SCANS LEVEL
            #===================================================================
            elif self.XNATLevel == 'scans':
                #print "GETTING SCAN DICOMS"
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc))     
            #===================================================================
            # CHECK FOR DICOMS AT THE RESOURCES LEVEL
            #===================================================================
            elif self.XNATLevel == 'resources':
                #print "GETTING RESOURCE DICOMS"
                self.checkForResourceDICOMS(self.xnatSrc.split("/resources")[0])          
            #===================================================================
            # DOWNLOAD ALL DICOMS
            #===================================================================
            import math   # for progress calculation    
            x = 0
            #print "IDENTIFIED DICOMS:"
            #print self.downloadables
            if len(self.downloadables)==0:
                self.XNATCommunicator.downloadFailed("Download Failed", "No scans in found to download!")
                return 
            
            if self.localDst.endswith("/"):
                self.localDst = self.localDst[:-2]                
            if not os.path.exists(self.localDst):
                    os.mkdir(self.localDst)  

            zipFolders = self.XNATCommunicator.getFiles(dict(zip(self.downloadables, 
                                           [(self.localDst + "/" + os.path.basename(dcm)) for dcm in self.downloadables])))
            #print (self.utils.lf() + str(zipFolders))   
            #===================================================================
            # INVENTORY DOWNLOADED 
            #===================================================================
            self.browser.updateStatus_Locked(["Inventorying downloaded files...", "", ""])    
            downloadedDICOMS = []
            for z in zipFolders:
                d = z.split(".")[0]
                if os.path.exists(d): 
                    self.utils.removeDirsAndFiles(d)
                self.utils.decompressFile(z, d)
                slicer.app.processEvents()
                for root, dirs, files in os.walk(d):
                    for relFileName in files:          
                        downloadedDICOMS.append(self.utils.adjustPathSlashes(os.path.join(root, relFileName)))
            m = slicer.util.mainWindow()
            #===================================================================
            # MAKE SURE DATABASE IS SET UP
            #===================================================================
            if not slicer.dicomDatabase:
                self.terminateLoad(['DICOM load', 'It doesn\'t look like your DICOM database directory is setup. Please set it up in the DICOM module and try your download again.'])
                m.moduleSelector().selectModule('DICOM')     
            else: 
                self.terminateLoad(['DICOM load', 'Indexing the downloaded DICOMS.  Please be patient.  When finished, a \'DICOM Details\' window will appear pertaining only to the images downloaded (Your previous DICOM database is still intact.)'])    
            #slicer.app.processEvents()
            #===================================================================
            # STORE EXISTING SLICER.DICOMDATABASE CONTENTS TO FILE
            #===================================================================
            self.browser.updateStatus_Locked(["Adding to Slicer's DICOM database...", "", ""])

            prevDICOMS = slicer.dicomDatabase.allFiles()
            #===================================================================
            # BACKUP THE OLD SLICER DATABASE FILE
            #===================================================================
            self.prevDBFile = slicer.dicomDatabase.databaseFilename
            self.newDBFile = os.path.join(os.path.dirname(self.utils.dicomDBBackupFN), os.path.basename(self.utils.dicomDBBackupFN))
            self.newDBFile = self.utils.adjustPathSlashes(self.newDBFile)
            if os.path.exists(self.newDBFile):
                self.utils.removeFile(self.newDBFile)            
            #print (self.utils.lf() + "COPYING %s to %s"%(self.prevDBFile, self.newDBFile))
            shutil.copy(self.prevDBFile, self.newDBFile)

            #===================================================================
            # CLEAR THE SLICER DATABASE FILE
            #===================================================================
            slicer.dicomDatabase.initializeDatabase()
            #===================================================================
            # ADD DICOM FILES TO SLICER DICOM DATABASE
            #===================================================================
            i = ctk.ctkDICOMIndexer()
            for dicomFile in downloadedDICOMS:          
                self.browser.updateStatus_Locked(["Adding '%s'"%(dicomFile), "to Slicer's DICOM database.", "Please wait..."])  
                #print("Adding '%s'"%(dicomFile), "to Slicer's DICOM database.", "Please wait...")  
                i.addFile(slicer.dicomDatabase, dicomFile)#, cachedPath)
            #===================================================================
            # OPEN A CUSTUM DICOM MODULE
            #===================================================================
            from DICOM import DICOMWidget
            self.DICOMWidget = DICOMWidget()         
            self.DICOMWidget.parent.hide()
            self.DICOMWidget.detailsPopup.window.setWindowTitle("XNAT DICOM Loader (from DICOMDetailsPopup)")          
            #===================================================================
            # CONNECT BUTTON SIGNALS FROM DICOM MODULE
            #===================================================================
            self.DICOMWidget.detailsPopup.loadButton.connect('clicked()', self.beginDICOMSession)
            #===================================================================
            # CONNECT ALL OTHER SIGNALS, TO CATCH IF THE POPUP WINDOW WAS CLOSED BY USER
            #===================================================================
            slicer.app.connect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)
            #===================================================================
            # OPEN DETAILS POPUP
            #===================================================================
            self.DICOMWidget.detailsPopup.open()
            #===================================================================
            # UPDATE BROWSER STATUS
            #===================================================================
            self.browser.XNATView.setEnabled(True)
            self.browser.XNATView.loadButton.setEnabled(True)
            return True
      
    def checkPopupOpen(self):
        if self.DICOMWidget and self.DICOMWidget.detailsPopup.window.isHidden():
            slicer.app.disconnect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)
            #print (self.utils.lf() + "POPUP CLOSED, RESTORING PREVIOUS DICOM DATABASE")
            self.browser.updateStatus_Locked(["", "Restoring original DICOM database.  Please wait.",""])
            self.restorePrevDICOMDB()
            #slicer.app.processEvents()
            del self.DICOMWidget
            self.browser.updateStatus(["", "Finished original DICOM database.",""])
    
    def beginDICOMSession(self):
        #print (self.utils.lf() + "BEGIN DICOM SESSION")
        self.browser.updateStatus(["", "DICOMS successfully loaded.",""])
        self.browser.generalProgressBar.setVisible(False)
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "dicom download"
        self.browser.XNATView.startNewSession(sessionArgs)
        #self.restorePrevDICOMDB()
        
    def restorePrevDICOMDB(self):
        #print (self.utils.lf() + "REINSERTING OLD DICOMS")
        #=======================================================================
        # DOES THE BACKUP FILE EXIST?
        #=======================================================================
        if os.path.exists(self.newDBFile):
            shutil.copy(self.newDBFile, self.prevDBFile)
