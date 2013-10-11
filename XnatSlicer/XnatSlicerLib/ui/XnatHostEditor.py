from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys


import XnatHostEditorUI



comment = """
XnatHostEditor is a widget that fits within the XnatSettingsPopup
that allows the user to edit the hosts that are stored in XnatSettings.
As a result, this class also communicates directly with XnatSettings.

TODO:
"""


        
class XnatHostEditor:
  """ Embedded within the settings popup.  Manages hosts.
  """

  
  def __init__(self, MODULE, parent = None):
    """ Init function.
    """

    self.parent = parent
    self.MODULE = MODULE


    
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
    self.urlLine, self.nameLine, self.setDefault, self.usernameLine = XnatHostEditorUI.makeSharedHostModalObjects(self)


    
    #--------------------
    # Buttons
    #--------------------
    self.addButton, self.editButton, self.deleteButton = XnatHostEditorUI.makeButtons(self)
    self.addButton.connect('clicked()', self.showAddHostModal)     
    self.editButton.connect('clicked()', self.showEditHostModal) 
    self.deleteButton.connect('clicked()', self.showDeleteHostModal)  


    
    #--------------------
    # Frame for setup window
    #--------------------
    self.frame = XnatHostEditorUI.makeFrame(self)

    
    
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
    if self.MODULE.settings.isModifiable(nameString):
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
    hostDictionary = self.MODULE.settings.getHostNameAddressDictionary()  



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
        if (self.MODULE.settings.isDefault(name)):
            self.hostLister.applyIsDefaultStyle()
        #
        # Get curr username
        #
        currName = self.MODULE.settings.getCurrUsername(name)
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
    self.MODULE.settings.deleteHost(self.prevName)
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
    deleted = self.MODULE.settings.deleteHost(hostStr[0])


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
    modifiable = not self.nameLine.text.strip("") in self.MODULE.settings.defaultHosts



    #--------------------
    # Determine if enetered host was set to default
    #--------------------
    modStr = str(modifiable)
    checkStr = str(self.setDefault.isChecked())


    
    #--------------------
    # Save Host
    #--------------------
    self.MODULE.settings.saveHost(self.nameLine.text, self.urlLine.text, isModifiable = modifiable, isDefault = self.setDefault.isChecked())



    #--------------------
    # Set default if checkbox is check
    #--------------------
    if self.setDefault.isChecked():
        self.MODULE.settings.setDefault(self.nameLine.text)   



    #--------------------
    # Set default username
    #--------------------
    if self.usernameLine.text != "":
        self.MODULE.settings.setCurrUsername(self.nameLine.text, self.usernameLine.text)



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
    self.currModal = XnatHostEditorUI.makeEditHostModal(self)
    self.currModal.setWindowModality(2)
    self.currModal.show()  



    
  def showDeleteHostModal(self, message=None):
    """ As described.
    """
    self.currModal = XnatHostEditorUI.makeDeleteHostModal(self)
    self.currModal.show()   



    
  def showAddHostModal(self):  
    """ As described.
    """ 
    self.currModal = XnatHostEditorUI.makeAddHostModal(self)
    self.currModal.show()





                  
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
