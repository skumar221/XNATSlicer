from __future__ import with_statement
from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import shutil
from contextlib import closing
from zipfile import ZipFile, ZIP_DEFLATED

from XnatFileInfo import *
from XnatUtils import *
from XnatTimer import *



comment = """
XnatScenePackager is used for the Save/Update process.  When 
sending a scene to an XNAT host, the class calls the necessary slicer.app API 
functions to get all of the scene's files into a .zip.  

TODO : 
"""



class XnatScenePackager(object):
    """Class containing methods for packaging scenes pertinent to the 
       XNATSlicer workflow.
    """
       
    def __init__(self, MODULE = None):
        """ Init function.
        """
        self.MODULE = MODULE

        

    
    def bundleScene(self, args):
        """ Main function for bundling a Slicer scene.
        """

        #-------------------
        # Init variables.
        #-------------------
        XnatIo = args['XnatIo'] 
        XnatDir = args['saveDir']
        XnatSharedDir = args['sharedDir']
        sceneName = args['fileName'] 
        metadata = args['metadata']      
        packageName = os.path.basename(sceneName.split(".")[0])  



        #-------------------
        # Create a directory for packaging.
        #-------------------
        tempDir = os.path.join(self.MODULE.utils.tempUploadPath, packageName)
        #print self.MODULE.utils.lf() +  "CREATE PACKAGE DIRECTORY: %s"%(tempDir)



        #-------------------
        # Try to remove the existing directory if it exists
        #-------------------
        try:
            #print self.MODULE.utils.lf() + ("%s does not exist. Making it."%(tempDir)) 
            if os.path.exists(tempDir): 
                self.MODULE.utils.removeDirsAndFiles(tempDir)
        except Exception, e: 
            pass
         
        try: 
            os.mkdir(tempDir)
        except Exception, e: 
            pass



        #-------------------
        # Make the save directory
        #-------------------
        try: 
            os.makedirs(tempDir + "/Data")
        except Exception, e: 
            print self.MODULE.utils.lf() +  "Likely the dir already exists: " + str(e)



        #-------------------
        # Call the API command 'slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory'
        #-------------------
        slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(tempDir, None)          



        #-------------------
        # Acqure .mrml filename within the bundlir dir
        #-------------------
        mrml = None
        for root, dirs, files in os.walk(tempDir):
            for relFileName in files:
                if relFileName.endswith("mrml"):
                    mrml = os.path.join(root, relFileName)
                    break


                
        #-------------------
        # Return appropriate dictionary with the mrml file
        # and the package directory.
        #-------------------
        return {'path':self.MODULE.utils.adjustPathSlashes(tempDir), 
                'mrml': self.MODULE.utils.adjustPathSlashes(mrml)}




    
    def packageDir(self, zipFileName, directoryToZip):
        """ Zips the bundled directory according to the
            native API methods.
        """
        slicer.app.applicationLogic().Zip(str(zipFileName), str(directoryToZip))
        #return
  
