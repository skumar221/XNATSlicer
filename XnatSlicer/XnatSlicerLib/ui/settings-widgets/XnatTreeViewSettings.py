from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettings import *
from XnatMetadataManager import *



comment = """
XnatTreeViewSettings

TODO:
"""




#--------------------
# Define the info metadata tags for storing into 
# the settings file
#--------------------
infoMetadataTags = {'projects': '', 'subjects' : '', 'experiments' : '', 'scans' :'', 'files' : '', 'slicer': ''}
for key in infoMetadataTags:
    infoMetadataTags[key] = 'infoMetadataTags_' + key


    
        
class XnatTreeViewSettings(XnatSettings):
    """ Embedded within the settings popup.  Manages hosts.
    """
  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatTreeViewSettings, self).__init__(title, MODULE)

            
        
        #--------------------
        # Add Sort Buttons section
        #--------------------
        self.addSortAndFilterButtons()
        self.addSpacing()


        
        #--------------------
        # Add font dropdown
        #--------------------
        self.addFontDropdown("Tree View Font Size:")
        self.addSpacing()

        

        #--------------------
        # Add the metadata Manager
        #--------------------        
        self.addMetadataManager()
        self.complete()


        
        
      
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
          if isDown and category == 'sort':
              self.buttons[category][name].setChecked(True)
              self.currentlyToggledFilterButton = self.buttons['sort'][name]




    def addFontDropdown(self, title = "Font Size:" ):
        """
        """
        super(XnatTreeViewSettings, self).addFontDropdown(title)

        self.fontSizeTag = "TreeViewFontSize"
        
        xnatHost = self.MODULE.XnatMetadataSettings.hostDropdown.currentText
        font = self.MODULE.XnatSettingsFile.getTagValues(xnatHost, self.fontSizeTag)


        if len(font) == 0:
            currSize = self.MODULE.GLOBALS.FONT_SIZE
            self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(currSize)]})
        else:
            currSize = font[0]
        
        def changeFontSize(size):
            try:
                self.MODULE.XnatView.changeFontSize(int(size))
                self.MODULE.XnatSettingsFile.setTagValues(xnatHost, {self.fontSizeTag: [str(size)]})
            except Exception, e:
                #print self.MODULE.utils.lf(), str(e)
                pass

        currDropdown = self.fontDropdowns[-1]
        currDropdown.connect('currentIndexChanged(const QString&)', changeFontSize)
        currDropdown.setCurrentIndex(currDropdown.findText(currSize))

        


    def addMetadataManager(self):
        """
        """
        #--------------------
        # Set the metadata manager type.
        #--------------------        
        self.setMetadataManagers('info')        
        self.addSection("Info. Column Metadata", self.XnatMetadataManagers['info'])

        
        self.setDefaultSelectedMetadata('info',  {
            'projects' : [
                'last_accessed_497',
                ],
                
            'subjects' : [
                'label',
                ],
                    
            'experiments' : [
                'date',
                ],
                        
            'scans' : [
                'series_description',
                'type',
                'quality',
                ],
                                                                          
            'resources' : [
                'element_name',
                ],
                                                                                              
            'files' : [
                'Size',
                ],
                                                                                                    
            'slicer' : [
                'Size',
                ]
                
        })


        
        for key, manager in self.XnatMetadataManagers.iteritems():
            manager.setCustomEditVisible(False)
            manager.setItemType('checkbox')


            


    def addSortAndFilterButtons(self):
        """
        """
        #--------------------
        # Create buttons
        #--------------------
        self.buttons = {}
        self.buttons['sort'] = {}
        self.buttons['sort'] = {'accessed': self.MODULE.utils.generateButton(iconOrLabel = 'Last Accessed', 
                                                                               toolTip = "Sort projects, prioritizing those accessed by current user.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(90, 20), 
                                                                               enabled = True)}

        
        #--------------------
        # Connect the filter button
        #--------------------
        self.buttons['sort']['accessed'].setCheckable(True)
        self.buttons['sort']['accessed'].setChecked(False)
        def accessedToggled(toggled):
            if toggled:
                self.MODULE.XnatView.filter_accessed()
            else:
                self.MODULE.XnatView.filter_all()
        
        self.buttons['sort']['accessed'].connect('toggled(bool)', accessedToggled)

        #--------------------
        # Make the button layout
        #--------------------
        self.sortButtonLayout = qt.QHBoxLayout()
        for key, value in self.buttons['sort'].iteritems():
            self.sortButtonLayout.addWidget(value)
        self.sortButtonLayout.addStretch()


        #--------------------
        # Create a "Filter Projects By" section.
        #--------------------
        self.addSection("Filter Projects By:", self.sortButtonLayout)
