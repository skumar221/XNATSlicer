from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile
import urllib2

from XNATFileInfo import *
from XNATMRMLParser import *
from XNATUtils import *
from XNATScenePackager import *
from XNATTimer import *

#########################################################
comment = """
  
  
# TODO : 
"""
#
#########################################################

def getSaver(saverType, browser):
    pass
    print self.utils.lf() + "GET LOADER: " + loaderType
    if   loaderType == "scene": return SceneLoader(browser)
    elif loaderType == "dicom": return DICOMLoader(browser)
    elif loaderType == "file":  return FileLoader(browser)

class XNATSaveWorkflow(object):
    def __init__(self, browser, XNATCommunicator, sessionArgs):
        """ Parent class of any load workflow
        """
        self.browser = browser
        self.scenePackager = XNATScenePackager(self.browser)
        self.utils = XNATUtils()
        self.sessionArgs = sessionArgs
        self.XNATCommunicator = XNATCommunicator
        
    def saveScene(self):       
        #=======================================================================
        #     PACKAGE SCENE
        #
        #     NOTE: The scene packager refers to the .metadata file.     
        #======================================================================= 
        package = self.scenePackager.bundleScene(self.sessionArgs)
        projectDir =         package['path']
        mrmlFile =           package['mrml']  
        #=======================================================================
        #     ZIP PACKAGE
        #=======================================================================           
        self.browser.updateStatus(["Compressing package. Please wait...", "", ""]) 
        packageFileName = projectDir + self.utils.defaultPackageExtension
        if os.path.exists(packageFileName): 
            self.utils.removeFile(packageFileName) 
        self.scenePackager.packageDir(packageFileName, projectDir)
        
        self.browser.updateStatus(["Deleting temporary package.", "", ""])    
        self.utils.removeDirsAndFiles(projectDir)
        #=======================================================================
        #     UPLOAD PACKAGE
        #=======================================================================          
        self.browser.updateStatus(["Sending '%s' to XNAT. Please wait..."%
                                   (os.path.basename(packageFileName)), "", ""])
        #print ("UPLOADING HERE: " + self.sessionArgs['saveDir'] + "/" + os.path.basename(packageFileName))
        self.XNATCommunicator.upload(packageFileName, self.sessionArgs['saveDir'] + "/" + os.path.basename(packageFileName))
        slicer.app.processEvents()
        if self.sessionArgs['sharable']:
            self.browser.updateStatus(["", "Finished updating '%s' in XNAT."%
                                       (os.path.basename(packageFileName)), ""])
        else: self.browser.updateStatus(["", "Finished writing '%s' to XNAT."%
                                         (os.path.basename(packageFileName)), ""])                        
        #=======================================================================
        #     UPDATE VIEWER
        #=======================================================================
        self.sessionArgs['sessionType'] = "scene upload"
        self.browser.XNATView.startNewSession(self.sessionArgs)
        self.browser.XNATView.loadButton.setEnabled(True)
        self.browser.XNATView.deleteButton.setEnabled(True) 
        self.browser.XNATView.setCurrItemToChild(item = None, 
                                                 childFileName = os.path.basename(packageFileName))
        


    def determineSaveLocation(self, itemType, selectedDir, saveLevel = None):
        """ Method goes through various steps to determine the optimal XNAT 
            location to save the current scene.
        """
        #=======================================================================
        #     SET VARIABLES
        #=======================================================================
        print self.utils.lf() + "DETERMINE SAVE DIR"
        currDir = os.path.dirname(selectedDir)
        saveDir = ""
        
              
        #=======================================================================
        #     NONE HANDLER
        #=======================================================================
        if not saveLevel:                                                                     
            # This is where another analysis step could exist to determine where
            # the scene could be saved.                                             
            saveLevel = self.utils.defaultXNATSaveLevel               
        
        #=======================================================================
        #     CHECK SAVE LEVEL VALIDITY
        #=======================================================================
        else:
            findCount = False
            for key, value in self.utils.xnatDepthDict.iteritems():
                if value == saveLevel: 
                    findCount = True
            if not findCount:
                print (self.utils.lf() + 
                       "Couldn't find save level '%s'. Resorting to default: %s"%(saveLevel, self.utils.defaultXNATSaveLevel))
                saveLevel = self.utils.defaultXNATSaveLevel 
        #         Look at the sessionManager, reconcile save dir based on that
        #         and XNATSaveLevel
        if self.browser.XNATView.sessionManager.currSessionInfo:
            saveDir = self.utils.getSlicerDirAtLevel(self.browser.XNATView.sessionManager.currSessionInfo['RemoteURI'], saveLevel)
        else:
            return None            
        print "SAVEDIR: " + saveDir 

        otherRequiredDirs = []
        baseDir = saveDir.split(self.utils.slicerDirName)[0]
        for folderName in self.utils.requiredSlicerFolders:
            otherRequiredDirs.append("%s%s/files/"%(baseDir, folderName))
            
        return {'saveDir': saveDir, 'others': otherRequiredDirs}


                    