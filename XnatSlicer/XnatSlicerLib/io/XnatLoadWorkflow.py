from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile
import urllib2
from datetime import datetime

from XnatFileInfo import *
from XnatUtils import *
from XnatScenePackager import *
from XnatTimer import *
from XnatSessionManager import *
from XnatMrmlParser import *
from XnatPopup import *

    

comment = """
XnatLoadWorkflow is a parent class to various loader classes:
XnatSceneLoadWorkflow, XnatDicomLoadWorkflow, XnatFileLoadWorkflow.  Loader types
are determined by the treeViewItem being clicked in the 
XnatLoadWorkflow function 'beginWorkflow'.  Functions of XnatLoadWorkflow
are generic in nature and pertain to string construction for querying
and downloading files.

TODO:
"""



class XnatLoadWorkflow(object):
    """ Parent Load workflow class to: XnatDicomLoadWorkflow, 
        XnatSceneLoadWorkflow, and XnatFileLoadWorkflow.
    """

    
    def __init__(self, MODULE):
        """ Parent init.
        """
        self.MODULE = MODULE       
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None


        
    def initLoad(self):
        """ As stated.
        """


        
    def load(self, args):
        """ Sets needed variables.
        """
        self.xnatSrc = args["xnatSrc"]
        self.localDst = args["localDst"]



        
    def setup(self):
        """ As stated.
        """
        pass



     
    def loadFinish(self):
        """ As stated.
        """
        pass



    
    def terminateLoad(self, warnStr):
        """ Notifies the user that they will terminate the load.
            Reenables the viewer UI.
        """
        qt.QMessageBox.warning( None, warnStr[0], warnStr[1])
        self.MODULE.XnatView.setEnabled(True)



        
    def getLoadables_byDir(self, rootDir):
        """Returns the loadable filenames (determined by filetype) in a dir.
        """
        allImages = []
        mrmls = []
        dicoms = []   
        for folder, subs, files in os.walk(rootDir):
            for file in files:
                extension =  os.path.splitext(file)[1].lower() 
                if self.MODULE.utils.isDICOM(ext = extension):
                    dicoms.append(os.path.join(folder,file))                   
                if self.MODULE.utils.isMRML(ext = extension): 
                    mrmls.append(os.path.join(folder,file))  
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms}



    
    def getLoadables_byList(self, fileList):
        """Returns the loadable filenames (determined by filetype) 
           in filename list.
        """
        allImages = []
        mrmls = []
        dicoms = []
        others = []    


        
        #------------------------
        # Cycle through list to determine loadability.
        #------------------------
        for file in fileList:
            file = str(file)
            extension =  os.path.splitext(file)[1].lower() 
            if extension or (extension != ""):
                if self.MODULE.utils.isDICOM(ext = extension):
                    dicoms.append(file)                   
                if self.MODULE.utils.isMRML(ext = extension): 
                    mrmls.append(file)
                else:
                    others.append(file)
        return {'MRMLS':mrmls, 'ALLIMAGES': allImages, 'DICOMS': dicoms, 'OTHERS': others, 'ALLNONMRML': allImages + dicoms + others}
   

    

    def beginWorkflow(self, button = None):
        """ As stated. 
        """

        #------------------------
        # Show clearSceneDialog
        #------------------------
        if not button and not self.MODULE.utils.isCurrSceneEmpty():           
            self.MODULE.XnatView.initClearDialog()
            self.MODULE.XnatView.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow) 
            self.MODULE.XnatView.clearSceneDialog.show()
            return
        
        
        
        #------------------------
        # Begin Workflow once button in clearSceneDialog is pressed.
        #------------------------
        #
        # Clear the scene and current session if button was 'yes'.
        #
        if (button and 'yes' in button.text.lower()):
            self.MODULE.XnatView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)
        #    
        # Acquire vars: current treeItem, the XnatPath, and the remote URI for 
        # getting the file.
        #
        currItem = self.MODULE.XnatView.currentItem()
        pathObj = self.MODULE.XnatView.getXnatUriObject(currItem)
        remoteURI = self.MODULE.settingsFile.getAddress(self.MODULE.XnatLoginMenu.hostDropdown.currentText) + '/data' + pathObj['childQueryUris'][0]
        #    
        # Check path string if at the scan level -- adjust accordingly.
        #
        if '/scans/' in remoteURI and not remoteURI.endswith('/files'):
            remoteURI += '/files'
        #
        # Construct dst string (the local file to be downloaded).
        #
        dst = os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['downloads'],  currItem.text(self.MODULE.XnatView.getColumn('MERGED_LABEL')))
            

            
        #------------------------
        # Determine loader based on the XnatView's currItem
        #------------------------
        #
        # Slicer files
        #
        if (('files' in remoteURI and 'resources/Slicer' in remoteURI) and remoteURI.endswith(self.MODULE.utils.defaultPackageExtension)): 
            loader = self.MODULE.XnatSceneLoadWorkflow
        #    
        # Other readable files
        #
        elif ('files' in remoteURI and '/resources/' in remoteURI):
            loader =  self.MODULE.XnatFileLoadWorkflow
        #    
        #  DICOMS
        #
        else:      
            loader =  self.MODULE.XnatDicomLoadWorkflow
                    
                    
                
        #------------------------
        # Call load of subclass loader.
        #------------------------
        args = {"xnatSrc": remoteURI, 
                "localDst":dst, 
                "folderContents": None}
        loadSuccessful = loader.initLoad(args)  
            
            
            
        #------------------------
        # Enable XnatView
        #------------------------
        self.MODULE.XnatView.setEnabled(True)
        self.lastButtonClicked = None
    
        
