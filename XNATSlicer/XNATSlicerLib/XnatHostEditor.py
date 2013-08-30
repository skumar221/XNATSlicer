from __main__ import vtk, qt, ctk, slicer


import os
import glob
import sys


import XnatHostEditorUI



comment = """
  XnatSettings is the class that manages storable settings for the
  XnatSlicer module.  The class is activated by clicking the wrench
  icon in the XnatSlicer browser.
"""





        
class XnatHostEditor:
  """ Embedded within the settings popup.  Manages hosts.
  """



  
  def __init__(self, browser, parent = None):
    """ Descriptor
    """

    self.parent = parent
    self.browser = browser


    #
    # Current popup opened by user
    #
    self.currPopup = None


    #
    # Host lister
    #        
    self.hostLister = HostLister(clickCallback = self.listItemClicked)

    
    #
    # Shared popup objects
    #
    self.urlLine, self.nameLine, self.setDefault, self.usernameLine = XnatHostEditorUI.makeSharedPopupObjects(self)


    #
    # Buttons
    #
    self.addButton, self.editButton, self.deleteButton = XnatHostEditorUI.makeButtons(self)
    self.addButton.connect('clicked()', self.showAddHostPopup)     
    self.editButton.connect('clicked()', self.showEditHostPopup) 
    self.deleteButton.connect('clicked()', self.showDeleteHostPopup)  


    
    #
    # Frame for setup window
    #
    self.frame = XnatHostEditorUI.makeFrame(self)

    
    
    #
    # Load hosts into host list
    #
    self.loadHosts()

    

    
  def listItemClicked(self, hostName):
    """ As stated
    """
    self.setButtonStates(self.hostLister.selectedText().split("\t")[0])



      
  def setButtonStates(self, nameString):   
    """ Enables / Disables button based upon the editable
        quality of the host.  Some hosts cannot be modified.
    """
    if not nameString in self.browser.settings.defaultHosts:
        self.deleteButton.setEnabled(True)
        self.editButton.setEnabled(True)
    else:
        self.deleteButton.setEnabled(False)
        self.editButton.setEnabled(True)




        
  def loadHosts(self):     
    """ Communicates with XnatSettings to load the stored hosts.
    """

    # Get host dictionary from XnatSettings
    hostDictionary = self.browser.settings.hostNameAddressDictionary()  

    # Empty hostList
    self.hostLister.setText("")

    # Iterate through dictionary and set host list
    for name in hostDictionary:

        # Add name and URL to host list
        self.hostLister.addNameAndUrl(name, hostDictionary[name])

        # Apply style if default
        if (self.browser.settings.isDefault(name)):
            self.hostLister.applyIsDefaultStyle()

        # Get curr username
        currName = self.browser.settings.getCurrUsername(name)

        # Add username if there is one
        if len(currName) > 0:
            self.hostLister.addUsername(currName)
        # Otherwise, newline
        else:
            self.hostLister.insertPlainText("\n")




    
  def rewriteHost(self):
    """ As described
    """
    self.browser.settings.deleteHost(self.prevName)
    self.prevName = None
    self.writeHost()


    
    
  def deleteHost(self):
    """ As described
    """
    hostStr = self.hostLister.selectedText().split("\t")
    deleted = self.browser.settings.deleteHost(hostStr[0])
    
    if deleted: 
        self.loadHosts()
        self.browser.settings.addHosts()

    # Close popup
    self.currPopup.close()
    self.currPopup = None


    
  def writeHost(self):
    """ As described
    """

    # Check if the nameLine is part of the defaut set
    modifiable = not self.nameLine.text.strip("") in self.browser.settings.defaultHosts

    # Determine if enetered host was set to default
    modStr = str(modifiable)
    checkStr = str(self.setDefault.isChecked())

    # Save Host
    self.browser.settings.saveHost(self.nameLine.text, self.urlLine.text, isModifiable = modifiable, isDefault = self.setDefault.isChecked())

    # Set default if checkbox is check
    if self.setDefault.isChecked():
        self.browser.settings.setDefault(self.nameLine.text)   

    # Set default username
    if self.usernameLine.text != "":
        self.browser.settings.setCurrUsername(self.nameLine.text, self.usernameLine.text)

    # Reload hosts
    self.browser.settings.addHosts()
    self.loadHosts() 

    # Close popup
    self.currPopup.close()
    self.currPopup = None




    
  def showEditHostPopup(self):
    """ As described
    """
    self.currPopup = XnatHostEditorUI.makeEditPopup(self)
    self.currPopup.show()  



    
  def showDeleteHostPopup(self, message=None):
    """ As described
    """
    self.currPopup = XnatHostEditorUI.makeDeletePopup(self)
    self.currPopup.show()   



    
  def showAddHostPopup(self):  
    """ As described
    """ 
    self.currPopup = XnatHostEditorUI.makeAddPopup(self)
    self.currPopup.show()





                  
class HostLister(qt.QTextEdit):
    """ Inherits qt.QTextEdit to list the hosts in the 
        Settings Popup
    """


    
    def __init__(self, parent = None, clickCallback = None): 
        """
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
