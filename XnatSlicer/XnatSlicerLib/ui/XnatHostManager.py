from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettingManager import *



comment = """
XnatHostManager is a widget that fits within the XnatSettingsPopup
that allows the user to edit the hosts that are stored in XnatSettings.
As a result, this class also communicates directly with XnatSettings.

TODO:
"""


        
class XnatHostManager(XnatSettingManager):
    """ Embedded within the settings popup.  Manages hosts.
    """

  
    def __init__(self, title, MODULE):
        """ Init function.
        """
        
        #--------------------
        # Call parent init
        #--------------------
        super(XnatHostManager, self).__init__(title, MODULE)
        
        
        
        #--------------------
        # Current popup opened by user
        #--------------------
        self.currModal = None
        
        
        
        #--------------------
        # Host lister
        #--------------------      
        self.hostLister = HostLister(clickCallback = self.listItemClicked)
        
        
        
        #--------------------
        # Shared popup objects
        #--------------------
        self.urlLine, self.nameLine, self.setDefault, self.usernameLine = makeSharedHostModalObjects(self)
        
        
        
        #--------------------
        # Buttons
        #--------------------
        self.addButton, self.editButton, self.deleteButton = makeButtons(self)
        self.addButton.connect('clicked()', self.showAddHostModal)     
        self.editButton.connect('clicked()', self.showEditHostModal) 
        self.deleteButton.connect('clicked()', self.showDeleteHostModal)  
        

        
        #--------------------
        # Frame for setup window
        #--------------------
        self.makeFrame()
        
        

    
        #--------------------
        # Layout for entire frame
        #--------------------
        self.masterLayout.addStretch()
        self.frame.setLayout(self.masterLayout)



        
        #--------------------
        # Load hosts into host list
        #--------------------
        self.loadHosts()





        
        
        
    def listItemClicked(self, hostName):
        """ Callbcak for when a user clicks on a given item
        within the host editor.
        """
        self.setButtonStates(self.hostLister.selectedText().split("\t")[0])
        
        
        
        
    def setButtonStates(self, nameString):   
        """ Enables / Disables button based upon the editable
        quality of the host.  Some hosts cannot be modified.
        """
        if self.MODULE.settingsFile.isModifiable(nameString):
            self.deleteButton.setEnabled(True)
            self.editButton.setEnabled(True)
        else:
            self.deleteButton.setEnabled(False)
            self.editButton.setEnabled(True)



        
    def loadHosts(self):     
        """ Communicates with XnatSettings to load the stored hosts.
        """
        
        #--------------------
        # Get host dictionary from XnatSettings
        #--------------------
        hostDictionary = self.MODULE.settingsFile.getHostNameAddressDictionary()  
        
        
        
        #--------------------
        # Empty hostList in the editor.
        #--------------------
        self.hostLister.setText("")
        
        
        
        #--------------------
        # Iterate through dictionary and apply text to the hostList
        #--------------------
        for name in hostDictionary:
            #
            # Add name and URL to host list
            #
            self.hostLister.addNameAndUrl(name, hostDictionary[name])
            #
            # Apply style if default
            #
            if (self.MODULE.settingsFile.isDefault(name)):
                self.hostLister.applyIsDefaultStyle()
            #
            # Get curr username
            #
            currName = self.MODULE.settingsFile.getCurrUsername(name)
            #
            # If there's a username, add it....
            #
            if len(currName) > 0:
                self.hostLister.addUsername(currName) 
            #
            # Otherwise, insert newline.
            #
            else:
                self.hostLister.insertPlainText("\n")




    
    def rewriteHost(self):
        """ As stated.  Calls on the internal "writeHost" function.
        """
        self.MODULE.settingsFile.deleteHost(self.prevName)
        self.prevName = None
        self.writeHost()


    
    
    def deleteHost(self):
        """ As described
        """
        #--------------------
        # Delete the selected host by
        # applying the text to the settings, and removing from there.
        #--------------------
        hostStr = self.hostLister.selectedText().split("\t")
        deleted = self.MODULE.settingsFile.deleteHost(hostStr[0])
        
        
        #--------------------
        # Reload everything
        #--------------------
        if deleted: 
            self.loadHosts()
            self.MODULE.XnatLoginMenu.loadDefaultHost()
            
        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None


    
    
    def writeHost(self):
        """ As described.  See below for details.
        """

        #--------------------
        # Check if the nameLine is part of the defaut set
        #--------------------
        modifiable = not self.nameLine.text.strip("") in self.MODULE.settingsFile.defaultHosts



        #--------------------
        # Determine if enetered host was set to default
        #--------------------
        modStr = str(modifiable)
        checkStr = str(self.setDefault.isChecked())
        
        
        
        #--------------------
        # Save Host
        #--------------------
        self.MODULE.settingsFile.saveHost(self.nameLine.text, self.urlLine.text, isModifiable = modifiable, isDefault = self.setDefault.isChecked())



        #--------------------
        # Set default if checkbox is check
        #--------------------
        if self.setDefault.isChecked():
            self.MODULE.settingsFile.setDefault(self.nameLine.text)   



        #--------------------
        # Set default username
        #--------------------
        if self.usernameLine.text != "":
            self.MODULE.settingsFile.setCurrUsername(self.nameLine.text, self.usernameLine.text)



        #--------------------
        # Reload hosts
        #--------------------
        self.MODULE.XnatLoginMenu.loadDefaultHost()
        self.loadHosts() 



        #--------------------
        # Close popup
        #--------------------
        self.currModal.close()
        self.currModal = None




    
    def showEditHostModal(self):
        """ As described.
        """
        self.currModal = makeEditHostModal(self)
        self.currModal.setWindowModality(2)
        self.currModal.show()  
        
        
        
        
    def showDeleteHostModal(self, message=None):
        """ As described.
        """
        self.currModal = makeDeleteHostModal(self)
        self.currModal.show()   
            
            
            
            
    def showAddHostModal(self):  
        """ As described.
        """ 
        self.currModal = makeAddHostModal(self)
        self.currModal.show()


    


    def makeFrame(self):
        """ As described.
        """

        
        #--------------------
        # Layout for top part of frame (host list)
        #--------------------
        self.masterLayout.addWidget(self.hostLister)
        
        
        
        #--------------------
        # Layout for bottom part of frame (buttons)
        #--------------------
        buttonLayout = qt.QHBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.editButton)
        buttonLayout.addWidget(self.deleteButton)   
        self.masterLayout.addLayout(buttonLayout)


        

                  
