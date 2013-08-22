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



def getLoader(loaderType, browser):
    if   loaderType == "scene": return SceneLoader(browser)
    elif loaderType == "dicom": return DICOMLoader(browser)
    elif loaderType == "file":  return FileLoader(browser)
    elif loaderType == "mass_dicom":  return DICOMLoader(browser)

    

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
   





    
