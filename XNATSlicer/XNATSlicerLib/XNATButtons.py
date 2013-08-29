from __main__ import vtk, ctk, qt, slicer


import os


from XNATLoadWorkflow import *
from XNATSaveWorkflow import *
from XNATDeleteWorkflow import *



comment = """
  XNATButtons is the class that handles all of the UI interactions to
  call on the various XNATWorkflows.

  author: sunilk@mokacreativellc.com
  
 TODO : 
"""






class XNATButtons(object):
    """ Creates buttons for the GUI and calls respective workflows.
    """


    
    
    def __init__(self, parent = None, browser = None):
        """  Create buttons
        """

        # for inserting in gui
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



    
    def setEnabled(self, buttonKey = None, enabled = True):
        """ Sets a button enabled or disabled as part of QT
        """
        
        if buttonKey:
            self.buttons[buttonKey].setEnabled(enabled)
        else:
            for k,b in self.buttons.iteritems():
                b.setEnabled(enabled)



                
    def generateButton(self, iconFile="", toolTip="", font = qt.QFont('Arial', 10, 10, False),  size =  qt.QSize(30, 30), enabled=False, onclick=''):
        """ Creates an empty button.
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
        """ Starts Delete workflow.
        """  

        deleter = XNATDeleteWorkflow(self.browser)
        deleter.beginWorkflow()



            
    def saveClicked(self):        
        """ Starts Save workflow.
        """     
        
        self.lastButtonClicked = "save" 
        self.browser.XNATView.setEnabled(False)

        saver = XNATSaveWorkflow(self.browser)
        saver.beginWorkflow()



        
    def loadClicked(self):
        """ Starts Load workflow.
        """
        
        self.lastButtonClicked = "load"
        self.browser.XNATView.setEnabled(False)

        loader = XNATLoadWorkflow(self.browser)
        loader.beginWorkflow()


            
          
    def addProjClicked(self):
        """ Adds a project folder to the server.
        """

        self.addProjEditor = XNATAddProjEditor(self, self.browser, self.browser.XNATCommunicator)
        self.addProjEditor.show()
