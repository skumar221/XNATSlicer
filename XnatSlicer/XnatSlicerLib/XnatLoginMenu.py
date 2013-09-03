from __main__ import vtk, ctk, qt, slicer

import os

from XnatSettings import *
import XnatLoginMenuUI



comment = """
  XnatLoginMenu is the class that handles all of the UI  
  to the XnatCommunicator.  It does not contain specific methods
  for the communications, rather it links the buttons to the 
  various communication classes and methods.

  TODO : 
"""






class XnatLoginMenu(object):
    """ Handles UI for loggin into XNAT as well as settings by 
        linking to button clicks to external methods.
    """



    
    def __init__(self, parent = None, browser = None):
        """ Descriptor
        """
        
        self.parent = parent
        self.browser = browser


        # Vars
        self.currHostUrl = None
        self.currHostName = None
        self.currHostAddress = None
        self.XnatHosts = None
        self.defaultPasswordText = "Password"
        self.defaultUsernameText = "Login"
        self.hostLoggedIn = False
        
        
        # Username and password lines 
        self.usernameLabel, self.passwordLabel, self.usernameLine, self.passwordLine = XnatLoginMenuUI.makeCredentialsWidgets(self)
        self.usernameLine.connect('cursorPositionChanged(int, int)', self.usernameLineEdited)  
        self.passwordLine.connect('cursorPositionChanged(int, int)', self.passwordLineEdited)
        self.passwordLine.connect('returnPressed()', self.simulateLoginClicked) 
        
        
        # Login button
        self.loginButton = XnatLoginMenuUI.makeLoginButton(self)
        self.loginButton.connect('clicked()', self.loginButtonClicked)
        
        
        # Host dropdown
        self.hostDropdown = XnatLoginMenuUI.makeHostDropdown(self)
        self.hostDropdown.connect('currentIndexChanged(const QString&)', self.hostDropdownClicked)



        # Settings button
        self.settingsButton = XnatLoginMenuUI.makeSettingsButton(self)  
        self.settingsButton.connect('pressed()', self.settingsButtonClicked)


        # Login layout
        self.loginLayout = XnatLoginMenuUI.makeLoginLayout(self)



        
    def resetHostDropdown(self):
        """ As stated.
        """
 
        # Clear host dropdown
        self.hostDropdown.clear()

        
        # Get the dictionary from settings
        hostDict = self.browser.settings.getHostNameAddressDictionary()
        for name in hostDict:     
            self.browser.XnatLoginMenu.hostDropdown.addItem(name)       

        

            
    def loadDefaultHost(self):
        """ As stated.
        """

        # Reset.
        self.resetHostDropdown()


        # Set host Dropdown to default stored hostName
        defaultName = self.browser.settings.getDefault()
        self.setHostDropdownByName(defaultName)

        
        # This will populate the stored user
        self.hostDropdownClicked(defaultName)
        self.populateCurrUser()

        


    def setHostDropdownByName(self, hostName):
        """ As stated.
        """
        for i in range(0, self.hostDropdown.maxVisibleItems):
            if self.hostDropdown.itemText(i).strip().lower() == hostName.strip().lower():
                self.hostDropdown.setCurrentIndex(i)
                self.currHostName = self.hostDropdown.itemText(i)
                break
            

            
        
    def populateCurrUser(self):
        """ If "Remember username" is clicked, queries the settings file to bring up 
        the username saved.
        """

        # Does the username exist in the settings file?
        if self.currHostName: 
            currUser = self.browser.settings.getCurrUsername(self.currHostName).strip()
            if len(currUser) > 0:  
                self.usernameLine.setText(currUser)
            else: 
                self.usernameLine.setText(self.defaultUsernameText)

                
        # If not, populate with default line
        else:
            self.usernameLine.setText(self.defaultUsernameText)       




    def simulateLoginClicked(self):
        """ Equivalent of clicking the login button.
        """
        self.loginButton.animateClick()


        
        
    def settingsButtonClicked(self):
        """ Equivalent of clicking the settings button.
        """
        self.browser.settingsPopup.showWindow()



        
    def usernameLineEdited(self):
        """ Listener when the username line is edited.
        """     
        if self.defaultUsernameText in str(self.usernameLine.text): 
            self.usernameLine.setText("")   


            
            
    def passwordLineEdited(self):  
        """ Listener for when the password line is edited.
        """     
        if self.defaultPasswordText in str(self.passwordLine.text): 
            self.passwordLine.setText("")
        self.passwordLine.setEchoMode(2)



        
    def hostDropdownClicked(self, name):
        """ Signal methods once dropdown is clicked -- loads the stored hosts.
        """
        self.currHostName = self.hostDropdown.currentText
        if self.hostDropdown.currentText:    
            self.populateCurrUser()


            
            
    def loginButtonClicked(self):
        """ Signal methods once the login button is clicked.
        """        
        self.browser.settings.setCurrUsername(self.hostDropdown.currentText, self.usernameLine.text)
        self.browser.XnatView.clear()
        if self.browser.settings.getAddress(self.hostDropdown.currentText):
            self.currHostUrl = qt.QUrl(self.browser.settings.getAddress(self.hostDropdown.currentText))
        else:
            pass  
        self.browser.loggedIn = True
        self.browser.beginXnat()
