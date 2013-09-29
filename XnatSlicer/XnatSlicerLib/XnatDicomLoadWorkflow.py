from XnatLoadWorkflow import *
import DICOMScalarVolumePlugin 


comment = """
XnatDicomLoader is the loader class for all DICOM input received
from Xnat.  The high-level workflow of the download is as follows:

1) Download a zip file of one scan or multiple scans in DICOM format.
2) Unpack the zip file and cache accordingly
3) Apply these files to the database
4) Open the DICOMWidget.detailsPopup to parse and unify

DICOMLoader makes use of Slicer's DICOM database and 
Steve Pieper's DICOMPlugin for parsing.
"""






class XnatDicomLoadWorkflow(XnatLoadWorkflow):
    """ XnatDicomLoadWorkflow conducts the necessary steps
    to load DICOM files into Slicer. See above comment for 
    more details.
    """



    
    def initLoad(self, args):
        """ Starter function for loading DICOMs into Slicer from
        Xnat.  The function 'load' is its successor.
        """
        
        #
        # Call parent for variable setting.
        #
        super(XnatDicomLoadWorkflow, self).load(args)


        
        #
        # Define vars.
        #
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
        self.newDBFile = None
        self.prevDBFile = None


        
        #
        # indexingDicomsWindow (informational window for waiting).
        #
        msg =  """Indexing the downloaded DICOMS.  When finished, a \'DICOM Details\' window will appear pertaining only to the images downloaded.  Your previous DICOM database is still intact."""
        self.indexingDicomsWindow = qt.QMessageBox()
        self.indexingDicomsWindow.setText(msg)
        # Set icon to informational.
        self.indexingDicomsWindow.setIcon(1)
        # Block all input from other windows.
        self.indexingDicomsWindow.setWindowModality(2)

        

        #
        # Is the user downloading multiple folders?
        #
        if self.xnatSrc.endswith("files"):
            
            # if not, proceed with load
            self.load()
        else:
            
            # if so, then setup+show dialog asking user to proceed
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


            
            
    def getDownloadables(self, parentXnatPath):
        """Checks if DICOM files exist at the 'resources' 
        level of a given XNAT path.
        """
        print "getDownloadables"
        resources = self.browser.XnatCommunicator.getResources(parentXnatPath)     
        print "%s parentXnatPath: %s\nresources:%s"%(self.browser.utils.lf(), parentXnatPath, resources) 
        for resource in resources:
            filePath =  "%s/resources/%s/files"%(parentXnatPath, resource) 
            contents = self.browser.XnatCommunicator.getFolderContents(filePath, metadataTags = ['Name', 'Size'])
            fileNames = contents['Name']

            
            # Check to see if the file extensions are valid
            for filename in fileNames:
                if self.utils.isDICOM(filename.rsplit('.')[1]):
                    # Add to "downloadables" if good
                    self.downloadables.append(filePath + "/" + filename)
                else:
                    print  "%s Not a usable file: '%s' "%(self.utils.lf(), (filename))



 
                
    def load(self): 
        """ MAIN function.  Function once after user clicks 
        'Yes' in the 'Are You Sure?' dialog.
        """

            
        experimentsList = []
        scansList = []   


            
        #--------------------
        # Remove existing files in the local download path (self.localDst)
        #--------------------
        if os.path.exists(self.localDst):
            self.utils.removeFilesInDir(self.localDst)
        if not os.path.exists(self.localDst): 
            os.mkdir(self.localDst)


        print(self.browser.utils.lf(), "Downloading DICOMS in '%s'."%(self.xnatSrc),"Please wait.") 
  
                
        #--------------------
        # SUBJECT - get downloadables (currently not enabled and untested)
        #--------------------
        if self.XnatLevel == 'subjects':
            
            # Get downloadables
            self.getDownloadables(os.path.dirname(self.xnatSrc)) 
            
            # Get 'experiments'                               
            experimentsList, sizes = self.browser.XnatCommunicator.getFolderContents(self.xnatSrc, self.browser.utils.XnatMetadataTags_subjects)
            
            # Check for DICOMs (via 'resources') at the 'experiments' level.
            for expt in experimentsList:
                self.getDownloadables(self.xnatSrc + "/" + expt)
                    
            # Get 'scans'
            for expt in experimentsList:
                parentScanFolder = self.xnatSrc + "/" + expt + "/scans"
                scanList = self.browser.XnatCommunicator.getFolderContents(parentScanFolder, self.browser.utils.XnatMetadataTags_scans)
                for scan in scanList:
                    self.getDownloadables(parentScanFolder + "/" + scan)


                        
        #--------------------
        # EXPERIMENT - get downloadables
        #--------------------
        elif self.XnatLevel == 'experiments':
            #print "GETTING EXPERIMENT DICOMS"
            self.getDownloadables(os.path.dirname(self.xnatSrc)) 
            scansList, sizes = self.browser.XnatCommunicator.getFolderContents(self.xnatSrc, self.browser.utils.XnatMetadataTags_experiments)
            for scan in scansList:
                self.getDownloadables(self.xnatSrc + "/" + scan)


                    
        #--------------------
        # SCAN - get downloadables
        #--------------------
        elif self.XnatLevel == 'scans':
            selector = self.xnatSrc.split("/files")[0] if self.xnatSrc.endswith('/files') else self.xnatSrc
            self.getDownloadables(selector)   


                
        #--------------------
        # RESOURCES - get downloadables
        #--------------------
        elif self.XnatLevel == 'resources':
            self.getDownloadables(self.xnatSrc.split("/resources")[0])      
        

                
        #--------------------
        # Download all dicoms as part of a zip
        #--------------------   
        if len(self.downloadables) == 0:
            self.browser.XnatCommunicator.downloadFailed("Download Failed", "No scans in found to download!")
            return 
            
        if self.localDst.endswith("/"):
            self.localDst = self.localDst[:-2]                
        if not os.path.exists(self.localDst):
            os.mkdir(self.localDst)  

        print self.downloadables
        self.localDst = self.localDst.replace('...', '')
        _dict = dict(zip(self.downloadables, [(self.localDst + "/" + os.path.basename(dcm)) for dcm in self.downloadables]))
        
        zipFolders = self.browser.XnatCommunicator.getFiles(_dict)


            
        #--------------------
        # Inventory downloaded zipfile
        #--------------------
        print "%s Inventorying downloaded files..."%(self.browser.utils.lf())    
        downloadedDICOMS = []
        for z in zipFolders:
            d = z.split(".")[0]
                
            # remove existing unzip path if it exists
            if os.path.exists(d): 
                self.utils.removeDirsAndFiles(d)
                    
            # decompress zips
            self.utils.decompressFile(z, d)
            #slicer.app.processEvents()
            
            # add to downloadedDICOMS list
            for root, dirs, files in os.walk(d):
                for relFileName in files:          
                    downloadedDICOMS.append(self.utils.adjustPathSlashes(os.path.join(root, relFileName)))
           

            
        #--------------------
        # Make sure Slicer's DICOMdatabase is set up
        #--------------------
        self.browser.XnatView.viewWidget.setEnabled(False) 
        m = slicer.util.mainWindow()
        if not slicer.dicomDatabase:
            msg =  """It doesn\'t look like your DICOM database directory is setup. Please set it up in the DICOM module and try your download again."""
            self.terminateLoad(['DICOM load', msg ])
            m.moduleSelector().selectModule('DICOM')     
        else: 
            self.indexingDicomsWindow.show()
               


        #--------------------
        # Add dicom files to slicer dicom database
        #--------------------
        i = ctk.ctkDICOMIndexer()
        i.addListOfFiles(slicer.dicomDatabase, downloadedDICOMS)


        dlDicomObj = {}
        for dlFile in downloadedDICOMS:
            dlDicomObj[os.path.basename(dlFile)] = dlFile
            
        matchedDatabaseFiles = []
        for patient in slicer.dicomDatabase.patients():
            for study in slicer.dicomDatabase.studiesForPatient(patient):
                for series in slicer.dicomDatabase.seriesForStudy(study):
                    seriesFiles = slicer.dicomDatabase.filesForSeries(series)
                    for sFile in seriesFiles:
                       if os.path.basename(sFile) in dlDicomObj: 
                           matchedDatabaseFiles.append(sFile)

        print matchedDatabaseFiles
        c = slicer.modules.dicomPlugins['DICOMScalarVolumePlugin']()
        loadables = c.examine([matchedDatabaseFiles])

        highFileCountIndex = 0
        for i in range(0, len(loadables)):
            print len(loadables[i].files), i
            if len(loadables[i].files) > highFileCountIndex:
                highFileCountIndex = i

        print "HIGH FILE COUNT", highFileCountIndex
        c.load(loadables[highFileCountIndex])
                    

            
        #--------------------
        # Update browser status
        #--------------------
        self.browser.XnatView.setEnabled(True)


      
        return True



        
    def checkPopupOpen(self):
        """ Determines if the DICOM details popup is visible. 
        Adjusts the XnatViewer accordingly.
        """
        if self.DICOMWidget and self.DICOMWidget.detailsPopup.window.isHidden():
            slicer.app.disconnect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)
            #print(self.browser.utils.lf(), "Restoring original DICOM database.  Please wait.")
            self.restorePrevDICOMDB()
            del self.DICOMWidget
            #print(self.browser.utils.lf(), "Finished original DICOM database.")
            self.browser.XnatView.setEnabled(True)



            
    def beginDICOMSession(self):
        """ As stated.
        """
        #print(self.browser.utils.lf(), "DICOMS successfully loaded.")
        sessionArgs = XnatSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "dicom download"
        self.browser.XnatView.startNewSession(sessionArgs)



        
    def restorePrevDICOMDB(self):
        """ As stated.
        """
        if os.path.exists(self.newDBFile):
            shutil.copy(self.newDBFile, self.prevDBFile)
