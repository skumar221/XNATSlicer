from __future__ import with_statement
from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import shutil



from XNATFileInfo import *

from XNATUtils import *
from XNATTimer import *

# For zipping packages

from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED
#########################################################
#
# 
comment = """
  XNATScenePackager is used for the Save/Update process.  When 
  sending a scene to XNAT, the class conducts the necessary slicer.app 
  calls to get all of the scene's files into a .zip.  It then proceeds
  to make the appropriate changes related to shared image nodes 
  (which need to be removed and stored on XNAT in a separate
  directory).  The end result is a lightweight scene package that 
  remotely refers to the relevant image nodes.

# TODO : 
"""
#
#########################################################


class XNATScenePackager(object):
    """Class containing methods for packaging scenes pertinent to the 
       Slicer-XNAT workflow.  The major feature of this class is that 
       it handles any shared nodes and 1) uploads them to a "shared" 
       folder on XNAT 2) eliminates them from scene packages sent to XNAT."""
       
    def __init__(self, browser = None):
        self.browser = browser
        self.viewer = self.browser.XNATView
        self.utils = XNATUtils()
        self.hostName = 'https://central.xnat.org'
    
    def determineSceneType(self):
        scene = slicer.app.mrmlScene()
        currURL = os.path.normpath(scene.GetURL())
        if currURL == None or currURL == '': return None
        elif currURL.find(self.utils.projectPath) == 0: return "XNATSlicerScene"
        else: return "LocalScene"                    
        return None
                                       
    def bundleScene(self, args):
            #
            # STEP 1: Init variables.
            #
            XNATCommunicator = args['XNATCommunicator'] 
            XNATDir = args['saveDir']
            XNATSharedDir = args['sharedDir']
            sceneName = args['fileName'] 
            metadata = args['metadata']      
            packageName = os.path.basename(sceneName.split(".")[0])              
            #
            # STEP 2: Analyzes the scene type.
            #
            #print self.utils.lf() +  "ANALYZING SCENE TYPE"
            sceneType = self.determineSceneType() 
            #print self.utils.lf() +  "SCENE TYPE: %s"%(sceneType)                     
            #   
            # STEP 3: Create a directory for packaging.
            #            
            tempDir = os.path.join(self.utils.tempUploadPath, packageName)
            #print self.utils.lf() +  "CREATE PACKAGE DIRECTORY: %s"%(tempDir)
            try:
                #print self.utils.lf() + ("%s does not exist. Making it."%(tempDir)) 
                self.utils.removeFilesInDir(tempDir)
                os.rmdir(tempDir)
            except Exception, e: pass 
            try: os.mkdir(tempDir)
            except Exception, e: pass
            #
            # STEP 4: Write according to scene type and if there's matching metadata.
            #
            #print self.utils.lf() +  "BEGINNING THE SCENE WRITE"
            self.browser.updateStatus(["", "Write all...", ""]) 
            #print self.utils.lf() +  "WRITING ALL!"
            self.writeScene_All(tempDir)            
            slicer.app.processEvents()              
           
            self.browser.updateStatus(["", "Finding mrml...", ""]) 
            mrml = None
            for root, dirs, files in os.walk(tempDir):
                for relFileName in files:
                    if relFileName.endswith("mrml"):
                        mrml = os.path.join(root, relFileName)
                        break
                    
            slicer.app.processEvents()
            self.browser.updateStatus(["", "Bundling scene.  Please wait...", ""])            
            return {'path':self.utils.adjustPathSlashes(tempDir), 
                    'mrml': self.utils.adjustPathSlashes(mrml)}

    # SOURCE OF FOLLOWING CODE: 
    # http://stackoverflow.com/questions/296499/how-do-i-zip-the-contents-of-a-folder-using-python-version-2-5
    #
    # NOTE: To be deprecated after MRB methods are put in place.
    def zipdir(self, basedir=None, zipArchive=None):
        assert os.path.isdir(basedir)
        with closing(ZipFile(zipArchive, "w", ZIP_DEFLATED)) as z:
            for root, dirs, files in os.walk(basedir):
                #NOTE: ignore empty directories
                for fn in files:
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(basedir)+len(os.sep):] #XXX: relative path
                    z.write(absfn, zfn)
    
    def packageDir(self, packageFilePath, sceneDir):
        #logic = slicer.app.applicationLogic()
        #logic.SaveSceneToSlicerDataBundleDirectory(sceneDir, None)
        slicer.app.applicationLogic().Zip(packageFilePath,sceneDir)
        
    def writeScene_All(self, saveDir):
        #slicer.app.processEvents()       
        if os.path.exists(saveDir): 
            self.utils.removeDirsAndFiles(saveDir)
                #slicer.app.processEvents()
        try: 
            os.makedirs(saveDir + "/Data")
        except Exception, e: 
            print self.utils.lf() +  "Likely the dir already exists: " + str(e)
        slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(saveDir, None)
        slicer.app.processEvents()
    
    def clearAndMakeDir(self, path):  
        if os.path.exists(path): shutil.rmtree(path, True)
        os.mkdir(path)
  