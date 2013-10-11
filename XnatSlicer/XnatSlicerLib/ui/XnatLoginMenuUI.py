from __main__ import vtk, ctk, qt, slicer

import os



comment = """
Constructs the various QT Widgets for the Login
menu.

TODO:
"""



def makeCredentialsWidgets(XnatLoginMenu):
    """ Makes the username and password lines
        and lables.
    """

    #--------------------
    # Username + password label and lines.
    #--------------------
    usernameLabel = qt.QLabel('username:')
    usernameLabel.setFont(XnatLoginMenu.MODULE.utils.labelFontBold)
    
    passwordLabel = qt.QLabel('password:')
    passwordLabel.setFont(XnatLoginMenu.MODULE.utils.labelFontBold)    
    
    usernameLine = qt.QLineEdit()   
    passwordLine = qt.QLineEdit() # encrypted
    
    usernameLine.setFixedWidth(100)
    passwordLine.setFixedWidth(100)

    
    #--------------------
    # Sets aesthetics.
    #--------------------
    usernameLine.setText(XnatLoginMenu.defaultUsernameText)
    usernameLine.setFont(XnatLoginMenu.MODULE.utils.labelFontItalic)
    passwordLine.setFont(XnatLoginMenu.MODULE.utils.labelFontItalic) 
    passwordLine.setText(XnatLoginMenu.defaultPasswordText)
    passwordLine.selectAll()

        
    return usernameLabel, passwordLabel, usernameLine, passwordLine



        
def makeHostDropdown(XnatLoginMenu):
    """ Initiates the dropdown that allows the user to select hosts
    """
    
    hostDropdown = qt.QComboBox()
    hostDropdown.setFont(XnatLoginMenu.MODULE.utils.labelFont)
    hostDropdown.toolTip = "Select Xnat host"
    return hostDropdown



        
def makeLoginButton(XnatLoginMenu):
    """ Connects the login to the first treeView call
    """
    
    plt = qt.QPalette()
    plt.setColor(qt.QPalette().Button, qt.QColor(255,255,255))    
    loginButton = qt.QPushButton("Login")
    loginButton.setFont(XnatLoginMenu.MODULE.utils.labelFontBold)    
    loginButton.toolTip = "Login to selected Xnat host"    
    loginButton.setFixedSize(XnatLoginMenu.MODULE.utils.buttonSizeMed.width(), (XnatLoginMenu.MODULE.utils.buttonSizeSmall.height() - 4))
    return loginButton




def makeSettingsButton(XnatLoginMenu):
    """ Initiates the button aesthetics for the button 
        that opens the manage hosts popup 
    """
    
    settingsButton = qt.QPushButton()
    settingsButton.setIcon(qt.QIcon(os.path.join(XnatLoginMenu.MODULE.utils.iconPath, 'wrench.png')) )
    settingsButton.toolTip = "Settings"
    settingsButton.setFixedSize(XnatLoginMenu.MODULE.utils.buttonSizeMed.width() - 10, 26)

    return settingsButton




def makeLoginLayout(XnatLoginMenu):
    """ As stated.
    """

    #--------------------
    # Username/Password Row
    #--------------------
    credentialsRow = qt.QHBoxLayout()
    credentialsRow.addWidget(XnatLoginMenu.settingsButton)
    credentialsRow.addWidget(XnatLoginMenu.hostDropdown)
    credentialsRow.addSpacing(20)
    credentialsRow.addWidget(XnatLoginMenu.usernameLine)
    credentialsRow.addWidget(XnatLoginMenu.passwordLine)
    credentialsRow.addWidget(XnatLoginMenu.loginButton)
    

    
    #--------------------
    # Everything related to logging in.
    #--------------------
    loginLayout = qt.QGridLayout() 
    loginLayout.addLayout(credentialsRow, 0,2)
    
    return loginLayout
