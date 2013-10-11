from __main__ import vtk, ctk, qt, slicer



comment = """
Constructs the various QT Widgets for Editing the hosts
available to the user in the settings modal.

TODO:
"""



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
    if selHost[0].strip("") in hostEditor.MODULE.settings.defaultHosts:
        hostEditor.nameLine.setReadOnly(True)
        hostEditor.nameLine.setFont(hostEditor.MODULE.utils.labelFontItalic)
        hostEditor.nameLine.setEnabled(False)
        hostEditor.urlLine.setReadOnly(True)
        hostEditor.urlLine.setFont(hostEditor.MODULE.utils.labelFontItalic)
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
    if hostEditor.MODULE.settings.isDefault(hostEditor.nameLine.text):
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
    hostEditor.usernameLine.setText(hostEditor.MODULE.settings.getCurrUsername(hostEditor.nameLine.text))
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





def makeFrame(hostEditor):
    """ As described.
    """
    
    #--------------------
    # For the frame
    #--------------------
    hostEditor.mhLabel = qt.QLabel("Manage Hosts")


    
    #--------------------
    # Layout for top part of frame (host list)
    #--------------------
    topRow = qt.QHBoxLayout()
    topRow.addWidget(hostEditor.mhLabel)
    hostEditor.hostLayout = qt.QFormLayout()    
    hostEditor.hostLayout.addRow(topRow)
    hostEditor.hostLayout.addRow(hostEditor.hostLister)


    
    #--------------------
    # Layout for bottom part of frame (buttons)
    #--------------------
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addWidget(hostEditor.addButton)
    buttonLayout.addWidget(hostEditor.editButton)
    buttonLayout.addWidget(hostEditor.deleteButton)   
    hostEditor.hostLayout.addRow(buttonLayout)


    
    #--------------------
    # Layout for entire frame
    #--------------------
    frame = qt.QFrame()
    frame.setStyleSheet("QWidget { background: rgb(255,255,255)}")
    frame.setLayout(hostEditor.hostLayout)
    
    return frame




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
    usernameLine.setFont(hostEditor.MODULE.utils.labelFontItalic) 

    return urlLine, nameLine, setDefault, usernameLine 
