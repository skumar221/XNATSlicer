from __main__ import vtk, ctk, qt, slicer
# PYTHON INCLUDES
import os
import sys
import shutil
import zipfile
import urllib2
from datetime import datetime
# MODULE INCLUDES
from XNATFileInfo import *
from XNATUtils import *
from XNATScenePackager import *
from XNATTimer import *
from XNATSessionManager import *
from XNATMRMLParser import *

def getLoader(loaderType, browser):
    if   loaderType == "scene": return SceneLoader(browser)
    elif loaderType == "dicom": return DICOMLoader(browser)
    elif loaderType == "file":  return FileLoader(browser)
    elif loaderType == "mass_dicom":  return DICOMLoader(browser)

#=================================================================
# XNATLoadWorkflow is a parent class to various loader types
# (Slicer files, DICOM folders, individual files, etc.).  Loader types
# are determined by the treeView item being clicked. 
#=================================================================

class XNATLoadWorkflow(object):
    def __init__(self, browser):
        """ Parent class of any load workflow
        """
        self.utils = XNATUtils()
        self.browser = browser       
        self.stopwatch = XNATTimer(self.utils)
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None

    def load(self, args):
        self.XNATCommunicator =  args["XNATCommunicator"]
        self.xnatSrc = args["xnatSrc"]
        self.localDst = args["localDst"]
        
    def loadFinish(self):
        pass

    def terminateLoad(self, warnStr):
        qt.QMessageBox.warning( None, warnStr[0], warnStr[1])
        self.browser.XNATView.setEnabled(True)

    def getLoadables_byDir(self, rootDir):
        """Returns the loadable filenames (determined by filetype) in a dir"""
        allImages = []
        mrmls = []
        dicoms = []   
        for folder, subs, files in os.walk(rootDir):
            for file in files:
                extension =  os.path.splitext(file)[1].lower() 
                if self.utils.isDICOM(ext = extension):
                    dicoms.append(os.path.join(folder,file))                   
                if self.utils.isMRML(ext = extension): 
                    mrmls.append(os.path.join(folder,file))  
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms}
    
    def getLoadables_byList(self, fileList):
        """Returns the loadable filenames (determined by filetype) in filename list"""
        allImages = []
        mrmls = []
        dicoms = []
        others = []    
        for file in fileList:
            file = str(file)
            extension =  os.path.splitext(file)[1].lower() 
            if extension or (extension != ""):
                if self.utils.isDICOM(ext = extension):
                    dicoms.append(file)                   
                if self.utils.isMRML(ext = extension): 
                    mrmls.append(file)
                else:
                    others.append(file)
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms, 'OTHERS': others, 'ALLNONMRML': allImages + dicoms + others}
   