class HostLister(qt.QTextEdit):
    """ Inherits qt.QTextEdit to list the hosts in the 
        SettingsModal
    """


    
    def __init__(self, parent = None, clickCallback = None): 
        """ Init function.
        """
        qt.QTextEdit.__init__(self, parent)
        
        self.currText = None        
        self.setFixedHeight(120)
        self.setReadOnly(True)
        self.setLineWrapMode(False)
        self.setHorizontalScrollBarPolicy(1)

        self.clickCallback = clickCallback
  


        
    def mouseReleaseEvent(self, event):
        """ After the user clicks on a given line.
        """
        cursor = qt.QTextCursor(self.textCursor())
        cursor.select(qt.QTextCursor.LineUnderCursor)
        self.setTextCursor(cursor)
        if cursor.selectedText():
            self.currText = cursor.selectedText()

        if self.clickCallback:
            self.clickCallback(self.currText)


                

    def addNameAndUrl(self, name, url):
        """ Applies aesthetic scheme will adding name and Url.
        """
        self.setTextColor(qt.QColor(0,0,0))
        self.setFontItalic(False)
        self.insertPlainText(name + "\t") 
        self.setFontItalic(True)
        self.setTextColor(qt.QColor(130,130,130))
        self.insertPlainText(url + "\t" )
        self.setTextColor(qt.QColor(0,0,0))
        self.setFontItalic(False)



        
    def applyIsDefaultStyle(self):
        """ Stylistic display.
        """
        self.setFontItalic(True)
        self.setTextColor(qt.QColor(0,0,225))
        self.insertPlainText("default")



        
    def selectedText(self):
        """ Returns selected text.
        """ 
        return self.currText


        
        
    def addUsername(self, username):
        """ Stylistic adding of username.
        """
        self.setFontItalic(True)
        self.setTextColor(qt.QColor(20,20,20))
        self.insertPlainText("\t(stored login): " + username + "\n")







def makeAddHostModal(hostEditor):
    """ As stated. 
    """
    
    #--------------------
    # Clear shared object lines
    #--------------------
    hostEditor.nameLine.clear()
    hostEditor.urlLine.clear()



    #--------------------    
    # Buttons
    #--------------------
    saveButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")



    #--------------------
    # Create for line editors
    #--------------------
    currLayout = qt.QFormLayout()
    currLayout.addRow("Name:", hostEditor.nameLine)
    currLayout.addRow("URL:", hostEditor.urlLine)
    currLayout.addRow(hostEditor.setDefault)



    #--------------------
    # Create layout for buttons
    #--------------------
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)



    #--------------------
    # Combine both layouts
    #--------------------
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)



    #--------------------
    # Make window
    #--------------------
    addHostModal = qt.QDialog(hostEditor.addButton)
    addHostModal.setWindowTitle("Add Host")
    addHostModal.setFixedWidth(300)
    addHostModal.setLayout(masterForm)
    addHostModal.setWindowModality(2)



    #--------------------
    # Clear previous host
    #--------------------
    hostEditor.prevName = None

    

    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", addHostModal.close)
    saveButton.connect("clicked()", hostEditor.writeHost)   

    
    return addHostModal




