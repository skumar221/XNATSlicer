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
XnatLoadWorkflow is a parent class to various loader types
(Slicer files, DICOM folders, individual files, etc.).  Loader types
are determined by the treeViewItem being clicked in the 
XnatLoadWorkflow function 'beginWorkflow'. 
"""






class XnatLoadWorkflow(object):
    """ Parent Load workflow class to: XnatDicomLoadWorkflow, 
        XnatSceneLoadWorkflow, and XnatFileLoadWorkflow.
    """



    
    def __init__(self, browser):
        """ Parent init.
        """
        self.utils = XnatUtils()
        self.browser = browser       
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None


        
    def initLoad(self):
        """ As stated.
        """


        
    def load(self, args):
        """ As stated.
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
        """ As stated.
        """
        qt.QMessageBox.warning( None, warnStr[0], warnStr[1])
        self.browser.XnatView.setEnabled(True)



        
    def getLoadables_byDir(self, rootDir):
        """Returns the loadable filenames (determined by filetype) in a dir.
        """
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
        """Returns the loadable filenames (determined by filetype) 
           in filename list.
        """
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
   

    

    def beginWorkflow(self, button = None):
        """ As stated. 
        """

        
        #------------------------
        # Show clearSceneDialog
        #------------------------
        if not button and not self.browser.utils.isCurrSceneEmpty():           
            self.browser.XnatView.initClearDialog()
            self.browser.XnatView.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow) 
            self.browser.XnatView.clearSceneDialog.show()
            return
        
        
        
        #------------------------
        # Begin Workflow once button is pressed.
        #------------------------

        # Clear the scene and current session if button was 'yes'.
        if (button and 'yes' in button.text.lower()):
            self.browser.XnatView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)

            
        # Acquire vars: current treeItem, the XnatPath, and the remote URI for 
        # getting the file.
        currItem = self.browser.XnatView.viewWidget.currentItem()
        pathObj = self.browser.XnatView.getXnatUriObject(currItem)
        remoteURI = self.browser.settings.getAddress(self.browser.XnatLoginMenu.hostDropdown.currentText) + '/data' + pathObj['childQueryUris'][0]

            
        # Check path string if at the scan level.
        if '/scans/' in remoteURI and not remoteURI.endswith('/files'):
            remoteURI += '/files'

                
        # Construct dst (local).
        dst = os.path.join(self.browser.utils.downloadPath,  currItem.text(self.browser.XnatView.getColumn('MERGED_LABEL')))
            

            
        #------------------------
        # Determine loader based on currItem
        #------------------------
        
        # Slicer files
        if (('files' in remoteURI and 'resources/Slicer' in remoteURI) and remoteURI.endswith(self.browser.utils.defaultPackageExtension)): 
            loader = self.browser.XnatSceneLoadWorkflow
            
            # Other readable files
        elif ('files' in remoteURI and '/resources/' in remoteURI):
            loader =  self.browser.XnatFileLoadWorkflow
            
            #  DICOMS
        else:      
            loader =  self.browser.XnatDicomLoadWorkflow
                    
                    
                
        #------------------------
        # Call load
        #------------------------
        args = {"xnatSrc": remoteURI, 
                "localDst":dst, 
                "folderContents": None}
        loadSuccessful = loader.initLoad(args)  
            
            
            
        #------------------------
        # Enable TreeView
        #------------------------
        self.browser.XnatView.viewWidget.setEnabled(True)
        self.lastButtonClicked = None
    
        
