from __main__ import vtk, ctk, qt, slicer

import os

from XnatLoadWorkflow import *
from XnatSaveWorkflow import *
from XnatDeleteWorkflow import *
import XnatButtonsUI



comment = """
XnatButtons is the class that handles all of the buttons 
(and thier events)  to call on the various 
XnatWorkflows and filters.  This includes 'load/download', 
'delete', 'save/upload', 'create folder' and 'filter' UI elements.
It utilizes the UI file 'XnatButtonsUI' to generate the QT Widgets
that are used for the buttons.

TODO : 
"""



class XnatButtons(object):
    """ Creates buttons for the GUI and calls respective workflows.
    """
    
    def __init__(self, parent = None, MODULE = None):
        """  Create buttons
        """

        #--------------------
        # Public vars.
        #--------------------
        self.parent = parent
        self.MODULE = MODULE


        #--------------------
        # Buttons dictionary...for use by 
        # other classes.
        #--------------------
        self.buttons = {}


        
        #--------------------
        # IO Buttons (Save, Load, Delete, Add Project)
        #--------------------
        self.buttons['io'] = {}
        self.buttons['io'] = XnatButtonsUI.makeButtons_io(self)



        #--------------------
        # IO Button onClicks
        #--------------------
        self.buttons['io']['load'].connect('clicked()', self.onLoadClicked)
        self.buttons['io']['save'].connect('clicked()', self.onSaveClicked)
        self.buttons['io']['delete'].connect('clicked()', self.onDeleteClicked)
        self.buttons['io']['addProj'].connect('clicked()', self.onAddProjectClicked)


        
        #--------------------
        # Filter Buttons
        #--------------------
        self.buttons['filter'] = {}
        self.buttons['filter'] = XnatButtonsUI.makeButtons_filter(self, ['accessed'])


        
        #--------------------
        # Filter Button onClicks
        #--------------------
        self.currentlyToggledFilterButton = None
        for key in self.buttons['filter']:
            self.buttons['filter'][key].connect('clicked()', self.onFilterButtonClicked)


            
        #--------------------
        # Testing button
        #--------------------
        self.buttons['io']['test'].connect('clicked(boolean*)', self.onTestClicked)
        self.setEnabled('test', True)



        
    def setEnabled(self, buttonKey = None, enabled = True):
        """ Sets a button enabled or disabled as part of QT
        """
        
        #--------------------
        # If button is specified, apply 'setEnambed' to 
        # it.
        #--------------------
        if buttonKey:
            self.buttons['io'][buttonKey].setEnabled(enabled)



        #--------------------
        # Otherwise apply 'setEnabled' to all buttons.
        #--------------------
        else:
            for k,b in self.buttons.iteritems():
                b.setEnabled(enabled)

                


    
    def onDeleteClicked(self, button=None):
        """ Starts Delete workflow.
        """  

        deleter = XnatDeleteWorkflow(self.MODULE)
        deleter.beginWorkflow()



            
    def onSaveClicked(self):        
        """ Starts Save workflow.
        """     
        
        self.lastButtonClicked = "save" 
        self.MODULE.XnatView.setEnabled(False)
        saver = XnatSaveWorkflow(self.MODULE)
        saver.beginWorkflow()


        

    def onTestClicked(self):        
        """ Starts Save workflow.
        """     
        self.lastButtonClicked = "test" 
        self.MODULE.XnatView.setEnabled(True)
        self.MODULE.tester.runTest()


        
        
    def onLoadClicked(self):
        """ Starts Load workflow.
        """
        
        self.lastButtonClicked = "load"
        self.MODULE.XnatView.setEnabled(False)
        loader = XnatLoadWorkflow(self.MODULE)
        loader.beginWorkflow()


            
          
    def onAddProjectClicked(self):
        """ Adds a project folder to the server.
        """

        self.addProjEditor = XnatAddProjEditor(self, self.MODULE, self.MODULE.XnatIo)
        self.addProjEditor.show()



        
    def setButtonDown(self, category = None, name = None, isDown = True, callSignals = True):
        """ Programmatically sets a button down based on
            the arguments.  The user has the option to allow for
            the 'clicked()' signals to be called or not.  
            This is used primarily for default programmatic 
            manipulation of the buttons, such as loadProjects() in 
            XNATTreeView, where default filters are applied, but
            the signals of clicking are not desired, but 
            self.currentlyToggledFilterButton is still tracked.
        """
        if isDown and category == 'filter':
            self.buttons[category][name].setChecked(True)
            self.currentlyToggledFilterButton = self.buttons['filter'][name]


            

    def onFilterButtonClicked(self):
        """ As stated.  Handles the toggling of filter
            buttons relative to one another. O(4n).
        """

        #-----------------
        # Count down buttons
        #------------------
        checkedButtons = 0
        buttonLength = len(self.buttons['filter'])
        for key in self.buttons['filter']:
           currButton = self.buttons['filter'][key]
           if currButton.isChecked():
               checkedButtons += 1

               
               
        #-----------------
        # If there are no down buttons, apply the ['all']
        # filter and return.
        #------------------
        if checkedButtons == 0:
            for key in self.buttons['filter']:
                self.buttons['filter'][key].setDown(False)
                self.buttons['filter'][key].setChecked(False)
            self.currentlyToggledFilterButton = ''
            self.MODULE.XnatView.loadProjects(['all'])
            return
 

        
        #-----------------
        # If a new button has been clicked
        # then set it as the self.currentlyToggledFilterButton. 
        #------------------
        for key in self.buttons['filter']:
            currButton = self.buttons['filter'][key]
            if currButton.isChecked() and self.currentlyToggledFilterButton != currButton:
                self.currentlyToggledFilterButton = currButton
                break

            
                
        #-----------------
        # Un-toggle previously toggled buttons.
        #-----------------
        for key in self.buttons['filter']:
            currButton = self.buttons['filter'][key]
            if currButton.isChecked() and self.currentlyToggledFilterButton != currButton:
                currButton.setDown(False)

                

        #-----------------
        # Apply method
        #------------------
        for key in self.buttons['filter']:
            if self.currentlyToggledFilterButton == self.buttons['filter'][key]:
                self.MODULE.XnatView.loadProjects([self.currentlyToggledFilterButton.text.lower()])
