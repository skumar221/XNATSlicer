from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil

from XNATFileInfo import *
from XNATUtils import *
from XNATScenePackager import *
from XNATSessionManager import *
from XNATTimer import *



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



class XNATSaveDialog(object):
    """ Parent class of all of the save dialogs.
    """



    
    def __init__(self, browser):
        """ Descriptor
        """

        self.browser = browser
        self.dialogs = []        

        self.setup()
        self.begin()         



        
    def begin(self):
        """ Descriptor
        """
        
        print "%s"%(self.browser.utils.lf())

        
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


    


    
class SaveEmptyDialog(XNATSaveDialog):
    
     def __init__(self, browser, viewer):

         
         # Call parent
         super(saveemptydialog, self).__init__(browser, viewer)



         
     def setup(self):

         
         # dialog setup
         self.setnumdialogs(1)
         self.dialogs[0].settext('the slicer scene appears to be empty. ' + 
                                 'are you sure you want to continue?')      
         
         # Button Setup
         self.dialogs[0].addButton(qt.QMessageBox.Ok)
         self.dialogs[0].addButton(qt.QMessageBox.Cancel)


         
         
     def buttonClicked(self,button):

         
        # if ok button clicked
        if button.text.lower().find('ok') > -1: 

            # re-call viewer.save with updated params
            self.browser.xnatview.savebuttonclicked(excluderoutines = ['empty'])


            


            
class saveunlinkeddialog(xnatsavedialog):


    
     def __init__(self, browser, viewer, savepath, sessionargs):
         
        # call parent
        self.sessionargs = sessionargs
        super(saveunlinkeddialog, self).__init__(browser, viewer)


        
       
     def setup(self):

         
         # dialog setup
         self.setnumdialogs(1)
         msg = """the scene doesn't appear to be associated with a specific xnat location.  
                  would you like to save it within this xnat """
        
         msg = "%s %s (%s)?" %(msg, self.browser.utils.defaultxnatsavelevel[:-1], os.path.basename(self.sessionargs['savelevel']))
         msg.replace('location', self.browser.utils.defaultxnatsavelevel[:-1])
         
         self.dialogs[0].settext(msg)      

         
         # button setup
         self.dialogs[0].addbutton(qt.qmessagebox.yes)
         self.dialogs[0].addbutton(qt.qmessagebox.cancel)
         self.browser.xnatview.selectitem_bypath((self.sessionargs['savelevel']))



         
     def buttonclicked(self,button):

         
        # If ok button clicked
        if button.text.lower().find('yes') > -1: 

            
            # Re-call viewer.save with updated params
            FileSaveDialog(self.browser, self.sessionArgs)


            


            
class FileSaveDialog(XNATSaveDialog):  
""" Descriptor
"""

    
    def __init__(self, browser, sessionargs):
        """ Descriptor
        """

        # determine filename
        self.filename = none


        # Init params
        self.sessionargs = sessionargs


        # Dialog setup
        self.inputindex = 0  
        self.noticelabel = qt.qlabel("")
        self.savesharablecb = none

        # Call parent
        super(FileSaveDialog, self).__init__(browser)

        print "%s"%(self.browser.utils.lf())
        return



    
    def setup(self):     
        
        print "%s"%(self.browser.utils.lf())


        # Window setup   
        self.setnumdialogs(1, {'0':qt.qdialog(slicer.util.mainwindow())}) 
        self.dialogs[0].setfixedwidth(600)   

        
        # Labeling
        self.saveButtonStr = "Save"
        fileLineLabel = qt.QLabel("Filename: ")


        # Set fileline text
        self.fileLine = qt.QLineEdit(self.sessionArgs['fileName'].split(self.browser.utils.defaultPackageExtension)[0])

        
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
        bottomrow = qt.qhboxlayout()
        #bottomrow.addwidget(self.savesharablecb)
        bottomrow.addwidget(buttonrow)

        

        # apply layouts
        dialoglayout.addlayout(fileinputlayout)
        dialoglayout.addwidget(self.noticelabel)
        dialoglayout.addlayout(bottomrow)
        self.dialogs[0].setlayout(dialoglayout)


        
        # button connect  
        buttonRow.connect('clicked(QAbstractButton*)', self.buttonClicked)
        self.browser.XNATView.selectItem_byPath((self.sessionArgs['saveLevel']))



            
    def buttonClicked(self,button):
        """ Descriptor
        """
        slicer.app.processEvents()
        self.dialogs[0].hide()         

        
        # Filename from textline
        self.sessionArgs['fileName'] = self.browser.utils.replaceForbiddenChars(self.fileLine.text.split(".")[0], "_")
        self.sessionArgs['fileName'] += self.browser.utils.defaultPackageExtension

        
        if button.text.lower().find((self.saveButtonStr).lower()) > -1:                       
            self.sessionArgs['sharable'] = False      
            self.browser.XNATButtons.beginSaveWorkflow(self.sessionArgs)  
