from XnatLoadWorkflow import *
import DICOMScalarVolumePlugin 


comment = """
XnatDicomLoadWorkflow is the loader class for all DICOM input received
from Xnat.  The high-level workflow of the download is as follows:

1) Download a zip file of one scan or multiple scans in DICOM format.
2) Unpack the zip file and cache accordingly.
3) Apply these files to the slicer DICOM database.
4) Leverage the slicer 'DICOMWidget' to parse and and load the images.

NOTE: DICOMLoader makes use of Slicer's DICOM database and 
Steve Pieper's DICOMPlugin for parsing.

TODO:
"""


class XnatDicomLoadWorkflow(XnatLoadWorkflow):
    """ XnatDicomLoadWorkflow conducts the necessary steps
        to load DICOM files into Slicer.
    """
    
    def initLoad(self, args):
        """ Starter function for loading DICOMs into Slicer from
            Xnat.  The function 'load' is its successor.  This function
            determines if the user is downloading a single folder or multiple dicom
            folders.
        """
        
        #--------------------
        # Call parent class -- sets relevant public
        # variables.
        #--------------------
        super(XnatDicomLoadWorkflow, self).load(args)


        
        #--------------------
        # Define public vars. for XnatDicomLoadWorkflow.
        #--------------------
        self.XnatLevel = ''
        if '/scans/' in self.xnatSrc:
            self.XnatLevel = 'scans'
        elif '/experiments/' in self.xnatSrc:
            self.XnatLevel = 'experiments'
        elif '/subjects/' in self.xnatSrc:
            self.XnatLevel = 'subjects'
        self.folderName = os.path.basename(os.path.dirname(self.xnatSrc))
        self.downloadables = []
        self.DICOMWidget = None



        #---------------------
        # Is the user downloading multiple folders?
        #---------------------
        if self.xnatSrc.endswith("files"):
            #
            # If not, proceed with load at the current URI 
            # (contianed in 'args' argument)
            #
            self.load()
        else:
            #
            # If so, then setup+show dialog asking user if they
            # want to proceed.
            #
            self.areYouSureDialog = qt.QMessageBox()
            self.areYouSureDialog.setIcon(4)

            self.areYouSureDialog.setText("You are about to load all of " +   
                                          self.folderName + "'s "+  
                                          "DICOMs.\n" + 
                                          "This may take several minutes.\n" +
                                          "Are you sure you want to continue?")
            self.areYouSureDialog.addButton(qt.QMessageBox.Yes)
            self.areYouSureDialog.addButton(qt.QMessageBox.No)
            self.areYouSureDialog.connect('buttonClicked(QAbstractButton*)', self.load)
            self.areYouSureDialog.show()


            
            
    def getDownloadables(self, parentXnatUri):
        """ Called within the 'load' function. Checks if DICOM 
            files exist at the 'resources' level of a given XNAT path.
        """

        #---------------------
        # Get the resources of the Xnat URI provided in the argument.
        #---------------------
        resources = self.browser.XnatIo.getResources(parentXnatUri)     
        #print "%s parentXnatUri: %s\nresources:%s"%(self.browser.utils.lf(), parentXnatUri, resources) 


        #---------------------
        # Loop through resources.
        #---------------------
        for resource in resources:
            #
            # Construct the fileFolderUri.
            #
            fileFolderUri =  "%s/resources/%s/files"%(parentXnatUri, resource) 
            #
            # Get the contentsof the fileFolderUri.
            #
            contents = self.browser.XnatIo.getFolderContents(fileFolderUri, metadataTags = ['Name', 'Size'])
            fileNames = contents['Name']
            #
            # Check to see if the file extensions (contents) are valid.
            #
            for filename in fileNames:
                #
                # If valud, add to "downloadables" if DICOM
                #
                if self.utils.isDICOM(filename.rsplit('.')[1]):
                    self.downloadables.append(fileFolderUri + "/" + filename)
                else:
                    print  "%s Not a usable file: '%s' "%(self.utils.lf(), (filename))



                
    def load(self): 
        """ Main load function for downloading DICOM files
            from an XNAT server and loading them into slicer. 
            The general approach is as follows: 
            
            1) Clear existing download path
            2) Acquire downloadables depending on the XNAT level.  
               (Experiment is the minimum download level.)
            3) Get the downloadables by zipped folder files.
            4) Conduct the necessary caching and file management of the download.
            5) Insert downloaded DICOMS into slicer.dicomDatabase
            6) Query the database for the recently downloaded DICOMs
            7) Acquire "Loadables" based on database query.
            8) Load loadables with highest file count to Slicer.
        """

            
        experimentsList = []
        scansList = []   


            
        #--------------------
        # Remove existing files in the local download path (self.localDst)
        # if they exist.
        #--------------------
        if os.path.exists(self.localDst):
            self.utils.removeFilesInDir(self.localDst)
        if not os.path.exists(self.localDst): 
            os.mkdir(self.localDst)


        print(self.browser.utils.lf(), "Downloading DICOMS in '%s'."%(self.xnatSrc),"Please wait.") 
  

        
        #--------------------
        # SUBJECT - get downloadables 
        #
        # NOTE: This is currently untested and disallowed 
        # from the workflow, though it could be enabled in the
        # future.
        #--------------------
        if self.XnatLevel == 'subjects':

            #
            # Get downloadables
            #
            self.getDownloadables(os.path.dirname(self.xnatSrc)) 

            
            #
            # Get 'experiments'       
            #                        
            experimentsList, sizes = self.browser.XnatIo.getFolderContents(self.xnatSrc, self.browser.utils.XnatMetadataTags_subjects)


            #
            # Check for DICOMs (via 'resources') at the 'experiments' level.
            #
            for expt in experimentsList:
                self.getDownloadables(self.xnatSrc + "/" + expt)


            #    
            # Get 'scans'
            #
            for expt in experimentsList:
                parentScanFolder = self.xnatSrc + "/" + expt + "/scans"
                scanList = self.browser.XnatIo.getFolderContents(parentScanFolder, self.browser.utils.XnatMetadataTags_scans)
                for scan in scanList:
                    self.getDownloadables(parentScanFolder + "/" + scan)
        

                        
        #--------------------
        # EXPERIMENT - get downloadables.
        #--------------------
        elif self.XnatLevel == 'experiments':
            #print(self.browser.utils.lf(), "Retrieving experiment-level DICOMS.") 
            #
            # First, get the downloadables at the current URI.
            #
            self.getDownloadables(os.path.dirname(self.xnatSrc)) 
            #
            # Then, scan the folder contents of the 'scan' folders within
            # the experiment.  Get the downloadables accordingly.
            #
            scansList, sizes = self.browser.XnatIo.getFolderContents(self.xnatSrc, self.browser.utils.XnatMetadataTags_experiments)
            for scan in scansList:
                self.getDownloadables(self.xnatSrc + "/" + scan)


                    
        #--------------------
        # SCANS - get downloadables.
        #--------------------
        elif self.XnatLevel == 'scans':
            selector = self.xnatSrc.split("/files")[0] if self.xnatSrc.endswith('/files') else self.xnatSrc
            self.getDownloadables(selector)   


                
        #--------------------
        # RESOURCES - get downloadables.
        #--------------------
        elif self.XnatLevel == 'resources':
            self.getDownloadables(self.xnatSrc.split("/resources")[0])      
        


        #--------------------
        # Exit out if there are no downloadables.
        #--------------------           
        if len(self.downloadables) == 0:
            self.browser.XnatIo.downloadFailed("Download Failed", "No scans in found to download!")
            return 


        
        #--------------------
        # Set the local download path.
        #--------------------         
        if self.localDst.endswith("/"):
            self.localDst = self.localDst[:-2]                
        if not os.path.exists(self.localDst):
            os.mkdir(self.localDst)  


            
        #--------------------
        # Download all DICOMS as part of a zipped file.
        #--------------------           
        _dict = dict(zip(self.downloadables, [(self.localDst + "/" + os.path.basename(dcm)) for dcm in self.downloadables]))        
        zipFolders = self.browser.XnatIo.getFiles(_dict)


            
        #--------------------
        # Inventory downloaded zipfile
        #--------------------
        downloadedDICOMS = []
        for zipFile in zipFolders:
            extractPath = zipFile.split(".")[0]

            
            #
            # Remove existing extract path if it exists
            #
            if os.path.exists(extractPath): 
                self.utils.removeDirsAndFiles(extractPath)

                
            #    
            # If the zipfile does not exist, then exit.
            # (This is the result of the Cancel button in 
            # the download modal being clicked.) 
            #
            if not os.path.exists(zipFile):
                print "%s exiting workflow..."%(self.browser.utils.lf())  
                self.browser.XnatView.setEnabled(True) 
                return False


            #
            # Decompress zips.
            #
            self.utils.decompressFile(zipFile, extractPath)


            #
            # Add to files in the decompressed destination 
            # to downloadedDICOMS list.
            #
            print "%s Inventorying downloaded files..."%(self.browser.utils.lf())  
            for root, dirs, files in os.walk(extractPath):
                for relFileName in files:          
                    downloadedDICOMS.append(self.utils.adjustPathSlashes(os.path.join(root, relFileName)))
           

            
        #--------------------
        # Make sure Slicer's DICOMdatabase is set up.
        # Show a popup informing the user if it's not.
        # The user has to restart the process if it's not.
        #--------------------
        self.browser.XnatView.viewWidget.setEnabled(False) 
        m = slicer.util.mainWindow()
        if not slicer.dicomDatabase:
            msg =  """It doesn\'t look like your DICOM database directory is setup. Please set it up in the DICOM module and try your download again."""
            self.terminateLoad(['DICOM load', msg ])
            m.moduleSelector().selectModule('DICOM')     
               


        #--------------------
        # Add DICOM files to slicer.dicomDataase
        #--------------------
        i = ctk.ctkDICOMIndexer()
        i.addListOfFiles(slicer.dicomDatabase, downloadedDICOMS)


        
        #--------------------
        # Create dictionary of downloaded DICOMS
        # for quick retrieval when comparing with files
        # in the slicer.dicomDatabase.  Speed preferred over
        # memory consumption here.
        #--------------------      
        dlDicomObj = {}
        for dlFile in downloadedDICOMS:
            dlDicomObj[os.path.basename(dlFile)] = dlFile


            
        #--------------------
        # Parse through the slicer.dicomDatabase
        # to get all of the files, as determined by series.
        #--------------------
        matchedDatabaseFiles = []
        for patient in slicer.dicomDatabase.patients():
            for study in slicer.dicomDatabase.studiesForPatient(patient):
                for series in slicer.dicomDatabase.seriesForStudy(study):
                    seriesFiles = slicer.dicomDatabase.filesForSeries(series)
                    #
                    # Compare files in series with what was just downloaded.
                    # If there's a match, append to 'matchedDatabaseFiles'.
                    #
                    for sFile in seriesFiles:
                       if os.path.basename(sFile) in dlDicomObj: 
                           matchedDatabaseFiles.append(sFile)


                           
        #--------------------
        # Acquire loadabes as determined by
        # the 'DICOMScalarVolumePlugin' class, by feeding in 
        # 'matchedDatabaseFiles' as a nested array.
        #--------------------
        dicomScalarVolumePlugin = slicer.modules.dicomPlugins['DICOMScalarVolumePlugin']()
        loadables = dicomScalarVolumePlugin.examine([matchedDatabaseFiles])


        
        #--------------------
        # Determine loadable with the highest file count. 
        # This is usually all DICOM files collated as one volume.
        #--------------------
        highestFileCount = 0
        highestFileCountIndex = 0
        for i in range(0, len(loadables)):
            if len(loadables[i].files) > highestFileCount:
                highestFileCount = len(loadables[i].files)
                highestFileCountIndex = i


                
        #--------------------
        # Load loadable with the highest file count.
        # This is assumed to be the volume file that contains
        # the majority of the downloaded DICOMS.
        #--------------------
        dicomScalarVolumePlugin.load(loadables[highestFileCountIndex])
                    

            
        #--------------------
        # Reenable the XnatView so the user
        # can interact with it.
        #--------------------
        self.browser.XnatView.setEnabled(True)


      
        return True




            
    def beginDICOMSession(self):
        """ Once a DICOM folder has been downloaded, 
            track the origins of the files for Save/upload
            routines.
        """
        #print(self.browser.utils.lf(), "DICOMS successfully loaded.")
        sessionArgs = XnatSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "dicom download"
        self.browser.XnatView.startNewSession(sessionArgs)