class SceneLoader(XNATLoadWorkflow):
    
    def load(self, args):
        super(SceneLoader, self).load(args)
        #=======================================================================
        # STEP 1: Get scene package
        #=======================================================================
        self.XNATCommunicator.getFile({self.xnatSrc : self.localDst})
        self.browser.updateStatus(["", "Decompressing '" + os.path.basename(self.xnatSrc) + "'", ""])
        #=======================================================================
        # STEP 2: Analyze package to determine scene type
        #=======================================================================
        fileInfo = XNATFileInfo(remoteURI = self.xnatSrc, localURI = self.localDst)
        packageInfo = self.analyzePackage(fileInfo) 
        newMRMLFile = self.prepSelfContainedScene(packageInfo)
        #=======================================================================
        # STEP 3: Load is good if mrml file is returned
        #=======================================================================
        if newMRMLFile: 
            return self.loadFinish(newMRMLFile)    
        return False
          
    def decompressPackagedScene(self, packageFileName, destDir):
        fileURLs = []
        #=======================================================================
        # STEP 1: Zip handling
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
        # STEP 2: *.mrb handling
        #=======================================================================
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
        
    def analyzePackage(self, currXNATFileInfo):
        """ Checks downloaded scene file for its contents.  Delegates how to handle it accordingly.
        """
        #=======================================================================
        # STEP 1: Decompress scene, get files
        #=======================================================================
        extractDir = self.utils.tempPath
        tempUnpackDir = os.path.join(extractDir, currXNATFileInfo.basenameNoExtension)
        fileList = self.decompressPackagedScene(currXNATFileInfo.localURI, tempUnpackDir)
        #=======================================================================
        # STEP 2: Return dictionary of useful params
        #=======================================================================
        return {'basename': currXNATFileInfo.basename, 
                'unpackDir': tempUnpackDir, 
                'nameOnly': currXNATFileInfo.basenameNoExtension, 
                'remoteURI': currXNATFileInfo.remoteURI, 
                'localURI': currXNATFileInfo.localURI}
            
    def prepSelfContainedScene(self, packageInfo):
        """ Loads the scene package if the scene was created outside of the module's packaging workflow (XNATScenePacakger)."""
        #=======================================================================
        # STEP 1: Cache the scene     
        #=======================================================================
        self.storeSceneLocally(packageInfo, False)    
        #=======================================================================
        # STEP 2: Deconstruct package info
        #=======================================================================
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']
        #=======================================================================
        # STEP 3: Get mrmls and nodes within package
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
        # STEP 4: define relevant paths
        #=======================================================================
        newRemoteDir = self.utils.getParentPath(remoteURI, "resources")
        filePathsToChange = {}
        #=======================================================================
        # STEP 5: Cache images and sharables
        #=======================================================================
        for pFile in parseableFiles:
            pFileBase = os.path.basename(pFile)
            if os.path.basename(os.path.dirname(pFile)) == "Data":
                # special case for url encoding
                filePathsToChange[os.path.basename(urllib2.quote(pFileBase))] = "./Data/" + urllib2.quote(pFileBase)
        #=======================================================================
        # STEP 6: Parse mrml, updating paths to relative
        #=======================================================================
        newMRMLFile = self.utils.appendFile(mrmlFiles[0], "-LOCALIZED")       
        #
        # NOTE: Parsing of the MRML is needed because node filePaths are absolute, not relative.
        # TODO: Submit a change request for absolute path values to Slicer
        #
        mrmlParser = XNATMRMLParser(self.browser)
        mrmlParser.changeValues(mrmlFiles[0], newMRMLFile,  {},  None, True)
        return newMRMLFile


    def storeSceneLocally(self, packageInfo, cacheOriginalPackage = True):
        """ Creates a project cache (different from an image cache) based on
        """  
        #=======================================================================
        # STEP 1: Init params         
        #=======================================================================
        scenePackageBasename = packageInfo['basename']
        extractDir = packageInfo['unpackDir']
        sceneName = packageInfo['nameOnly']
        remoteURI = packageInfo['remoteURI']
        localURI = packageInfo['localURI']
        #=======================================================================
        # STEP 2: Establish caching directories
        #=======================================================================
        sceneDir = os.path.join(self.utils.projectPath, sceneName)
        if not os.path.exists(sceneDir): os.mkdir(sceneDir)       
        self.cachePathDict = {'localFiles': os.path.join(sceneDir, 'localFiles'),
                              'cacheManager': os.path.join(sceneDir, 'cacheManagement'),
                              'originalPackage': os.path.join(sceneDir, 'originalPackage')}
        #=======================================================================
        # STEP 3: Create relevant paths locally
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
        # STEP 4: Move unpacked contents to new directory
        #=======================================================================
        self.utils.moveDirContents(extractDir, self.cachePathDict['localFiles'])
        #=======================================================================
        # STEP 5: Move package as well to cache, if desired 
        #=======================================================================
        if cacheOriginalPackage:
            qFile = qt.QFile(localURI)
            qFile.copy(os.path.join(self.cachePathDict['originalPackage'], scenePackageBasename))
            qFile.close()
        #=======================================================================
        # STEP 6: Delete package
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
        # STEP 1: Call loadscene
        #=======================================================================
        self.browser.updateStatus(["", "Loading '" + os.path.basename(self.xnatSrc) + "'", ""])
        slicer.util.loadScene(fileName) 
        
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "scene download"
        self.browser.XNATView.startNewSession(sessionArgs)
        
        self.browser.updateStatus_Locked(["", "Scene '%s' loaded."%(os.path.basename(fileName.rsplit(".")[0])), ""])  
        self.browser.generalProgressBar.setVisible(False)
        #=======================================================================
        # STEP 2: Enable view in browser
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
        # STEP 1: Call parent
        #=======================================================================
        super(FileLoader, self).load(args)
        #=======================================================================
        # STEP 2: Get the file
        #=======================================================================
        self.XNATCommunicator.getFile({self.xnatSrc: self.localDst})
        #slicer.app.processEvents()
        #=======================================================================
        # STEP 3: Open file
        #=======================================================================
        a = slicer.app.coreIOManager()
        t = a.fileType(self.localDst)
        nodeOpener = slicer.util.loadNodeFromFile(self.localDst, t)
        #=======================================================================
        # STEP 4: Update status bar
        #=======================================================================
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
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
        # STEP 1: Call parent
        #=======================================================================
        super(DICOMLoader, self).load(args)
        #=======================================================================
        # STEP 2: Define globals
        #=======================================================================
        self.XNATLevel = os.path.basename(os.path.dirname(os.path.dirname(self.xnatSrc)))
        self.folderName = os.path.basename(os.path.dirname(self.xnatSrc))
        self.downloadables = []
        self.DICOMWidget = None
        self.newDBFile = None
        self.prevDBFile = None
        #=======================================================================
        # STEP 3: Is the user downloading multiple folders?
        #=======================================================================
        if self.xnatSrc.endswith("files"):
            # if not, proceed with load
            self.proceedWithLoad('yes')
        else:
            # if so, then setup+show dialog asking user to proceed
            self.areYouSureDialog = qt.QMessageBox()
            self.areYouSureDialog.setIcon(4)
            #print "XNATSRC: " + self.xnatSrc
            self.areYouSureDialog.setText("You are about to load all of " +   
                                          self.folderName + "'s "+  
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
                    self.downloadables.append(filePath + filename)
                else:
                    print (self.utils.lf() + " NOT A DICOM: '%s'"%(filePath + filename))
            except Exception, e:
                print self.utils.lf() + "LIKELY NOT A USEABLE FILE: '%s' "%(filePath + filename) + str(e)
        
    def proceedWithLoad(self, button): 
        if ((str(button) == 'yes') or 
            (('yes' in button.text.lower()))):
            experimentsList = []
            scansList = []   
            self.browser.updateStatus(["", "Downloading DICOMS in '%s'."%(os.path.dirname(self.xnatSrc)),"Please wait."])          
            #===================================================================
            # STEP 1: Remove existing files    
            #===================================================================
            if os.path.exists(self.localDst):
                self.utils.removeFilesInDir(self.localDst)
            if not os.path.exists(self.localDst): 
                os.mkdir(self.localDst)
            #===================================================================
            # STEP 2: DICOMS
            #===================================================================
            if self.XNATLevel == 'subjects':
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
            # STEP 3: Check for dicoms at experiments level
            #===================================================================
            elif self.XNATLevel == 'experiments':
                #print "GETTING EXPERIMENT DICOMS"
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc)) 
                scansList = self.XNATCommunicator.getFolderContents(self.xnatSrc)
                for scan in scansList:
                    self.checkForResourceDICOMS(self.xnatSrc + "/" + scan)
            #===================================================================
            # STEP 4: Check for dicoms at the scans level
            #===================================================================
            elif self.XNATLevel == 'scans':
                #print "GETTING SCAN DICOMS"
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc))     
            #===================================================================
            # STEP 5: Check for dicoms at the resources level
            #===================================================================
            elif self.XNATLevel == 'resources':
                #print "GETTING RESOURCE DICOMS"
                self.checkForResourceDICOMS(self.xnatSrc.split("/resources")[0])          
            #===================================================================
            # STEP 6: Download all dicoms
            #===================================================================
            import math   # for progress calculation    
            x = 0
            if len(self.downloadables)==0:
                self.XNATCommunicator.downloadFailed("Download Failed", "No scans in found to download!")
                return 
            
            if self.localDst.endswith("/"):
                self.localDst = self.localDst[:-2]                
            if not os.path.exists(self.localDst):
                    os.mkdir(self.localDst)  

            zipFolders = self.XNATCommunicator.getFiles(dict(zip(self.downloadables, 
                                           [(self.localDst + "/" + os.path.basename(dcm)) for dcm in self.downloadables])))
            #===================================================================
            # STEP 7: Inventory downloaded 
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
            # STEP 8: Make sure database is set up
            #===================================================================
            if not slicer.dicomDatabase:
                self.terminateLoad(['DICOM load', 'It doesn\'t look like your DICOM database directory is setup. Please set it up in the DICOM module and try your download again.'])
                m.moduleSelector().selectModule('DICOM')     
            else: 
                self.terminateLoad(['DICOM load', 'Indexing the downloaded DICOMS.  Please be patient.  When finished, a \'DICOM Details\' window will appear pertaining only to the images downloaded (your previous DICOM database is still intact.)'])    
            #slicer.app.processEvents()
            #===================================================================
            # STEP 9: Store existing slicer.dicomdatabase contents to file
            #===================================================================
            self.browser.updateStatus_Locked(["Adding to Slicer's DICOM database...", "", ""])

            prevDICOMS = slicer.dicomDatabase.allFiles()
            #===================================================================
            # STEP 10: Backup the old slicer database file
            #===================================================================
            self.prevDBFile = slicer.dicomDatabase.databaseFilename
            self.newDBFile = os.path.join(os.path.dirname(self.utils.dicomDBBackupFN), os.path.basename(self.utils.dicomDBBackupFN))
            self.newDBFile = self.utils.adjustPathSlashes(self.newDBFile)
            if os.path.exists(self.newDBFile):
                self.utils.removeFile(self.newDBFile)            
            #print (self.utils.lf() + "COPYING %s to %s"%(self.prevDBFile, self.newDBFile))
            shutil.copy(self.prevDBFile, self.newDBFile)

            #===================================================================
            # STEP 11: Clear the slicer database file
            #===================================================================
            slicer.dicomDatabase.initializeDatabase()
            #===================================================================
            # STEP 12: Add dicom files to slicer dicom database
            #===================================================================
            i = ctk.ctkDICOMIndexer()
            for dicomFile in downloadedDICOMS:          
                self.browser.updateStatus_Locked(["Adding '%s'"%(dicomFile), "to Slicer's DICOM database.", "Please wait..."])  
                #print("Adding '%s'"%(dicomFile), "to Slicer's DICOM database.", "Please wait...")  
                i.addFile(slicer.dicomDatabase, dicomFile)#, cachedPath)
            #===================================================================
            # STEP 13: Open a custum dicom module
            #===================================================================
            from DICOM import DICOMWidget
            self.DICOMWidget = DICOMWidget()         
            self.DICOMWidget.parent.hide()
            self.DICOMWidget.detailsPopup.window.setWindowTitle("XNAT DICOM Loader (from DICOMDetailsPopup)")          
            #===================================================================
            # STEP 14: Connect button signals from dicom module
            #===================================================================
            self.DICOMWidget.detailsPopup.loadButton.connect('clicked()', self.beginDICOMSession)
            #===================================================================
            # STEP 15: Connect all other signals, to catch if the popup window was closed by user
            #===================================================================
            slicer.app.connect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)
            #===================================================================
            # STEP 16: Open details popup
            #===================================================================
            self.DICOMWidget.detailsPopup.open()
            #===================================================================
            # STEP 17: Update browser status
            #===================================================================
            self.browser.XNATView.setEnabled(True)
            self.browser.XNATView.loadButton.setEnabled(True)
            return True
      
    def checkPopupOpen(self):
        if self.DICOMWidget and self.DICOMWidget.detailsPopup.window.isHidden():
            slicer.app.disconnect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)
            self.browser.updateStatus_Locked(["", "Restoring original DICOM database.  Please wait.",""])
            self.restorePrevDICOMDB()
            del self.DICOMWidget
            self.browser.updateStatus(["", "Finished original DICOM database.",""])
    
    def beginDICOMSession(self):
        self.browser.updateStatus(["", "DICOMS successfully loaded.",""])
        self.browser.generalProgressBar.setVisible(False)
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "dicom download"
        self.browser.XNATView.startNewSession(sessionArgs)

        
    def restorePrevDICOMDB(self):
        if os.path.exists(self.newDBFile):
            shutil.copy(self.newDBFile, self.prevDBFile)
