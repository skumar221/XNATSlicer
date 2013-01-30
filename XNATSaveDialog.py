from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil

from XNATFileInfo import *
from XNATMRMLParser import *
from XNATUtils import *
from XNATScenePackager import *
from XNATSessionManager import *
from XNATTimer import *



################################################################################
comment = """
            XNATSaveDialog is a class that manages various 
            dialogs related to saving XNAT files.
            
            There is a parent class called XNATSaveDialog.
            
            The classes that inherit from it are:
            1) LocalSceneDialog 
                (For saving a scene that was locally loaded.)
            
            2) Save Empty Dialog
                (For saving a scene that appears empty.)
                
            3) FileSaveDialog
                (Where user enters filename, amongst other
                things.)
          """
#################################################################################



#################################################################################
#################################################################################
#################################################################################
class XNATSaveDialog(object):
    """ Parent class of all of the save dialogs.
    """
    
    def __init__(self, browser, viewer):
        #=======================================================================
        # INIT PARAMS
        #=======================================================================
        self.browser = browser
        self.viewer = viewer
        self.utils = XNATUtils()
        #=======================================================================
        # DIALOG WINDOW LIST
        #=======================================================================
        self.dialogs = []        
        #=======================================================================
        # CALL SETUP FUNCTIONS -- USUALLY TO CHILD
        #=======================================================================
        self.setup()
       
        #=======================================================================
        # SHOW FIRST WINDOW
        #=======================================================================
        self.begin()         
        
    def begin(self):
        #=======================================================================
        # SHOW FIRST WINDOW
        #=======================================================================
        self.dialogs[0].show()
        
        #=======================================================================
        # ADJUST POSITION
        #=======================================================================
        mainWindow = slicer.util.mainWindow()
        screenMainPos = mainWindow.pos
        x = screenMainPos.x() + 400
        y = screenMainPos.y() + 400
        self.dialogs[0].move(qt.QPoint(x,y))     
        
    def okClicked(self):
        pass
    
    def yesClicked(self):
        pass
    
    def noClicked(self):
        pass
        
    def cancelClicked(self):
        for dialog in self.dialogs: dialog.hide()
        return
       
    def setNumDialogs(self, numDialogs = 1, dialogType = None):
        for x in range(0, numDialogs):
            try:
                #===============================================================
                # SET DIALOG BASED ON TYPE
                #===============================================================
                self.dialogs.append(dialogType[str(x)])              
            except Exception, e:
                #===============================================================
                # SET DEFAULT DIALOG TYPE
                #===============================================================
                print "EXCEPTION: SET NUM DIALOGS: " + str(e)
                self.dialogs.append(qt.QMessageBox())   
                self.dialogs[x].connect('buttonClicked(QAbstractButton*)', 
                                        self.buttonClicked)
                self.dialogs[x].setTextFormat(1)
         
    def buttonClicked(self):
        pass

class SaveEmptyDialog(XNATSaveDialog):
    
     def __init__(self, browser, viewer):
         #======================================================================
         # CALL PARENT
         #======================================================================
         super(SaveEmptyDialog, self).__init__(browser, viewer)
       
     def setup(self):
         #======================================================================
         # DIALOG SETUP
         #======================================================================
         self.setNumDialogs(1)
         self.dialogs[0].setText('The Slicer scene appears to be empty. ' + 
                                 'Are you sure you want to continue?')      
         #======================================================================
         # BUTTON SETUP
         #======================================================================
         self.dialogs[0].addButton(qt.QMessageBox.Ok)
         self.dialogs[0].addButton(qt.QMessageBox.Cancel)
             
     def buttonClicked(self,button):
        #=======================================================================
        # IF OK BUTTON CLICKED
        #=======================================================================
        if button.text.lower().find('ok') > -1: 
            #===================================================================
            # RE-CALL viewer.save WITH UPDATED PARAMS
            #===================================================================
            self.viewer.saveButtonClicked(excludeRoutines = ['empty'])
            
class SaveUnlinkedDialog(XNATSaveDialog):
    
     def __init__(self, browser, viewer, savePath, sessionArgs):
         #======================================================================
         # CALL PARENT
         #======================================================================
         self.sessionArgs = sessionArgs
         super(SaveUnlinkedDialog, self).__init__(browser, viewer)
         
       
     def setup(self):
         #======================================================================
         # DIALOG SETUP
         #======================================================================
         self.setNumDialogs(1)
         msg = """The scene doesn't appear to be associated with a specific XNAT location.  
                  Would you like to save it within this XNAT """
        
         msg = "%s %s (%s)?" %(msg, self.utils.defaultXNATSaveLevel[:-1], os.path.basename(self.sessionArgs['saveLevel']))
         msg.replace('location', self.utils.defaultXNATSaveLevel[:-1])
         
         self.dialogs[0].setText(msg)      
         #======================================================================
         # BUTTON SETUP
         #======================================================================
         self.dialogs[0].addButton(qt.QMessageBox.Yes)
         self.dialogs[0].addButton(qt.QMessageBox.Cancel)
         self.viewer.viewWidget.setCurrentItem(self.viewer.getItem_byPath(self.sessionArgs['saveLevel']))
             
     def buttonClicked(self,button):
        #=======================================================================
        # IF OK BUTTON CLICKED
        #=======================================================================
        if button.text.lower().find('yes') > -1: 
            #===================================================================
            # RE-CALL viewer.save WITH UPDATED PARAMS
            #===================================================================
            FileSaveDialog(self.browser, self.viewer, self.sessionArgs)

