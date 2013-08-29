from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile
import urllib2
from datetime import datetime

from XNATFileInfo import *
from XNATUtils import *
from XNATScenePackager import *
from XNATTimer import *
from XNATSessionManager import *
from XNATMRMLParser import *
from XNATPopup import *

    

comment = """
XNATLoadWorkflow is a parent class to various loader types
(Slicer files, DICOM folders, individual files, etc.).  Loader types
are determined by the treeView item being clicked. 
"""






class XNATLoadWorkflow(object):
    """ Descriptor
    """



    
    def __init__(self, browser):
        """ Parent class of any load workflow
        """
        self.utils = XNATUtils()
        self.browser = browser       
        self.loadFile = None
        self.newMRMLFile = None
        self.currRemoteHost = None


        
        
    def load(self, args):
        """ Parent class of any load workflow
        """
        self.xnatSrc = args["xnatSrc"]
        self.localDst = args["localDst"]



        
    def setup(self):
        pass



     
    def loadFinish(self):
        """ Parent class of any load workflow
        """
        pass



    
    def terminateLoad(self, warnStr):
        """ Parent class of any load workflow
        """
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
   

    

    def beginWorkflow(self, button = None):
        """ Descriptor   
        """

        
        #------------------------
        # Clear Scene
        #------------------------
        if not button and not self.browser.utils.isCurrSceneEmpty():           
            self.browser.XNATView.initClearDialog()
            self.browser.XNATView.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow) 
            self.browser.XNATView.clearSceneDialog.show()
            return
        
        
        
        #------------------------
        # Begin Workflow once Clear Scene accepted
        #------------------------
        if (button and 'yes' in button.text.lower()) or self.browser.utils.isCurrSceneEmpty():


            # Clear the scene and current session
            self.browser.XNATView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)

            
            # Acquire vars
            currItem = self.browser.XNATView.viewWidget.currentItem()
            pathObj = self.browser.XNATView.getXNATPathObject(currItem)
            remoteURI = self.browser.settings.getAddress(self.browser.XNATLoginMenu.hostDropdown.currentText) + '/data' + pathObj['childQueryPaths'][0]

            
            # Check path string if at the scan level
            if '/scans/' in remoteURI and not remoteURI.endswith('/files'):
                remoteURI += '/files'

                
            # Construct dst (local)
            dst = os.path.join(self.browser.utils.downloadPath, 
                               currItem.text(self.browser.XNATView.column_name))


            
            #------------------------
            # Determine loader based on currItem
            #------------------------
            
            # Slicer files
            if (('files' in remoteURI and 'resources/Slicer' in remoteURI) and remoteURI.endswith(self.browser.utils.defaultPackageExtension)): 
                loader = self.browser.SceneLoadWorkflow
                
                # Other readable files
            elif ('files' in remoteURI and '/resources/' in remoteURI):
                loader =  self.browser.FileLoadWorkflow
                
                #  DICOMS
            else:      
                loader =  self.browser.DICOMLoadWorkflow
                    
                    
                
            #------------------------
            # Call load
            #------------------------
            args = {"xnatSrc": remoteURI, 
                    "localDst":dst, 
                    "folderContents": None}
            loadSuccessful = loader.load(args)  
            
            
            
            #------------------------
            # Enable TreeView
            #------------------------
            self.browser.XNATView.viewWidget.setEnabled(True)
            self.lastButtonClicked = None
    
        
