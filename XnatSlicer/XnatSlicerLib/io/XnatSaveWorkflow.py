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

    def __init__(self, browser):
        """ Init function.
        """
        
        self.browser = browser
        self.scenePackager = XnatScenePackager(self.browser)


        
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
        if self.browser.XnatView.sessionManager.sessionArgs:
            self.browser.XnatView.setEnabled(False)
            FileSaveDialog(self.browser, self)
            


        #------------------------
        # If scene is local, or of non-XNAT origin
        #------------------------
        elif (not self.browser.XnatView.sessionManager.sessionArgs):
            #
            # Construct new sessionArgs
            #
            fullPath = self.browser.XnatView.getXnatDir(self.browser.XnatView.getParents(self.browser.XnatView.viewWidget.currentItem()))
            remoteURI = self.browser.settings.getAddress(self.browser.XnatLoginMenu.hostDropdown.currentText) + fullPath
            sessionArgs = XnatSessionArgs(browser = self.browser, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            sessionArgs.printAll()
            return




        
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
        self.browser.XnatView.setEnabled(False)



        #------------------------
        # Package scene
        #------------------------
        package = self.scenePackager.bundleScene(self.browser.XnatView.sessionManager.sessionArgs)
        projectDir =         package['path']
        mrmlFile =           package['mrml']  
        


        #------------------------
        # Zip package     
        #------------------------ 
        packageFileName = projectDir + self.browser.utils.defaultPackageExtension
        if os.path.exists(packageFileName): 
            self.browser.utils.removeFile(packageFileName) 
        self.scenePackager.packageDir(packageFileName, projectDir)
        self.browser.utils.removeDirsAndFiles(projectDir)



        #------------------------
        # Upload package  
        #------------------------   
        uploadStr = self.browser.XnatView.sessionManager.sessionArgs['saveDir'] + "/" + os.path.basename(packageFileName)    
        self.browser.XnatCommunicator.upload(packageFileName, uploadStr)
        slicer.app.processEvents()
  


        #------------------------
        # Update viewer
        #------------------------
        baseName = os.path.basename(packageFileName)
        self.browser.XnatView.sessionManager.sessionArgs['sessionType'] = "scene upload"
        self.browser.XnatView.startNewSession(self.browser.XnatView.sessionManager.sessionArgs)
        self.browser.XnatView.setCurrItemToChild(item = None, childFileName = baseName)
        self.browser.XnatView.setEnabled(True)
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
        saveDir = ""
        
        #
        # NOTE: 'saveLevel' is the same as an XnatLevel.  (i.e. 
        # 'projects', 'subjects', 'experiments', 'scans', 'resources')
        #
        
        #------------------------
        # If no 'saveLevel' specified, go to default level.
        #------------------------
        if not saveLevel:                                                                                                                 
            saveLevel = self.browser.utils.defaultXnatSaveLevel               


            
        #------------------------    
        # If 'saveLevel' is specificed, check save level validity.
        #------------------------
        else:
            findCount = False
            for key, value in self.browser.utils.xnatDepthDict.iteritems():
                if value == saveLevel: 
                    findCount = True
            if not findCount:
                print (self.browser.utils.lf() + 
                       "Couldn't find save level '%s'. Resorting to default: %s"%(saveLevel, self.browser.utils.defaultXnatSaveLevel))
                saveLevel = self.browser.utils.defaultXnatSaveLevel 


                
        #------------------------
        # Look at the sessionManager, reconcile save dir based on that
        # and XnatSaveLevel derived above.
        #------------------------
        if self.browser.XnatView.sessionManager.currSessionInfo:
            saveDir = self.browser.utils.constructSlicerSaveUri(currUri = self.browser.XnatView.sessionManager.currSessionInfo['RemoteURI'], xnatLevel = saveLevel)
        else:
            return None            


        
        #------------------------
        # DEPRECATED: for other saving schemes like share files
        #------------------------
        otherRequiredDirs = []
        baseDir = saveDir.split(self.browser.utils.slicerFolderName)[0]
        for folderName in self.browser.utils.requiredSlicerFolders:
            otherRequiredDirs.append("%s%s/files/"%(baseDir, folderName))


            
        return {'saveDir': saveDir, 'others': otherRequiredDirs}


                    
