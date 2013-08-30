from __main__ import vtk, ctk, qt, slicer


import os


from XnatLoadWorkflow import *
from XnatSaveWorkflow import *
from XnatDeleteWorkflow import *
import XnatButtonsUI



comment = """
  XnatButtons is the class that handles all of the UI interactions to
  call on the various XnatWorkflows.
  
 TODO : 
"""






class XnatButtons(object):
    """ Creates buttons for the GUI and calls respective workflows.
    """


    
    
    def __init__(self, parent = None, browser = None):
        """  Create buttons
        """

        # for inserting in gui
        self.parent = parent
        self.browser = browser

        # Make buttons from ButtonsUI
        self.buttons = XnatButtonsUI.makeButtons(self)

        # Set button ui
        self.buttons['load'].connect('clicked()', self.loadClicked)
        self.buttons['save'].connect('clicked()', self.saveClicked)
        self.buttons['delete'].connect('clicked()', self.deleteClicked)
        self.buttons['addProj'].connect('clicked()', self.addProjClicked)



        
    def setEnabled(self, buttonKey = None, enabled = True):
        """ Sets a button enabled or disabled as part of QT
        """
        
        if buttonKey:
            self.buttons[buttonKey].setEnabled(enabled)
        else:
            for k,b in self.buttons.iteritems():
                b.setEnabled(enabled)


    
    def deleteClicked(self, button=None):
        """ Starts Delete workflow.
        """  

        deleter = XnatDeleteWorkflow(self.browser)
        deleter.beginWorkflow()



            
    def saveClicked(self):        
        """ Starts Save workflow.
        """     
        
        self.lastButtonClicked = "save" 
        self.browser.XnatView.setEnabled(False)

        saver = XnatSaveWorkflow(self.browser)
        saver.beginWorkflow()



        
    def loadClicked(self):
        """ Starts Load workflow.
        """
        
        self.lastButtonClicked = "load"
        self.browser.XnatView.setEnabled(False)

        loader = XnatLoadWorkflow(self.browser)
        loader.beginWorkflow()


            
          
    def addProjClicked(self):
        """ Adds a project folder to the server.
        """

        self.addProjEditor = XnatAddProjEditor(self, self.browser, self.browser.XnatCommunicator)
        self.addProjEditor.show()
