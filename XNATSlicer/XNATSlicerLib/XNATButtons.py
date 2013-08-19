from __main__ import vtk, ctk, qt, slicer
import os

from DICOMLoader import *
from XNATSaveDialog import *
from XNATSaveWorkflow import *

 
comment = """
  XNATButtons is the class that handles all of the UI interactions to the XNATCommunicator.

# TODO : 
"""


class XNATButtons(object):
    """ Descriptor
    """


    
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
        """ Descriptor
        """
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
        """ Descriptor
        """
        
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

            # Construct the full delete string based on type of tree item deleted
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

            
            # Show the delete dialog
            self.deleteDialog = qt.QMessageBox()
            self.deleteDialog.setIcon(qt.QMessageBox.Warning)
            self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from XNAT?"%(self.browser.XNATView.viewWidget.currentItem().text(self.browser.XNATView.column_name)))   
            self.deleteDialog.connect('buttonClicked(QAbstractButton*)', self.deleteClicked)
            self.deleteDialog.addButton(qt.QMessageBox.Ok)
            self.deleteDialog.addButton(qt.QMessageBox.Cancel)    
            self.deleteDialog.show()



            
    def saveClicked(self):        
        """ Conducts a series of steps (including the file naming workflow) 
            before actually saving the scene.
        """     
        self.lastButtonClicked = "save" 
        self.browser.XNATView.setEnabled(False)


        # If Scene is linked (i.e. the session manager is active)...
        if self.browser.XNATView.sessionManager.sessionArgs:
            self.browser.XNATView.setEnabled(False)
            FileSaveDialog(self.browser, self.browser.XNATView.sessionManager.sessionArgs)
            #self.browser.XNATView.makeRequiredSlicerFolders()
            
         
        # If scene is unlinked
        elif (not self.browser.XNATView.sessionManager.sessionArgs):

            
            # Construct new sessionArgs
            fullPath = self.browser.XNATView.getXNATDir(self.browser.XNATView.getParents(self.browser.XNATView.viewWidget.currentItem()))
            remoteURI = self.browser.settings.getAddress(self.browser.XNATLoginMenu.hostDropdown.currentText) + fullPath
            sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            sessionArgs.printAll()

            
            # Call unlinked dialog
            SaveUnlinkedDialog(self.browser, self, fullPath, sessionArgs)


            
          
    def addProjClicked(self):
        """ Descriptor
        """

        self.addProjEditor = XNATAddProjEditor(self, self.browser, self.browser.XNATCommunicator)
        self.addProjEditor.show()


        

    def beginSaveWorkflow(self, sessionArgs):   
        """ Descriptor
        """         
        
        self.browser.XNATView.currItem = self.browser.XNATView.viewWidget.currentItem()   
        self.browser.XNATView.startNewSession(sessionArgs)
        self.browser.XNATView.makeRequiredSlicerFolders() 
        saveWorkflow = XNATSaveWorkflow(self.browser, self.browser.XNATCommunicator, self.browser.XNATView.sessionManager.sessionArgs)
        saveWorkflow.saveScene()   
        self.browser.XNATButtons.buttons['load'].setEnabled(True)
        self.browser.XNATButtons.buttons['delete'].setEnabled(True) 

        

        
    def loadClicked(self, button = None):
        """ Descriptor
        """
        
        self.lastButtonClicked = "load"
        self.browser.XNATView.setEnabled(False)

        #------------------------
        # Clear Scene
        #------------------------
        if not button and not self.browser.utils.isCurrSceneEmpty():           
            self.browser.XNATView.initClearDialog()
            self.browser.XNATView.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.loadClicked) 
            self.browser.XNATView.clearSceneDialog.show()
            return

            
        #------------------------
        # Begin Workflow
        #------------------------
        if (button and 'yes' in button.text.lower()) or self.browser.utils.isCurrSceneEmpty():
            
            self.browser.XNATView.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)

            currItem = self.browser.XNATView.viewWidget.currentItem()
            pathObj = self.browser.XNATView.getXNATPathObject(currItem)

            
            remoteURI = self.browser.settings.getAddress(self.browser.XNATLoginMenu.hostDropdown.currentText) + '/data' + pathObj['childQueryPaths'][0]
            if '/scans/' in remoteURI and not remoteURI.endswith('/files'):
                remoteURI += '/files'
        
            dst = os.path.join(self.browser.utils.downloadPath, 
                               currItem.text(self.browser.XNATView.column_name))

            print "***********%s %s"%(self.browser.utils.lf(), remoteURI)

            
            #------------------------
            # Determine loader based on currItem
            #------------------------
            loader = None
            if (('files' in remoteURI and 'Slicer' in remoteURI) and remoteURI.endswith(self.browser.utils.defaultPackageExtension)): 
                print "SCENE LOADER SELECTED"
                loader = self.browser.SceneLoader
            elif ('files' in remoteURI and '/scans/' in remoteURI):   
                print "DICOM LOADER SELECTED"     
                loader =  self.browser.DICOMLoader
            else:
                print "FILE LOADER SELECTED"
                loader =  self.browser.FileLoader
                
            args = {"XNATCommunicator": self.browser.XNATCommunicator, 
                    "xnatSrc": remoteURI, 
                    "localDst":dst, 
                    "folderContents": None}
            

            self.browser.downloadPopup.setDownloadFilename(remoteURI)
            self.browser.downloadPopup.show()
            

        
            loadSuccessful = loader.load(args)  
            

            
        #------------------------
        # Enable TreeView
        #------------------------
        self.browser.XNATView.viewWidget.setEnabled(True)
        self.lastButtonClicked = None
    