class FileSaveDialog(XNATSaveDialog):  
    def __init__(self, browser, viewer, sessionArgs):
        #=======================================================================
        # DETERMINE FILENAME
        #=======================================================================
        self.fileName = None
        #=======================================================================
        # INIT PARAMS
        #=======================================================================
        self.sessionArgs = sessionArgs
        #=======================================================================
        # DIALOG SETUP
        #=======================================================================
        self.inputIndex = 0  
        self.noticeLabel = qt.QLabel("")
        self.saveSharableCB = None
        #=======================================================================
        # CALL PARENT
        #=======================================================================
        super(FileSaveDialog, self).__init__(browser, viewer)
        return
    
    def setup(self):     
        #=======================================================================
        # WINDOW SETUP   
        #=======================================================================
        self.setNumDialogs(1, {'0':qt.QDialog(slicer.util.mainWindow())}) 
        self.dialogs[0].setFixedWidth(600)     
        #=======================================================================
        # LABELING
        #=======================================================================
        self.saveButtonStr = "Save"
        fileLineLabel = qt.QLabel("Filename: ")
        #=======================================================================
        # SET FILELINE TEXT
        #=======================================================================  
        self.fileLine = qt.QLineEdit(self.sessionArgs['fileName'].split(self.utils.defaultPackageExtension)[0])
        #=======================================================================
        # DISPLAY NOTICES  
        #=======================================================================
#        if self.originFileName:
#            newText = ".(Please note, the selected scene <b>'%s'</b> is different from the one loaded--<b>'%s'</b>.)"%(self.fileName, self.originFileName) 
#            self.fileLine = qt.QLineEdit(self.originFileName.split(".")[0])    
        #=======================================================================
        # FILENAME LINE
        #=======================================================================
        fileInputLayout = qt.QHBoxLayout()
        fileInputLayout.addWidget(fileLineLabel)
        fileInputLayout.addWidget(self.fileLine)
        dialogLayout = qt.QVBoxLayout()
        #=======================================================================
        # BUTTONS
        #=======================================================================
        saveButton = qt.QPushButton()
        saveButton.setText(self.saveButtonStr)
        cancelButton = qt.QPushButton()
        cancelButton.setText("Cancel")
        buttonRow = qt.QDialogButtonBox()
        buttonRow.addButton(saveButton, 0)
        buttonRow.addButton(cancelButton, 2)               
        #=======================================================================
        # CHECK BOX
        #=======================================================================
        self.saveSharableCB = qt.QCheckBox('Make nodes sharable (experimental/coming soon)')
        self.saveSharableCB.setEnabled(False)     
        if self.sessionArgs['sharable']: 
            self.saveSharableCB.setCheckState(2)
        #=======================================================================
        # BOTTOM ROW        
        #=======================================================================
        bottomRow = qt.QHBoxLayout()
        #bottomRow.addWidget(self.saveSharableCB)
        bottomRow.addWidget(buttonRow)
        #=======================================================================
        # APPLY LAYOUTS
        #=======================================================================
        dialogLayout.addLayout(fileInputLayout)
        dialogLayout.addWidget(self.noticeLabel)
        dialogLayout.addLayout(bottomRow)
        self.dialogs[0].setLayout(dialogLayout)
        #=======================================================================
        # BUTTON CONNECT
        #=======================================================================
        buttonRow.connect('clicked(QAbstractButton*)', self.buttonClicked)
        self.viewer.viewWidget.setCurrentItem(self.viewer.getItem_byPath(self.sessionArgs['saveLevel']))
 
    def buttonClicked(self,button):
        slicer.app.processEvents()
        self.dialogs[0].hide()                  
        # FILENAME FROM TEXTLINE
        self.sessionArgs['fileName'] = self.utils.replaceForbiddenChars(self.fileLine.text.split(".")[0], "_")
        self.sessionArgs['fileName'] += self.utils.defaultPackageExtension
        if button.text.lower().find((self.saveButtonStr).lower()) > -1:                       
            self.sessionArgs['sharable'] = False      
            self.viewer.beginSaveWorkflow(self.sessionArgs)  
