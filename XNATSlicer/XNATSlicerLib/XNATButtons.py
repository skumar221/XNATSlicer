from __main__ import vtk, ctk, qt, slicer
import os

 
comment = """
  XNATButtons is the class that handles all of the UI interactions to the XNATCommunicator.

# TODO : 
"""


class XNATButtons(object):
    def __init__(self, parent = None, browser = None):
        
        self.parent = parent
        self.browser = browser

        self.buttons = {}

        self.buttons['load'] = self.generateButton(iconFile = 'load.jpg', 
                                                 toolTip = "Load file, image folder or scene from XNAT to Slicer.", 
                                                 font = self.browser.utils.labelFont,
                                                 size = self.browser.utils.buttonSizeMed, 
                                                 onclick = self.loadClicked,
                                                 enabled = False)
        

        self.buttons['save'] = self.generateButton(iconFile = 'save.jpg', 
                                                 toolTip ="Upload current scene to XNAT.", 
                                                 font = self.browser.utils.labelFont,
                                                 size = self.browser.utils.buttonSizeMed, 
                                                 onclick = self.saveClicked,
                                                 enabled = False)

        self.buttons['delete'] = self.generateButton(iconFile = 'delete.jpg', 
                                                 toolTip = "Delete XNAT file or folder.", 
                                                 font = self.browser.utils.labelFont,
                                                 size = self.browser.utils.buttonSizeSmall, 
                                                 onclick = self.deleteClicked,
                                                 enabled = False)
        
        self.buttons['addProj'] = self.generateButton(iconFile = 'addproj.jpg', 
                                                 toolTip = "Add Project, Subject, or Experiment to XNAT.", 
                                                 font = self.browser.utils.labelFont,
                                                 size = self.browser.utils.buttonSizeSmall, 
                                                 onclick = self.addProjClicked,
                                                 enabled = False)



    
    def setEnabled(self, buttonKey=None, enabled=True):
        if buttonKey:
            self.buttons[buttonKey].setEnabled(True)
        else:
            for k,b in self.buttons.iteritems():
                b.setEnabled(enabled)


    
    def generateButton(self, 
                       iconFile="", 
                       toolTip="", 
                       font = qt.QFont('Arial', 10, 10, False), 
                       size =  qt.QSize(30, 30), 
                       enabled=False, 
                       onclick=''):
        
        button = qt.QPushButton()
        button.setIcon(qt.QIcon(os.path.join(self.browser.utils.iconPath, iconFile)))
        button.setToolTip(toolTip)
        button.setFont(font)
        button.setFixedSize(size)
        button.connect('clicked()', onclick)
        button.setEnabled(enabled)               
        return button



    
    def deleteClicked(self, button=None):
        """ Descriptor
        """  
        if button and button.text.lower().find('ok') > -1: 

            
            #--------------------
            # Construct the full delete string based on type of tree item deleted
            #--------------------
            delStr = self.browser.XNATView.getXNATDir(self.browser.XNATView.getParents(self.browser.XNATView.viewWidget.currentItem()))
            if (('files' in self.browser.XNATView.viewWidget.currentItem().text(self.browser.XNATView.column_category))
                or (self.browser.utils.slicerDirName in self.browser.XNATView.viewWidget.currentItem().text(self.browser.XNATView.column_category))):
                delStr = delStr
            else:
                delStr = os.path.dirname(delStr)
            self.browser.XNATCommunicator.delete(delStr)
            
            # Set currItem to parent and expand it   
            self.browser.XNATView.viewWidget.setCurrentItem(self.browser.XNATView.viewWidget.currentItem().parent())
            self.browser.XNATView.getChildrenExpanded(self.browser.XNATView.viewWidget.currentItem())
        elif button and button.text.lower().find('cancel') > -1:
             return
        else:

            
            #--------------------
            # Show the delete dialog
            #--------------------
            self.deleteDialog = qt.QMessageBox()
            self.deleteDialog.setIcon(qt.QMessageBox.Warning)
            self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from XNAT?"%(self.viewWidget.currentItem().text(self.browser.XNATView.column_name)))   
            self.deleteDialog.connect('buttonClicked(QAbstractButton*)', self.deleteClicked)
            self.deleteDialog.addButton(qt.QMessageBox.Ok)
            self.deleteDialog.addButton(qt.QMessageBox.Cancel)    
            self.deleteDialog.show()



            
    def saveClicked(self):        
        """ Conducts a series of steps (including the file naming workflow) 
            before actually saving the scene.
        """     
        self.lastButtonClicked = "save" 

        
        #--------------------  
        # If Scene is linked (i.e. the session manager is active)...
        #--------------------
        if self.browser.XNATView.sessionManager.sessionArgs:
            self.browser.XNATView.makeRequiredSlicerFolders()
            FileSaveDialog(self.browser, self, self.browser.XNATView.sessionManager.sessionArgs)

            
        #--------------------
        # If scene is unlinked
        #--------------------
        elif (not self.browser.XNATView.sessionManager.sessionArgs):
            # Construct new sessionArgs
            fullPath = self.browser.XNATView.getXNATDir(self.browser.XNATView.getParents(self.browser.XNATView.viewWidget.currentItem()))
            remoteURI = self.browser.settings.getAddress(self.browser.hostDropdown.currentText) + fullPath
            sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            sessionArgs.printAll()
            # Call unlinked dialog
            SaveUnlinkedDialog(self.browser, self, fullPath, sessionArgs)


            
    def addProjClicked(self):
        self.addProjEditor = XNATAddProjEditor(self, self.browser, self.browser.XNATCommunicator)
        self.addProjEditor.show()



    def beginSaveWorkflow(self, sessionArgs):            
        self.browser.XNATView.currItem = self.browser.XNATView.viewWidget.currentItem()   
        self.browser.XNATView.startNewSession(sessionArgs)
        self.browser.XNATView.makeRequiredSlicerFolders() 
        saveWorkflow = XNATSaveWorkflow(self.browser, self.browser.XNATCommunicator, self.browser.XNATView.sessionManager.sessionArgs)
        saveWorkflow.saveScene()   


        
    def loadClicked(self, button = None):
        
        self.lastButtonClicked = "load"


        #------------------------
        # Clear Scene
        #------------------------
        if not button:
            if not self.browser.utils.isCurrSceneEmpty():           
                self.initClearDialog()
                self.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.loadClicked) 
                self.clearSceneDialog.show()
                return

            
        #------------------------
        # Begin Workflow
        #------------------------
        if (button and button.text.lower().find('yes') > -1) or self.browser.utils.isCurrSceneEmpty():
            self.browser.XNATView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)
            currItem = self.browser.XNATView.viewWidget.currentItem()
            parents= self.browser.XNATView.getParents(currItem)
            fullPath = self.browser.XNATView.getXNATDir(self.browser.XNATView.getParents(currItem))
            remoteURI = self.browser.settings.getAddress(self.browser.hostDropdown.currentText) + fullPath
            dst = os.path.join(self.browser.utils.downloadPath, currItem.text(self.browser.XNATView.column_name))
            # determine loader based on currItem
            loader = None
            if (('files' in currItem.text(self.browser.XNATView.column_category)) or 
                (self.browser.utils.slicerDirName in currItem.text(self.browser.XNATView.column_category))):
                if (currItem.text(self.browser.XNATView.column_name).endswith(self.browser.utils.defaultPackageExtension)): 
                    loader = SceneLoader(self.browser)
                else:
                    loader = FileLoader(self.browser)
            else:
                loader = DICOMLoader(self.browser)
            args = {"XNATCommunicator": self.browser.XNATCommunicator, 
                    "xnatSrc":fullPath, 
                    "localDst":dst, 
                    "folderContents": None}
            loadSuccessful = loader.load(args)  

            
        #------------------------
        # Enable TreeView
        #------------------------
        self.browser.XNATView.viewWidget.setEnabled(True)
        self.lastButtonClicked = None
    
