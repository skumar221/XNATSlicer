from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile


from XNATFileInfo import *

from XNATScenePackager import *
from XNATTimer import *


comment = """
  
  
# TODO : 
"""


    
class XNATSaveWorkflow(object):

    
    def __init__(self, browser, XNATCommunicator, sessionArgs):
        """ Parent class of any load workflow
        """
        self.browser = browser
        self.scenePackager = XNATScenePackager(self.browser)
        self.sessionArgs = sessionArgs


        
        
    def saveScene(self):    

        
        #----------------------
        # Package scene
        #
        #     NOTE: The scene packager refers to the .metadata file.     
        #---------------------- 
        package = self.scenePackager.bundleScene(self.sessionArgs)
        projectDir =         package['path']
        mrmlFile =           package['mrml']  

        
        #----------------------
        # Zip package
        #----------------------           

        packageFileName = projectDir + self.browser.utils.defaultPackageExtension
        if os.path.exists(packageFileName): 
            self.browser.utils.removeFile(packageFileName) 
        self.scenePackager.packageDir(packageFileName, projectDir)
        self.browser.utils.removeDirsAndFiles(projectDir)

        
        #----------------------
        # Upload package
        #----------------------      
        uploadStr = self.sessionArgs['saveDir'] + "/" + os.path.basename(packageFileName)    
        print ("UPLOADING HERE: " + uploadStr)
        from urlparse import urljoin

        self.browser.XNATCommunicator.upload(packageFileName, uploadStr)
        slicer.app.processEvents()
        if self.sessionArgs['sharable']:
            self.browser.updateStatus(["", "Finished updating '%s' in XNAT."%
                                       (os.path.basename(packageFileName)), ""])
        else: self.browser.updateStatus(["", "Finished writing '%s' to XNAT."%
                                         (os.path.basename(packageFileName)), ""])                        
        #----------------------
        # Update viewer
        #----------------------
        self.sessionArgs['sessionType'] = "scene upload"
        self.browser.XNATView.startNewSession(self.sessionArgs)

        self.browser.XNATView.setCurrItemToChild(item = None, 
                                                 childFileName = os.path.basename(packageFileName))
        


    def determineSaveLocation(self, itemType, selectedDir, saveLevel = None):
        """ Method goes through various steps to determine the optimal XNAT 
            location to save the current scene.
        """

        
        #----------------------
        # Set variables
        #----------------------
        print self.browser.utils.lf() + "DETERMINE SAVE DIR"
        currDir = os.path.dirname(selectedDir)
        saveDir = ""
        
              
        #----------------------
        # None handler
        #----------------------
        if not saveLevel:                                                                     
            # This is where another analysis step could exist to determine where
            # the scene could be saved.                                             
            saveLevel = self.browser.utils.defaultXNATSaveLevel               

            
        #----------------------
        # Check save level validity
        #----------------------
        else:
            findCount = False
            for key, value in self.browser.utils.xnatDepthDict.iteritems():
                if value == saveLevel: 
                    findCount = True
            if not findCount:
                print (self.browser.utils.lf() + 
                       "Couldn't find save level '%s'. Resorting to default: %s"%(saveLevel, self.browser.utils.defaultXNATSaveLevel))
                saveLevel = self.browser.utils.defaultXNATSaveLevel 

                
        #         Look at the sessionManager, reconcile save dir based on that
        #         and XNATSaveLevel
        if self.browser.XNATView.sessionManager.currSessionInfo:
            saveDir = self.browser.utils.getSlicerDirAtLevel(self.browser.XNATView.sessionManager.currSessionInfo['RemoteURI'], saveLevel)
        else:
            return None            
        print "SAVEDIR: " + saveDir 

        otherRequiredDirs = []
        baseDir = saveDir.split(self.browser.utils.slicerDirName)[0]
        for folderName in self.browser.utils.requiredSlicerFolders:
            otherRequiredDirs.append("%s%s/files/"%(baseDir, folderName))
            
        return {'saveDir': saveDir, 'others': otherRequiredDirs}


                    
