from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile

from XnatFileInfo import *
from XnatScenePackager import *
from XnatTimer import *
from XnatSaveDialog import *



comment = """
XnatSaveWorkflow manages all of the processes needed to upload
a file to an XNAT.  Packaging scenes and uploaded are conducted here.

TODO:
"""

    
class XnatSaveWorkflow(object):
    """ Descriptor above.
    """

    def __init__(self, MODULE):
        """ Init function.
        """
        
        self.MODULE = MODULE
        self.scenePackager = XnatScenePackager(self.MODULE)


        
        #------------------------
        # Set wait window
        #------------------------
        self.waitWindow = qt.QMessageBox(1, "Uploading", "Please wait while file uploads...")
        self.waitWindow.setWindowModality(2)


        
        #------------------------
        # This removes the OK button.
        #------------------------
        self.waitWindow.setStandardButtons(0)



        
    def beginWorkflow(self):
        """ As stated.  Conducts some prelimiary 
            steps (see below) before uploading the scene to the 
            XNAT host.
        """

        #------------------------
        # If Scene originated from XNAT (i.e. the session manager is active)...
        #------------------------
        if self.MODULE.XnatView.sessionManager.sessionArgs:
            self.MODULE.XnatView.setEnabled(False)
            FileSaveDialog(self.MODULE, self)
            


        #------------------------
        # If scene is local, or of non-XNAT origin
        #------------------------
        elif (not self.MODULE.XnatView.sessionManager.sessionArgs):
            #
            # Construct new sessionArgs
            #
            fullPath = self.MODULE.XnatView.constructXnatUri(self.MODULE.XnatView.getParents(self.MODULE.XnatView.currentItem()))
            remoteURI = self.MODULE.XnatSettingsFile.getAddress(self.MODULE.XnatLoginMenu.hostDropdown.currentText) + fullPath
            sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            self.MODULE.XnatView.sessionManager.startNewSession(sessionArgs)
            self.MODULE.XnatView.setEnabled(False)
            FileSaveDialog(self.MODULE, self)




        
    def saveScene(self):    
        """  Main function for saving/uploading a file
             to an XNAT host.
        """

        #------------------------
        # Show wait window
        #------------------------
        self.waitWindow.show()



        #------------------------
        # Disable the view widget
        #------------------------
        self.MODULE.XnatView.setEnabled(False)



        #------------------------
        # Package scene
        #------------------------
        package = self.scenePackager.bundleScene(self.MODULE.XnatView.sessionManager.sessionArgs)
        projectDir =         package['path']
        mrmlFile =           package['mrml']  
        


        #------------------------
        # Zip package     
        #------------------------ 
        packageFileName = projectDir + self.MODULE.utils.defaultPackageExtension
        if os.path.exists(packageFileName): 
            self.MODULE.utils.removeFile(packageFileName) 
        self.scenePackager.packageDir(packageFileName, projectDir)
        self.MODULE.utils.removeDirsAndFiles(projectDir)



        #------------------------
        # Upload package  
        #------------------------   
        uploadStr = self.MODULE.XnatView.sessionManager.sessionArgs['saveUri'] + "/" + os.path.basename(packageFileName)    
        self.MODULE.XnatIo.upload(packageFileName, uploadStr)
        slicer.app.processEvents()
  


        #------------------------
        # Update viewer
        #------------------------
        baseName = os.path.basename(packageFileName)
        self.MODULE.XnatView.sessionManager.sessionArgs['sessionType'] = "scene upload"
        self.MODULE.XnatView.startNewSession(self.MODULE.XnatView.sessionManager.sessionArgs)
        self.MODULE.XnatView.setCurrItemToChild(item = None, childFileName = baseName)
        self.MODULE.XnatView.setEnabled(True)
        print "\nUpload of '%s' complete."%(baseName)



        #------------------------
        # Hide wait window
        #------------------------
        self.waitWindow.hide()


        
        
    def determineSaveLocation(self, itemType, selectedDir, saveLevel = None):
        """ Method goes through various steps to determine the optimal XNAT
            location to save the current scene.
        """

        #------------------------
        # Set variables
        #------------------------
        currDir = os.path.dirname(selectedDir)
        saveUri = ""
        
        #
        # NOTE: 'saveLevel' is the same as an XnatLevel.  (i.e. 
        # 'projects', 'subjects', 'experiments', 'scans', 'resources')
        #
        
        #------------------------
        # If no 'saveLevel' specified, go to default level.
        #------------------------
        if not saveLevel:                                                                                                                 
            saveLevel = self.MODULE.utils.defaultXnatSaveLevel               


            
        #------------------------    
        # If 'saveLevel' is specificed, check save level validity.
        #------------------------
        else:
            findCount = False
            for key, value in self.MODULE.utils.xnatDepthDict.iteritems():
                if value == saveLevel: 
                    findCount = True
            if not findCount:
                print (self.MODULE.utils.lf() + 
                       "Couldn't find save level '%s'. Resorting to default: %s"%(saveLevel, self.MODULE.utils.defaultXnatSaveLevel))
                saveLevel = self.MODULE.utils.defaultXnatSaveLevel 


                
        #------------------------
        # Look at the sessionManager, reconcile save dir based on that
        # and XnatSaveLevel derived above.
        #------------------------
        if self.MODULE.XnatView.sessionManager.currSessionInfo:
            saveUri = self.MODULE.utils.constructSlicerSaveUri(currUri = self.MODULE.XnatView.sessionManager.currSessionInfo['RemoteURI'], xnatLevel = saveLevel)
        else:
            return None            


        
        #------------------------
        # DEPRECATED: for other saving schemes like share files
        #------------------------
        otherRequiredDirs = []
        baseDir = saveUri.split(self.MODULE.utils.slicerFolderName)[0]
        for folderName in self.MODULE.utils.requiredSlicerFolders:
            otherRequiredDirs.append("%s%s/files/"%(baseDir, folderName))


            
        return {'saveUri': saveUri, 'others': otherRequiredDirs}


                    
