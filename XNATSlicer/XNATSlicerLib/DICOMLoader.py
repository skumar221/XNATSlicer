from XNATLoadWorkflow import *



comment = """
"""






class DICOMLoader(XNATLoadWorkflow):
    """ DICOMLoader conducts the necessary steps
    to load DICOM files into Slicer
    """


    
    def setup(self):
        pass



    
    def load(self, args):
        #print(self.browser.utils.lf(), "Downloading DICOMS...") 


        # Call parent
        super(DICOMLoader, self).load(args)

        
        # Define vars
        self.XNATLevel = ''
        if '/scans/' in self.xnatSrc:
            self.XNATLevel = 'scans'
        elif '/experiments/' in self.xnatSrc:
            self.XNATLevel = 'experiments'
        elif '/subjects/' in xnatSrc:
            self.XNATLevel = 'subjects'

            
        self.folderName = os.path.basename(os.path.dirname(self.xnatSrc))
        self.downloadables = []
        self.DICOMWidget = None
        self.newDBFile = None
        self.prevDBFile = None


        # Is the user downloading multiple folders?
        if self.xnatSrc.endswith("files"):
            
            # if not, proceed with load
            self.proceedWithLoad('yes')
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
            self.areYouSureDialog.connect('buttonClicked(QAbstractButton*)', self.proceedWithLoad)
            self.areYouSureDialog.show()


            
            
    def checkForResourceDICOMS(self, parentXNATPath):
        """Checks if DICOM files exist at the 'resources' level.
        """

        
        #print "%s %s"%(self.browser.utils.lf(), parentXNATPath)
        resources = self.browser.XNATCommunicator.getResources(parentXNATPath)     
        #print "RESOURCES %s %s"%(self.browser.utils.lf(), resources) 
        for res in resources:
            filePath =  "%s/resources/%s/files"%(parentXNATPath,res) 
            #print "RESOURCES %s %s"%(self.browser.utils.lf(), filePath) 
            content, size = self.browser.XNATCommunicator.getFolderContents(filePath, metadataTag = 'Name')
            self.vetDICOMs(filePath, content)


            
    
    def vetDICOMs(self, filePath, fileNames):
        """  Cleans the DICOM list based on what is an acceptable
        format.
        """
        #print "%s %s"%(self.browser.utils.lf(), fileNames) 
        for filename in fileNames:
            try:
                ext = filename.split(".")[1]
                if self.utils.isDICOM(ext.lower()):
                    if not filePath.endswith("/"): 
                        filePath +="/"
                    self.downloadables.append(filePath + filename)
                else:
                    print  "%s Not a dicom: '%s' "%(self.utils.lf(), (filePath + filename))
            except Exception, e:
                print  "%s Likely not a usable file: '%s' "%(self.utils.lf(), (filePath + filename)) + str(e)



                
    def proceedWithLoad(self, button): 
        """ Function once after user clicks 'Yes' in the 'Are You Sure?' dialog.
        """
        
        proceed = False
        if isinstance(button, basestring) and 'yes' in button:
            proceed = True
        elif button.text and 'yes' in button.text.lower():
            proceed = True


            
        if proceed:

            experimentsList = []
            scansList = []   
            #print(self.browser.utils.lf(), "Downloading DICOMS in '%s'."%(self.xnatSrc),"Please wait.")   


            
            #--------------------
            # Remove existing files in the local download path (self.localDst)
            #--------------------
            if os.path.exists(self.localDst):
                self.utils.removeFilesInDir(self.localDst)
            if not os.path.exists(self.localDst): 
                os.mkdir(self.localDst)


                
            #--------------------
            # If the tree node level is at 'subjects'
            # check for DICOMs accordingly.
            #--------------------
            if self.XNATLevel == 'subjects':
                # Get 'resources' at the 'experiment' level.
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc)) 
                # Get 'experiments'.                                 
                experimentsList = self.browser.XNATCommunicator.getFolderContents(self.xnatSrc)
                # Check for DICOMs (via 'resources') at the 'experiments' level.
                for expt in experimentsList:
                    self.checkForResourceDICOMS(self.xnatSrc + "/" + expt)
                # Get 'scans'
                for expt in experimentsList:
                    parentScanFolder = self.xnatSrc + "/" + expt + "/scans"
                    scanList = self.browser.XNATCommunicator.getFolderContents(parentScanFolder)
                    for scan in scanList:
                        self.checkForResourceDICOMS(parentScanFolder + "/" + scan)


                        
            #--------------------
            # If the tree node level is at 'experiments', 
            # check for dicoms at experiments level
            #--------------------
            elif self.XNATLevel == 'experiments':
                #print "GETTING EXPERIMENT DICOMS"
                self.checkForResourceDICOMS(os.path.dirname(self.xnatSrc)) 
                scansList = self.browser.XNATCommunicator.getFolderContents(self.xnatSrc)
                for scan in scansList:
                    self.checkForResourceDICOMS(self.xnatSrc + "/" + scan)


                    
            #--------------------
            # If the tree node level is at 'scans', 
            # check for dicoms at the scans level
            #--------------------
            elif self.XNATLevel == 'scans':
                #print "GETTING SCAN DICOMS"
                selector = self.xnatSrc.split("/files")[0] if self.xnatSrc.endswith('/files') else self.xnatSrc
                self.checkForResourceDICOMS(selector)   


                
            #--------------------
            # If the tree node level is at 'resources', check for dicoms at the resources level
            #--------------------
            elif self.XNATLevel == 'resources':
                #print "GETTING RESOURCE DICOMS"
                self.checkForResourceDICOMS(self.xnatSrc.split("/resources")[0])    


                
            #--------------------
            # Download all dicoms as part of a zip
            #--------------------
            import math   # for progress calculation    

            if len(self.downloadables)==0:
                self.browser.XNATCommunicator.downloadFailed("Download Failed", "No scans in found to download!")
                return 
            
            if self.localDst.endswith("/"):
                self.localDst = self.localDst[:-2]                
            if not os.path.exists(self.localDst):
                    os.mkdir(self.localDst)  

            zipFolders = self.browser.XNATCommunicator.getFiles(dict(zip(self.downloadables, 
                                           [(self.localDst + "/" + os.path.basename(dcm)) for dcm in self.downloadables])))


            
            #--------------------
            # Inventory downloaded zjpfile
            #--------------------
            #print (self.browser.utils.lf(), "Inventorying downloaded files...")    
            downloadedDICOMS = []
            for z in zipFolders:
                d = z.split(".")[0]
                
                # remove existing zip if it exists
                if os.path.exists(d): 
                    self.utils.removeDirsAndFiles(d)
                    
                # decompress zips
                self.utils.decompressFile(z, d)
                slicer.app.processEvents()
                
                # add to downloadedDICOMS list
                for root, dirs, files in os.walk(d):
                    for relFileName in files:          
                        downloadedDICOMS.append(self.utils.adjustPathSlashes(os.path.join(root, relFileName)))
            m = slicer.util.mainWindow()


            
            #--------------------
            # Make sure Slicer's DICOMdatabase is set up
            #--------------------
            if not slicer.dicomDatabase:
                msg =  'It doesn\'t look like your DICOM database '
                msg += 'directory is setup. Please set it up in '
                msg += 'the DICOM module and try your download again.'
                self.terminateLoad(['DICOM load',  ])
                m.moduleSelector().selectModule('DICOM')     
            else: 
                msg =  'Indexing the downloaded DICOMS.  '
                msg += 'When finished, a \'DICOM Details\' window will appear '
                msg += 'pertaining only to the images downloaded (your previous '
                msg += 'DICOM database is still intact.)'
                self.terminateLoad(['DICOM load', msg])    
                

            
            #--------------------
            # Store existing slicer.dicomdatabase contents to file
            #--------------------
            #print(self.browser.utils.lf(), "Adding to Slicer's DICOM database...")
            prevDICOMS = slicer.dicomDatabase.allFiles()


            
            #--------------------
            # Backup the old slicer database file
            #--------------------
            self.prevDBFile = slicer.dicomDatabase.databaseFilename
            self.newDBFile = os.path.join(os.path.dirname(self.utils.dicomDBBackupFN), os.path.basename(self.utils.dicomDBBackupFN))
            self.newDBFile = self.utils.adjustPathSlashes(self.newDBFile)
            if os.path.exists(self.newDBFile):
                self.utils.removeFile(self.newDBFile)            
            #print (self.utils.lf() + "COPYING %s to %s"%(self.prevDBFile, self.newDBFile))
            shutil.copy(self.prevDBFile, self.newDBFile)


            
            #--------------------
            #  Clear the slicer database file
            #--------------------
            slicer.dicomDatabase.initializeDatabase()

            
            
            #--------------------
            # Add dicom files to slicer dicom database
            #--------------------
            i = ctk.ctkDICOMIndexer()
            for dicomFile in downloadedDICOMS:          
                #print(self.browser.utils.lf(), "Adding '%s'"%(dicomFile), "to Slicer's DICOM database.", "Please wait...")  
                #print("Adding '%s'"%(dicomFile), "to Slicer's DICOM database.", "Please wait...")  
                i.addFile(slicer.dicomDatabase, dicomFile)#, cachedPath)

                

            #--------------------
            # Open a custum dicom module
            #--------------------
            from DICOM import DICOMWidget
            self.DICOMWidget = DICOMWidget()         
            self.DICOMWidget.parent.hide()
            self.DICOMWidget.detailsPopup.window.setWindowTitle("XNAT DICOM Loader (from DICOMDetailsPopup)")         

            
            
            #--------------------
            # Connect button signals from dicom module
            #--------------------
            self.DICOMWidget.detailsPopup.loadButton.connect('clicked()', self.beginDICOMSession)


            
            #--------------------
            # Connect all other signals, to catch if the popup window was closed by user
            #--------------------
            slicer.app.connect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)


            
            #--------------------
            # Update browser status
            #--------------------
            self.browser.XNATView.setEnabled(True)


            
            #--------------------
            # Open details popup
            #--------------------
            self.DICOMWidget.detailsPopup.open()


      
            return True



        
    def checkPopupOpen(self):
        """ Determines if the DICOM details popup is visible. 
        Adjusts the XNATViewer accordingly.
        """
        if self.DICOMWidget and self.DICOMWidget.detailsPopup.window.isHidden():
            slicer.app.disconnect("focusChanged(QWidget *, QWidget *)", self.checkPopupOpen)
            #print(self.browser.utils.lf(), "Restoring original DICOM database.  Please wait.")
            self.restorePrevDICOMDB()
            del self.DICOMWidget
            #print(self.browser.utils.lf(), "Finished original DICOM database.")
            self.browser.XNATView.setEnabled(True)



            
    def beginDICOMSession(self):
        """ As stated.
        """
        #print(self.browser.utils.lf(), "DICOMS successfully loaded.")
        sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = self.xnatSrc)
        sessionArgs['sessionType'] = "dicom download"
        self.browser.XNATView.startNewSession(sessionArgs)



        
    def restorePrevDICOMDB(self):
        """ As stated.
        """
        if os.path.exists(self.newDBFile):
            shutil.copy(self.newDBFile, self.prevDBFile)
