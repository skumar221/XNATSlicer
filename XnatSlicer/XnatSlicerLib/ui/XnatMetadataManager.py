from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from AnimatedCollapsible import *
from XnatMetadataEditor import *




comment = """
XnatMetadataManager is a class that combines several 
XnatMetadtaEditors and AnimatedCollapsibles to 
allow for editing of metadata for the XNAT Folder levels outlined
in 'XnatGlobals.XNAT_LEVELS' (usually 'projects', 
'subjects', 'experiments','scans', etc.).

Usually, there are two XnatMetadataEditors for every
AnimatedCollapsible: XnatDefaultMetadataEditor and an
XnatCustomMetadataEditor.  Each editor can be tailored
even further depending on the class that utilizes the
XnatMetadataEditor.

TODO:
"""



        
class XnatMetadataManager(qt.QFrame):
    """ Class described above.
    """

    def __init__(self, MODULE):
        """ Init function.
        """

        super(XnatMetadataManager, self).__init__(self)


        
        #--------------------
        # Track the MODULE.
        #--------------------
        self.MODULE = MODULE



        #--------------------
        # Track all widgets.
        #--------------------
        self.collapsibles = {}
        self.metadataWidgets = {}
        self.defaultMetadataEditors = {}
        self.customMetadataEditors = {}
        self.buttons = {}
        self.labels = {}
        self.collapsibleLayouts = {}
        self.editCustomButtons = {}
        self.currItemType = ''


        
        #--------------------
        # The _layout that eventually becomes 
        # the layout of the XnatMetadataManager via
        # the '.setLayout' function
        #--------------------       
        self._layout = qt.QVBoxLayout()



        #--------------------
        # The Edit Button group.
        #
        # NOTE: A button group is created because
        # normal qt.QPushButton.connect events do not
        # send the button 'name' to the even method.  A
        # button group allows you to send the actual 
        # button to the vent method.
        #--------------------
        self.editCustomButtonGroup = qt.QButtonGroup()
        self.editCustomButtonGroup.connect('buttonClicked(QAbstractButton*)', self.editCustomClicked)
        self.editButtonsVisible = True



        #--------------------
        # We set this to true so the layout can anticipate
        # the size of the scroll area.
        #--------------------

        self.constructManager()
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.suspendAnimationDuration(True)
            collapsible.show()
            collapsible.setChecked(True)
            collapsible.suspendAnimationDuration(False)


        
    def constructManager(self):
        """ Constructs the XnatMetadataManager widget.
        """

        #--------------------
        # Loop through all folders as per 
        # XnatGlobals.XNAT_LEVELS.  We create an AnimatedCollapsible
        # for every folder, one XnatCustomMetadataEditor and one 
        # XnatDefaultMetadataEditor, along with the relevant buttons for
        # very folder in XNAT_LEVELS.
        #--------------------
        for xnatLevel in self.MODULE.GLOBALS.XNAT_LEVELS:

            #
            # Set DEFAULT label per xnat level.
            #
            self.labels[xnatLevel] = []
            self.labels[xnatLevel].append(qt.QLabel('<b>DEFAULT<b>'))
            self.labels[xnatLevel][0].setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)

            
            #
            # Set the collapsible's internal layout 
            # (a qt.QGridLayout) per folder.
            #
            self.collapsibleLayouts[xnatLevel] = qt.QGridLayout()
            self.collapsibleLayouts[xnatLevel].addWidget(self.labels[xnatLevel][0], 0, 0)


            #
            # Set the XnatDefaultMetadataEditor, 
            # add to layout.
            #
            self.defaultMetadataEditors[xnatLevel] = XnatDefaultMetadataEditor(self.MODULE, xnatLevel)
            self.collapsibleLayouts[xnatLevel].addWidget(self.defaultMetadataEditors[xnatLevel], 1, 0)


            #
            # Set the XnatCustomMetadataEditor, 
            # add to layout.
            # 
            self.customMetadataEditors[xnatLevel] = XnatCustomMetadataEditor(self.MODULE, xnatLevel)
            self.collapsibleLayouts[xnatLevel].addWidget(self.customMetadataEditors[xnatLevel], 1, 1, 1, 2)
            

            #
            # Set DEFAULT label per xnat level.
            #
            self.labels[xnatLevel].append(qt.QLabel('<b>CUSTOM<b>'))
            self.labels[xnatLevel][1].setFont(self.MODULE.GLOBALS.LABEL_FONT_BOLD)
            self.collapsibleLayouts[xnatLevel].addWidget(self.labels[xnatLevel][1], 0, 1)

            
            #
            # Add the 'editCustom' button. 
            #
            # NOTE: The user can choose to hide/show these buttons,
            # based on what's needed.  For isntance, the XnatMetadataSettings
            # class hides these buttons as they are not necessary for
            # its workflow.
            #
            self.editCustomButtons[xnatLevel] = self.MODULE.utils.generateButton(iconOrLabel = "Edit custom tags for '%s'"%(xnatLevel), 
                                                                               toolTip = "Adds a custom metadata tag to display in the 'Info' column.", 
                                                                               font = self.MODULE.GLOBALS.LABEL_FONT,
                                                                               size = qt.QSize(180, 20), 
                                                                               enabled = True)
            self.collapsibleLayouts[xnatLevel].addWidget(self.editCustomButtons[xnatLevel], 0, 2)
            self.editCustomButtonGroup.addButton(self.editCustomButtons[xnatLevel])
            

            #
            # Put all of the widgets into an
            # AnimatedCollapsible.
            #
            self.collapsibles[xnatLevel] = AnimatedCollapsible(self, xnatLevel.title(), 250, 250)

            contentsWidget = qt.QWidget()
            contentsWidget.setLayout(self.collapsibleLayouts[xnatLevel])
            self.collapsibles[xnatLevel].setWidget(contentsWidget)
            self.collapsibles[xnatLevel].setFixedWidth(550)


            #
            # Add collapsible to self._layout.
            #
            self._layout.addWidget(self.collapsibles[xnatLevel])
            self._layout.addSpacing(10)



        #--------------------
        # Set callback to Update XNATSlicer's 
        # layout when animating.
        #--------------------
        for key, collapsible in self.collapsibles.iteritems():
            collapsible.setOnAnimate(self.updateLayout)


            
        #--------------------
        # Set _layout to the master layout.
        #--------------------
        self._layout.addStretch()
        self.setLayout(self._layout)



        #--------------------
        #self.currItemType = 'label'
        #--------------------
        self.setItemType('label')



        




            


    def updateLayout(self):
        """
        """

        self.layout().update()


                


                        
    def setItemType(self, itemType):
        """ 
        """
        #print "\t (Metadata Manager) METADATA SET ITEM TYPE", itemType
        self.currItemType = itemType
        
        for key, metadataEditor in self.defaultMetadataEditors.iteritems():
            metadataEditor.setItemType(itemType)

        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setItemType(itemType)






    def setEditButtonsVisible(self, visible = None):
        """
        """

        #print "                 \n\n\nSET EDIT BUTTONS VISIBLE"
        if visible != None:
            self.editButtonsVisible = visible

        #--------------------
        # Hide the 'editCustom' buttons
        #--------------------
        for key, button in self.editCustomButtons.iteritems():
            if button:
                button.setVisible(self.editButtonsVisible)
                if not self.editButtonsVisible:
                    self.collapsibles[key].removeContentsWidgets(button)

            


    def editCustomClicked(self, button):
        """
        """
        for key, _button in self.editCustomButtons.iteritems():
            if button == _button:
                self.MODULE.xnatSettingsWindow.setCurrentIndex(1) 
                self.MODULE.metadataSettings.XnatMetadataManagers['main'].collapsibles[key].setChecked(True)
            else:
                self.MODULE.metadataSettings.XnatMetadataManagers['main'].collapsibles[key].setChecked(False)

        

                
    def setCustomEditVisible(self, visible):
        """
        """
        #
        # Custom
        #
        for key, metadataEditor in self.customMetadataEditors.iteritems():
            metadataEditor.setEditLineVisible(visible)


                
                   
    def update(self):
        """
        """
        self.updateLayout()
        for key in self.customMetadataEditors:
            self.customMetadataEditors[key].clear() 

            try:
                self.defaultMetadataEditors[key].update()
                self.customMetadataEditors[key].update()

                    
            except Exception, e:
                print self.MODULE.utils.lf()
                print str(e)



    def setOnMetadataCheckedTag(self, tag):
        """
        """

        for key in self.defaultMetadataEditors:
            self.defaultMetadataEditors[key].onMetadataCheckedTag = tag
        for key in self.customMetadataEditors:
            self.customMetadataEditors[key].onMetadataCheckedTag = tag            
