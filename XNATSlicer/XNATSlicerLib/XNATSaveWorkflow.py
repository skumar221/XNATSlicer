from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile

from XNATFileInfo import *
from XNATScenePackager import *
from XNATTimer import *
from XNATSaveDialog import *



comment = """
XNATSaveWorkflow manages all of the processes needed to upload
a file to XNAT.  Packaging scenes and uploaded are conducted here.

"""





    
class XNATSaveWorkflow(object):
    """ Descriptor above.
    """



    
    def __init__(self, browser):
        """ Parent class of any load workflow
        """
        
        self.browser = browser
        self.scenePackager = XNATScenePackager(self.browser)


        # Set wait window
        self.waitWindow = qt.QMessageBox(0, "Uploading", "Please wait while file uploads...")



        
    def beginWorkflow(self):
        """ Descriptor
        """

        # If Scene originated from XNAT (i.e. the session manager is active)...
        if self.browser.XNATView.sessionManager.sessionArgs:
            self.browser.XNATView.setEnabled(False)
            FileSaveDialog(self.browser, self)
            
         
        # If scene is local, or of non-XNAT origin
        elif (not self.browser.XNATView.sessionManager.sessionArgs):

            
            # Construct new sessionArgs
            fullPath = self.browser.XNATView.getXNATDir(self.browser.XNATView.getParents(self.browser.XNATView.viewWidget.currentItem()))
            remoteURI = self.browser.settings.getAddress(self.browser.XNATLoginMenu.hostDropdown.currentText) + fullPath
            sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            sessionArgs.printAll()

            
            # Call unlinked dialog
            SaveUnlinkedDialog(self.browser, self, fullPath)



        
    def saveScene(self):    
        """  Main command scene
        """

        # Show wait window
        self.waitWindow.show()

        
        # Disable the view widget
        self.browser.XNATView.setEnabled(False)


        # Package scene
        package = self.scenePackager.bundleScene(self.browser.XNATView.sessionManager.sessionArgs)
        projectDir =         package['path']
        mrmlFile =           package['mrml']  
        

        # Zip package      
        packageFileName = projectDir + self.browser.utils.defaultPackageExtension
        if os.path.exists(packageFileName): 
            self.browser.utils.removeFile(packageFileName) 
        self.scenePackager.packageDir(packageFileName, projectDir)
        self.browser.utils.removeDirsAndFiles(projectDir)

        
        # Upload package     
        uploadStr = self.browser.XNATView.sessionManager.sessionArgs['saveDir'] + "/" + os.path.basename(packageFileName)    
        self.browser.XNATCommunicator.upload(packageFileName, uploadStr)
        slicer.app.processEvents()
  
            
        # Update viewer
        baseName = os.path.basename(packageFileName)
        self.browser.XNATView.sessionManager.sessionArgs['sessionType'] = "scene upload"
        self.browser.XNATView.startNewSession(self.browser.XNATView.sessionManager.sessionArgs)
        self.browser.XNATView.setCurrItemToChild(item = None, childFileName = baseName)
        self.browser.XNATView.setEnabled(True)
        print "\nUpload of '%s' complete."%(baseName)


        # Hide wait window
        self.waitWindow.hide()


        
        
    def determineSaveLocation(self, itemType, selectedDir, saveLevel = None):
        """ Method goes through various steps to determine the optimal XNAT 
            location to save the current scene.
        """

        
        # Set variables
        print self.browser.utils.lf() + "DETERMINE SAVE DIR"
        currDir = os.path.dirname(selectedDir)
        saveDir = ""
        
              
        # None handler
        if not saveLevel:                                                                     
            # This is where another analysis step could exist to determine where
            # the scene could be saved.                                             
            saveLevel = self.browser.utils.defaultXNATSaveLevel               

            
        # Check save level validity
        else:
            findCount = False
            for key, value in self.browser.utils.xnatDepthDict.iteritems():
                if value == saveLevel: 
                    findCount = True
            if not findCount:
                print (self.browser.utils.lf() + 
                       "Couldn't find save level '%s'. Resorting to default: %s"%(saveLevel, self.browser.utils.defaultXNATSaveLevel))
                saveLevel = self.browser.utils.defaultXNATSaveLevel 

                
        # Look at the sessionManager, reconcile save dir based on that
        #  and XNATSaveLevel
        if self.browser.XNATView.sessionManager.currSessionInfo:
            saveDir = self.browser.utils.getSlicerDirAtLevel(self.browser.XNATView.sessionManager.currSessionInfo['RemoteURI'], saveLevel)
        else:
            return None            


        # DEPRECATED: for other saving schemes like share files
        otherRequiredDirs = []
        baseDir = saveDir.split(self.browser.utils.slicerDirName)[0]
        for folderName in self.browser.utils.requiredSlicerFolders:
            otherRequiredDirs.append("%s%s/files/"%(baseDir, folderName))


            
        return {'saveDir': saveDir, 'others': otherRequiredDirs}


                    
