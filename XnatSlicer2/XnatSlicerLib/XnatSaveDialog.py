from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil

from XnatFileInfo import *
from XnatUtils import *
from XnatScenePackager import *
from XnatSessionManager import *
from XnatTimer import *



comment = """
            XnatSaveDialog is a class that manages various 
            dialogs related to saving Xnat files.
            
            There is a parent class called XnatSaveDialog.
            
            The classes that inherit from it are:
            1) LocalSceneDialog 
                (For saving a scene that was locally loaded.)
            
            2) Save Empty Dialog
                (For saving a scene that appears empty.)
                
            3) FileSaveDialog
                (Where user enters filename, amongst other
                things.)
"""






class XnatSaveDialog(object):
    """ Parent class of all of the save dialogs.
    """



    
    def __init__(self, browser, saveWorkflow):
        """ Descriptor
        """

        self.browser = browser
        self.dialogs = []        

        self.setup()
        self.begin()         

        self.saveWorkflow = saveWorkflow;

        
    def begin(self):
        """ Descriptor
        """
        
        #print "%s"%(self.browser.utils.lf())

        
        # Show first window
        self.dialogs[0].show()
        

        # Adjust position
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
                
                # Set dialog based on type
                self.dialogs.append(dialogType[str(x)])      
                        
            except Exception, e:

                # Set default dialog type
                print "EXCEPTION: SET NUM DIALOGS: " + str(e)
                self.dialogs.append(qt.QMessageBox())   
                self.dialogs[x].connect('buttonClicked(QAbstractButton*)', 
                                        self.buttonClicked)
                self.dialogs[x].setTextFormat(1)



                
    def buttonClicked(self):
        pass

        



class SaveUnlinkedDialog(XnatSaveDialog):
     """ Descriptor
     """



     
     def __init__(self, browser, saveWorkflow):
        """ Descriptor
        """
        # call parent
        super(saveUnlinkedDialog, self).__init__(browser, saveWorkflow)


        
       
     def setup(self):
         """ Descriptor
         """
         
         # dialog setup
         self.setNumDialogs(1)
         msg = """the scene doesn't appear to be associated with a specific xnat location.  Would you like to save it within this xnat """
         msg = "%s %s (%s)?" %(msg, self.browser.utils.defaultXnatSaveLevel[:-1], os.path.basename(self.browser.XnatView.sessionManager.sessionArgs['savelevel']))
         msg.replace('location', self.browser.utils.defaultXnatSaveLevel[:-1])
         
         
         self.dialogs[0].setText(msg)      
         
         
         # button setup
         self.dialogs[0].addButton(qt.QMessageBox.yes)
         self.dialogs[0].addButton(qt.QMessageBox.cancel)
         self.browser.XNAView.selectItem_byPath((self.browser.XnatView.sessionManager.sessionArgs['savelevel']))



         
     def buttonclicked(self,button):
        """ Descriptor
        """
         
        # If ok button clicked
        if button.text.lower().find('yes') > -1: 

            
            # Re-call viewer.save with updated params
            FileSaveDialog(self.browser, self.browser.XnatView.sessionManager.sessionArgs)


            


            
class FileSaveDialog(XnatSaveDialog):  
    """ Descriptor
    """

    
    
    def __init__(self, browser, saveWorkflow):
        """ Descriptor
        """

        # determine filename
        self.fileName = None

        
        # Dialog setup
        self.inputIndex = 0  
        self.noticeLabel = qt.QLabel("")


        # Call parent
        super(FileSaveDialog, self).__init__(browser, saveWorkflow)

        #print "%s"%(self.browser.utils.lf())
        return



    
    def setup(self):     
        """ Descriptor
        """        
        #print "%s"%(self.browser.utils.lf())


        # Window setup   
        self.setNumDialogs(1, {'0':qt.QDialog(slicer.util.mainWindow())}) 
        self.dialogs[0].setFixedWidth(600)   

        
        # Labeling
        self.saveButtonStr = "Save"
        fileLineLabel = qt.QLabel("Filename: ")


        # Set fileline text
        self.fileLine = qt.QLineEdit(self.browser.XnatView.sessionManager.sessionArgs['fileName'].split(self.browser.utils.defaultPackageExtension)[0])

        
        # DISPLAY NOTICES  
        #        if self.originFileName:
        #            newText = ".(Please note, the selected scene <b>'%s'</b> is different from the one loaded--<b>'%s'</b>.)"%(self.fileName, self.originFileName) 
        #            self.fileLine = qt.QLineEdit(self.originFileName.split(".")[0])    

        
        # Filename line
        fileInputLayout = qt.QHBoxLayout()
        fileInputLayout.addWidget(fileLineLabel)
        fileInputLayout.addWidget(self.fileLine)
        dialogLayout = qt.QVBoxLayout()
     

        # Buttons
        saveButton = qt.QPushButton()
        saveButton.setText(self.saveButtonStr)
        cancelButton = qt.QPushButton()
        cancelButton.setText("Cancel")
        buttonRow = qt.QDialogButtonBox()
        buttonRow.addButton(saveButton, 0)
        buttonRow.addButton(cancelButton, 2)               
        
  
        # Bottom row        
        bottomRow = qt.QHBoxLayout()
        bottomRow.addWidget(buttonRow)

        
        # apply layouts
        dialogLayout.addLayout(fileInputLayout)
        dialogLayout.addWidget(self.noticeLabel)
        dialogLayout.addLayout(bottomRow)
        self.dialogs[0].setLayout(dialogLayout)


        # button connect  
        buttonRow.connect('clicked(QAbstractButton*)', self.buttonClicked)
        self.browser.XnatView.selectItem_byPath((self.browser.XnatView.sessionManager.sessionArgs['saveLevel']))



            
    def buttonClicked(self,button):
        """ Descriptor
        """
        
        slicer.app.processEvents()
        self.dialogs[0].hide()         

        
        # Filename from textline
        self.browser.XnatView.sessionManager.sessionArgs['fileName'] = self.browser.utils.replaceForbiddenChars(self.fileLine.text.split(".")[0], "_")
        self.browser.XnatView.sessionManager.sessionArgs['fileName'] += self.browser.utils.defaultPackageExtension


        # If 'yes' or 'ok' to save
        if self.saveButtonStr.lower() in button.text.lower():                       
            self.browser.XnatView.sessionManager.sessionArgs['sharable'] = False       

            
            # Pre-save
            self.browser.XnatView.startNewSession(self.browser.XnatView.sessionManager.sessionArgs)
            self.browser.XnatView.makeRequiredSlicerFolders() 

            
            # Save to Xnat         
            self.saveWorkflow.saveScene()   

            
            # UI config
            self.browser.XnatButtons.buttons['load'].setEnabled(True)
            self.browser.XnatButtons.buttons['delete'].setEnabled(True) 

            
        # Otherwise reenable everything
        else:
            self.browser.XnatView.setEnabled(True)
            