def makeEditHostModal(hostEditor):
    """ As stated.
    """

    #--------------------
    # Get selected strings from host list.
    #--------------------
    selHost = hostEditor.hostLister.selectedText().split("\t")


    
    #--------------------
    # Populate the line edits from selecting strings.
    #--------------------
    hostEditor.nameLine.setText(selHost[0])
    hostEditor.urlLine.setText(selHost[1])



    #--------------------
    # Prevent editing of default host. 
    #--------------------
    if selHost[0].strip("") in hostEditor.MODULE.settingsFile.defaultHosts:
        hostEditor.nameLine.setReadOnly(True)
        hostEditor.nameLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC)
        hostEditor.nameLine.setEnabled(False)
        hostEditor.urlLine.setReadOnly(True)
        hostEditor.urlLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC)
        hostEditor.urlLine.setEnabled(False)


        
    #--------------------
    # Otherwise, go ahead.
    #--------------------
    else:
        hostEditor.nameLine.setEnabled(True)
        hostEditor.urlLine.setEnabled(True)



    #--------------------
    # Buttons.
    #--------------------
    cancelButton = qt.QPushButton("Cancel")   
    saveButton = qt.QPushButton("OK")



    #--------------------
    # Layouts.
    #--------------------
    currLayout = qt.QFormLayout()
    hostEditor.prevName = hostEditor.nameLine.text
    currLayout.addRow("Edit Name:", hostEditor.nameLine)
    currLayout.addRow("Edit URL:", hostEditor.urlLine)



    #--------------------
    # Default checkbox if default.
    #--------------------
    if hostEditor.MODULE.settingsFile.isDefault(hostEditor.nameLine.text):
        hostEditor.setDefault.setCheckState(2)



    #--------------------
    # Labels.
    #--------------------
    spaceLabel = qt.QLabel("")
    unmLabel = qt.QLabel("Stored Username:")


    
    #--------------------
    # Layouts.
    #--------------------
    currLayout.addRow(hostEditor.setDefault)
    hostEditor.usernameLine.setText(hostEditor.MODULE.settingsFile.getCurrUsername(hostEditor.nameLine.text))
    currLayout.addRow(spaceLabel)
    currLayout.addRow(unmLabel)
    currLayout.addRow(hostEditor.usernameLine)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)


    
    #--------------------
    # The modal.
    #--------------------
    editHostModal = qt.QDialog(hostEditor.addButton)
    editHostModal.setWindowTitle("Edit Host")
    editHostModal.setFixedWidth(300)
    editHostModal.setLayout(masterForm)
    editHostModal.setWindowModality(2)


    
    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", editHostModal.close)
    saveButton.connect("clicked()", hostEditor.rewriteHost) 

    return editHostModal




def makeDeleteHostModal(hostEditor):
    """ As stated.
    """

    #--------------------
    # get selected strings from host list
    #--------------------
    selHost = hostEditor.hostLister.selectedText().split("\t")


    
    #--------------------
    # Buttons
    #--------------------
    okButton = qt.QPushButton("OK")
    cancelButton = qt.QPushButton("Cancel")



    #--------------------
    # Labels
    #--------------------
    messageLabel = qt.QTextEdit()
    messageLabel.setReadOnly(True)
    messageLabel.insertPlainText("Are you sure you want to delete the host ") 
    messageLabel.setFontItalic(True)
    messageLabel.setFontWeight(100)    
    messageLabel.insertPlainText(selHost[0])

    messageLabel.setFontWeight(0)   
    messageLabel.insertPlainText(" ?")
    messageLabel.setFixedHeight(40)
    messageLabel.setFrameShape(0)


    
    #--------------------
    # Layouts
    #--------------------
    currLayout = qt.QVBoxLayout()
    currLayout.addWidget(messageLabel)
    currLayout.addStretch(1)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(okButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)



    #--------------------
    # Window
    #--------------------
    deleteHostModal = qt.QDialog(hostEditor.addButton)
    deleteHostModal.setWindowTitle("Delete Host")
    deleteHostModal.setLayout(masterForm)
    deleteHostModal.setWindowModality(2)



    #--------------------
    # Button Connectors
    #--------------------
    cancelButton.connect("clicked()", deleteHostModal.close)
    okButton.connect("clicked()", hostEditor.deleteHost) 
    
    return deleteHostModal

    



def makeButtons(hostEditor):
    """ As described.
    """
    addButton = qt.QPushButton("Add")
    editButton = qt.QPushButton("Edit")
    deleteButton = qt.QPushButton("Delete")
    
    deleteButton.setEnabled(False)
    editButton.setEnabled(False)  

    return addButton, editButton, deleteButton




def makeSharedHostModalObjects(hostEditor):
    """ Makes commonly shared UI objects for the Add, Edit popups.
    """
    urlLine = qt.QLineEdit()
    nameLine = qt.QLineEdit()
    setDefault = qt.QCheckBox("Set As Default?")
    usernameLine = qt.QLineEdit()
        
    urlLine.setEnabled(True)
    nameLine.setEnabled(True) 
    usernameLine.setFont(hostEditor.MODULE.GLOBALS.LABEL_FONT_ITALIC) 

    return urlLine, nameLine, setDefault, usernameLine 
