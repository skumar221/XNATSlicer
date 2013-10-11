from __main__ import vtk, ctk, qt, slicer

import os

from XnatSettings import *
import XnatLoginMenuUI



comment = """
XnatLoginMenu is the class that handles all of the UI  
to the XnatCommunicator related to logging in to a given 
XNAT host.  

TODO : 
"""



class XnatLoginMenu(object):
    """ Handles UI for loggin into XNAT as well as settings by 
        linking to button clicks to external methods in the
        XnatCommunicator.
    """

    def __init__(self, parent = None, browser = None):
        """ Init function.
        """
        
        self.parent = parent
        self.browser = browser


        
        #--------------------
        # Set relevant variables.
        #--------------------
        self.currHostUrl = None
        self.currHostName = None
        self.currHostAddress = None
        self.XnatHosts = None
        self.defaultPasswordText = "Password"
        self.defaultUsernameText = "Login"
        self.hostLoggedIn = False
        

        
        #--------------------
        # Create Username and password lines 
        #--------------------
        self.usernameLabel, self.passwordLabel, self.usernameLine, self.passwordLine = XnatLoginMenuUI.makeCredentialsWidgets(self)


        
        #--------------------
        # Create login button
        #--------------------
        self.loginButton = XnatLoginMenuUI.makeLoginButton(self)
        

        
        #--------------------
        # Create host dropdown.
        #--------------------
        self.hostDropdown = XnatLoginMenuUI.makeHostDropdown(self)
        


        #--------------------
        # Create settings button.
        #--------------------
        self.settingsButton = XnatLoginMenuUI.makeSettingsButton(self)  
        

        
        #--------------------
        # Create login layout.
        #--------------------
        self.loginLayout = XnatLoginMenuUI.makeLoginLayout(self)



        #--------------------
        # Set event connections.
        #--------------------
        self.usernameLine.connect('cursorPositionChanged(int, int)', self.onUsernameLineEdited)  
        self.passwordLine.connect('cursorPositionChanged(int, int)', self.onPasswordLineEdited)
        self.passwordLine.connect('returnPressed()', self.simulateLoginClicked)
        self.loginButton.connect('clicked()', self.loginButtonClicked)
        self.hostDropdown.connect('currentIndexChanged(const QString&)', self.onHostDropdownClicked)
        self.settingsButton.connect('pressed()', self.onSettingsButtonClicked)



        
    def resetHostDropdown(self):
        """ Clears the host dropdown widget and then
            loads the defaults from the XnatSettings object.
        """

        #--------------------
        # Clear host dropdown
        #--------------------
        self.hostDropdown.clear()


        
        #--------------------
        # Get the dictionary from settings and the key to 
        # the dropdown widget.
        #--------------------
        hostDict = self.browser.settings.getHostNameAddressDictionary()
        for name in hostDict:     
            self.browser.XnatLoginMenu.hostDropdown.addItem(name)       

        

            
    def loadDefaultHost(self):
        """ Loads the default host into the 
            hostDropdown from XnatSettings.
        """

        #--------------------
        # Reset the dropdown.
        #--------------------
        self.resetHostDropdown()


        #--------------------
        # Set host dropdown to default stored hostName.
        #--------------------
        defaultName = self.browser.settings.getDefault()
        self.setHostDropdownByName(defaultName)


        #--------------------
        # Populate the stored user into the username line.
        #--------------------
        self.onHostDropdownClicked(defaultName)
        self.populateCurrUser()

        


    def setHostDropdownByName(self, hostName):
        """ Sets the current intem in the hostDropdown
            to the name specified in the 'hostName' argument by
            looping through all of its visible items.
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

        #--------------------
        # Does the username exist in the settings file?
        #--------------------
        if self.currHostName: 
            currUser = self.browser.settings.getCurrUsername(self.currHostName).strip()
            #
            # If it does, and it's not a '' string, then apply it to the
            # usernameLine....
            #
            if len(currUser) > 0:  
                self.usernameLine.setText(currUser)
            #
            # Otherwise apply a default string to the username line.
            #
            else: 
                self.usernameLine.setText(self.defaultUsernameText)


                
        #--------------------        
        # If not, populate with default line
        #--------------------
        else:
            self.usernameLine.setText(self.defaultUsernameText)       




    def simulateLoginClicked(self):
        """ Equivalent of clicking the login button.
        """
        self.loginButton.animateClick()


        
        
    def onSettingsButtonClicked(self):
        """ Event function for when the settings button
            is clicked.  Displays the XnatSettingsPopup 
            from the browser.
        """
        self.browser.settingsPopup.showWindow()



        
    def onUsernameLineEdited(self):
        """ Event function for when the username line is edited.
        """     
        if self.defaultUsernameText in str(self.usernameLine.text): 
            self.usernameLine.setText("")   


            
            
    def onPasswordLineEdited(self):  
        """ Event function for when the password line is edited.
        """     
        if self.defaultPasswordText in str(self.passwordLine.text): 
            self.passwordLine.setText("")
        self.passwordLine.setEchoMode(2)



        
    def onHostDropdownClicked(self, name):
        """ Event function for when the hostDropdown is clicked.  
            Loads the stored username into the username line, 
            if it's there.
        """
        self.currHostName = self.hostDropdown.currentText
        if self.hostDropdown.currentText:    
            self.populateCurrUser()


            
            
    def loginButtonClicked(self):
        """ Event function for when the login button is clicked.
            Steps below.
        """        

        #--------------------
        # Store the current username in settings
        #--------------------
        self.browser.settings.setCurrUsername(self.hostDropdown.currentText, self.usernameLine.text)

        
        #--------------------
        # Clear the current XnatView.
        #--------------------
        self.browser.XnatView.clear()


        #--------------------
        # Derive the XNAT host URL by mapping the current item in the host
        # dropdown to its value pair in the settings.  
        #--------------------
        if self.browser.settings.getAddress(self.hostDropdown.currentText):
            self.currHostUrl = qt.QUrl(self.browser.settings.getAddress(self.hostDropdown.currentText))
            #
            # Call the 'beginXnat' function from the browser.
            #
            self.browser.loggedIn = True
            self.browser.beginXnat()
        else:
            print "%s The host '%s' doesn't appear to have a valid URL"%(self.browser.utils.lf(), self.hostDropdown.currentText) 
            pass  

