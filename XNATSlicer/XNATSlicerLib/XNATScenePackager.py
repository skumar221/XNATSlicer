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

comment = """
  XNATScenePackager is used for the Save/Update process.  When 
  sending a scene to XNAT, the class conducts the necessary slicer.app 
  calls to get all of the scene's files into a .zip.  

# TODO : 
"""


class XNATScenePackager(object):
    """Class containing methods for packaging scenes pertinent to the 
       Slicer-XNAT workflow."""


       
    def __init__(self, browser = None):
        self.browser = browser


    
    def bundleScene(self, args):
        """ Main function of the class
        """
    
        # Init variables.
        XNATCommunicator = args['XNATCommunicator'] 
        XNATDir = args['saveDir']
        XNATSharedDir = args['sharedDir']
        sceneName = args['fileName'] 
        metadata = args['metadata']      
        packageName = os.path.basename(sceneName.split(".")[0])  


        # Create a directory for packaging.
        tempDir = os.path.join(self.browser.utils.tempUploadPath, packageName)
        print self.browser.utils.lf() +  "CREATE PACKAGE DIRECTORY: %s"%(tempDir)
        
        try:
            print self.browser.utils.lf() + ("%s does not exist. Making it."%(tempDir)) 
            self.browser.utils.removeFilesInDir(tempDir)
            os.rmdir(tempDir)
        except Exception, e: 
            pass
         
        try: 
            os.mkdir(tempDir)
        except Exception, e: 
            pass

        
        # Write according to scene type and if there's matching metadata.
        print self.browser.utils.lf() +  "Writing scene to: %s"%(tempDir)
        self.saveToBundleDirectory(tempDir)            


        # Acqure mrml filename
        mrml = None
        for root, dirs, files in os.walk(tempDir):
            for relFileName in files:
                if relFileName.endswith("mrml"):
                    mrml = os.path.join(root, relFileName)
                    break
                    
       
        return {'path':self.browser.utils.adjustPathSlashes(tempDir), 
                'mrml': self.browser.utils.adjustPathSlashes(mrml)}




    
    def packageDir(self, zipFileName, directoryToZip):
        """ Zips the bundled directory according to the
        native API
        """
        slicer.app.applicationLogic().Zip(str(zipFileName), str(directoryToZip))
        #return
        
  


        
    def saveToBundleDirectory(self, saveDir):
        """ Puts all of the scene nodes (including the mrml) into a bundle
        directory.
        """ 


        # Remove existing if the name is the same
        if os.path.exists(saveDir): 
            self.browser.utils.removeDirsAndFiles(saveDir)

            
        # Make the save directory
        try: 
            os.makedirs(saveDir + "/Data")
        except Exception, e: 
            print self.browser.utils.lf() +  "Likely the dir already exists: " + str(e)

            
        # Call the API command
        slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(saveDir, None)




        
    def clearAndMakeDir(self, path): 
        """ Utility
        """ 
        if os.path.exists(path): shutil.rmtree(path, True)
        os.mkdir(path)
  
