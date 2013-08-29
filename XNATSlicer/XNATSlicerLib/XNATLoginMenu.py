from __main__ import vtk, ctk, qt, slicer

import os

from XNATSettings import *



comment = """
  XNATLoginMenu is the class that handles all of the UI interactions to the XNATCommunicator.

# TODO : 
"""



class XNATLoginMenu(object):
    """ XNATLoginMenu
    """



    
    def __init__(self, parent = None, browser = None):
        """ Descriptor
        """
        
        self.parent = parent
        self.browser = browser

        
        # Username and password lines  
        self.usernameLabel = qt.QLabel('username:')
        self.usernameLabel.setFont(self.browser.utils.labelFontBold)
        self.passwordLabel = qt.QLabel('password:')
        self.passwordLabel.setFont(self.browser.utils.labelFontBold)    
        self.usernameLine = qt.QLineEdit()   
        self.passwordLine = qt.QLineEdit() # encrypted
        self.usernameLine.setFixedWidth(100)
        self.passwordLine.setFixedWidth(100)

        
        # Login button
        self.loginButton = None
        
        
        # Host dropdown
        self.hostLabel = qt.QLabel('host:')
        self.hostLabel.setFont(self.browser.utils.labelFontBold)
        self.hostDropdown = None
        self.hostLoggedIn = False


        # Globals
        self.currHostUrl = None
        self.currHostName = None
        self.currHostAddress = None
        self.XNATHosts = None


        # Settings button
        self.settingsButton = None  
        self.networkRequest = None



        
    def initGUI(self):
        """ Descriptor
        """
        
        # Host Dropdown
        self.initHostDropdown()       

        
        # Manage Hosts Button
        self.initSettingsButton()

        
        # Login Lines
        self.initLoginLines()

        
        # Login Button
        self.initLoginButton()


        # Username/Password Row
        credentialsRow = qt.QHBoxLayout()
        credentialsRow.addWidget(self.settingsButton)
        credentialsRow.addWidget(self.hostDropdown)
        credentialsRow.addSpacing(20)
        credentialsRow.addWidget(self.usernameLine)
        credentialsRow.addWidget(self.passwordLine)
        credentialsRow.addWidget(self.loginButton)

        
        # Everything related to logging in
        self.loginLayout = qt.QGridLayout() 
        self.loginLayout.addLayout(credentialsRow, 0,2)


        
        
    def initLoginLines(self):
        """ Password and login lines
        """

        
        # Descriptions
        self.defaultPasswordText = "Password"
        self.defaultUsernameText = "Login"

        
        # Asthetics  
        self.usernameLine.setText(self.defaultUsernameText)
        self.usernameLine.setFont(self.browser.utils.labelFontItalic)
        self.passwordLine.setFont(self.browser.utils.labelFontItalic) 
        self.passwordLine.setText(self.defaultPasswordText)
        self.passwordLine.selectAll()

        
        # Signals
        self.usernameLine.connect('cursorPositionChanged(int, int)', self.usernameLineEdited)  
        self.passwordLine.connect('cursorPositionChanged(int, int)', self.passwordLineEdited)
        self.passwordLine.connect('returnPressed()', self.simulateLoginClicked) 


        # Load the previously stored user
        self.populateCurrUser()



        
    def initHostDropdown(self):
        """ Initiates the dropdown that allows the user to select hosts
        """
        self.hostDropdown = qt.QComboBox()
        self.hostDropdown.setFont(self.browser.utils.labelFont)
        self.hostDropdown.toolTip = "Select XNAT host"
        self.currHostUrl = qt.QUrl(self.hostDropdown.currentText)
        self.addHosts()
        self.hostDropdown.connect('currentIndexChanged(const QString&)', self.hostDropdownClicked) 



        
    def initSettingsButton(self):
        """ Initiates the button aesthetics for the button that opens the manage 
        hosts popup 
        """
        self.settingsButton = qt.QPushButton()
        self.settingsButton.setIcon(qt.QIcon(os.path.join(self.browser.utils.iconPath, 
                                                          'wrench.png')) )
        self.settingsButton.toolTip = "Settings"
        self.settingsButton.setFixedSize(self.browser.utils.buttonSizeMed.width() - 10, 26)
        self.settingsButton.connect('pressed()', self.settingsButtonClicked)



        
    def initLoginButton(self):
        """ Connects the login to the first treeView call
        """
        plt = qt.QPalette()
        plt.setColor(qt.QPalette().Button, qt.QColor(255,255,255))    
        self.loginButton = qt.QPushButton("Login")
        
        self.loginButton.setFont(self.browser.utils.labelFontBold)    
        self.loginButton.toolTip = "Login to selected XNAT host"    
        self.loginButton.connect('clicked()', self.loginButtonClicked)
        self.loginButton.setFixedSize(self.browser.utils.buttonSizeMed.width(), self.browser.utils.buttonSizeSmall.height() - 4) 



        
    def addHosts(self):
        """ Adds and stores the entered host
        """
        self.hostDropdown.clear()
        hostDict = self.browser.settings.hostNameAddressDictionary()
        for name in hostDict:     
            self.hostDropdown.addItem(name)
            
 
        # Loop through to find default host
        if not self.currHostName:
            for i in range(0, len(hostDict.keys())):    
                if int(self.browser.settings.isDefault(hostDict.keys()[i]))>0:
                    self.hostDropdown.setCurrentIndex(i)
                    self.currHostName = hostDict.keys()[i]
                    break

                
                

    def populateCurrUser(self):
        """ If "Remember username" is clicked, queries the settings file to bring up 
        the username saved.
        """

        # Does the username exist in the settings file?
        if self.currHostName:    
            currUser = self.browser.settings.getCurrUsername(self.currHostName).strip("").strip(" ")
            if len(currUser) > 0:  
                self.usernameLine.setText(currUser)
            else: 
                self.usernameLine.settext(self.defaultusernametext)

                
        # If not, populate with default line
        else:
            self.usernameLine.setText(self.defaultUsernameText)       




    def simulateLoginClicked(self):
        """ Equivalent of clicking the login button.
        """
        self.loginButton.animateClick()
        #self.loginButtonClicked()


        
        
    def settingsButtonClicked(self):
        """ Equivalent of clicking the settings button.
        """
        self.settingsPopup = SettingsPopup(self, self.browser.settings)
        self.settingsPopup.show()



        
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
        self.browser.XNATView.clear()
        if self.browser.settings.getAddress(self.hostDropdown.currentText):
            self.currHostUrl = qt.QUrl(self.browser.settings.getAddress(self.hostDropdown.currentText))
        else:
            pass  
        self.browser.loggedIn = True
        self.browser.beginXNAT()
