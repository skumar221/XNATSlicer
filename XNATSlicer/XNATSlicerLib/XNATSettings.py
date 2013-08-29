from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys
from XNATUtils import *

hostTag = 'Hosts/'
hostNameTag = 'FullName/'
hostAddressTag =   'Address/'
hostUsernameTag = 'Username/'
hostIsModifiableTag = 'IsModifiable/'
hostIsDefaultTag = 'IsDefault/'
hostCurrUserTag = 'CurrUser/'
RESTPathTag = 'RESTPath/'
pathTag = 'Paths/'

#=================================================================
# XNATSettings is the class that manages storable settings for the
# XNATSlicer module.  The class is activated by clicking the wrench
# icon in the XNATSlicer browser.
#=================================================================

class SettingsPopup:
    def __init__(self, browser, settings):        
        self.browser = browser
        self.settings = settings
        self.spacer = qt.QLabel("\n\n\n")
            
    def setWindow(self):
        self.windowLayout = qt.QFormLayout()
        self.window = qt.QWidget()
        self.window.setFixedWidth(500)
        self.window.setWindowModality(2)
        self.window.setLayout(self.windowLayout)
        self.window.hide()
        
    def show(self, position = True):
        self.setWindow()
        self.hostMgr = HostManager(self.browser, self.settings, parent = self)
        self.windowLayout.addRow(self.hostMgr.frame)#, 0, 0)

        self.windowLayout.addRow(self.spacer)
        self.windowLayout.addRow(self.spacer)

        self.windowLayout.addRow(self.spacer)
        self.windowLayout.addRow(self.spacer)
        self.doneButton = qt.QPushButton("Done")
        self.windowLayout.addRow(self.doneButton)#, 5, 5)
        self.doneButton.connect('clicked()', self.donePressed)
        
        self.window.show()
        if position:
            self.window.show()
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.window.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.window.height/2
            self.window.move(qt.QPoint(x,y))
        
        self.window.raise_()
        
    
    def donePressed(self):
        self.setWindow()
        self.window.hide()

class HostManager:
  """
  Embedded within the settings popup.  Manages hosts.
  """

  def __init__(self, browser, settings, parent = None):

    self.parent = parent
    self.browser = browser
    self.settings = settings
    self.utils = XNATUtils()


    self.urlLine = qt.QLineEdit()
    self.nameLine = qt.QLineEdit()
    
    self.setDefault = qt.QCheckBox("Set As Default?")

    self.mhLabel = qt.QLabel("Manage Hosts")
    self.usrLabel = qt.QLabel("Current Usernames") 
    
    self.hostDropdown = qt.QComboBox()
    self.hostDropdown.setFont(self.utils.labelFont)
    self.hostDropdown.connect('currentIndexChanged(const QString&)',self.hostDropdownClicked)   
    
    self.usernameLine = qt.QLineEdit()
    self.usernameLine.setFont(self.utils.labelFontItalic)
         
    self.hostList = HostLister()
    self.hostList.setFixedHeight(120)
    self.hostList.setReadOnly(True)
    self.hostList.setLineWrapMode(False)
    self.hostList.setHorizontalScrollBarPolicy(1)
    self.hostList.linkedWidget = self
    self.loadHosts()
        
    self.addButton = qt.QPushButton("Add")
    self.addButton.connect('clicked()', self.addButtonClicked)     
    
    self.editButton = qt.QPushButton("Edit")
    self.editButton.setEnabled(False)
    self.editButton.connect('clicked()', self.editButtonClicked)   
    
    self.deleteButton = qt.QPushButton("Delete")
    self.deleteButton.setEnabled(False)
    self.deleteButton.connect('clicked()', self.deleteButtonClicked)              
        
    topRow = qt.QHBoxLayout()
    topRow.addWidget(self.mhLabel)
       
    self.hostLayout = qt.QFormLayout()    
    self.hostLayout.addRow(topRow)
    self.hostLayout.addRow(self.hostList)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addWidget(self.addButton)
    buttonLayout.addWidget(self.editButton)
    buttonLayout.addWidget(self.deleteButton)   
    self.hostLayout.addRow(buttonLayout)

    self.frame = qt.QFrame()
    self.frame.setStyleSheet("QWidget { background: rgb(255,255,255)}")
    self.frame.setLayout(self.hostLayout)
    
    self.nameLine.setEnabled(True)
    self.urlLine.setEnabled(True)
        
    self.currWindow = None
    
    
  def hostDropdownClicked(self):
      self.usernameLine.setText(self.settings.getCurrUsername(self.hostDropdown.currentText))
      
  def enableStuff(self, state):   
    str = self.hostList.selectedText()
    list = str.split("\t")
    
    if self.settings.isModifiable(list[0]).find('1') > -1:
        self.deleteButton.setEnabled(state)
        self.editButton.setEnabled(state)
    else:
        self.deleteButton.setEnabled(False)
        self.editButton.setEnabled(True)
    
  def loadHosts(self):     
    hostDictionary= self.settings.hostNameAddressDictionary()   
    self.hostList.setText("")
    
    for name in hostDictionary:
        self.hostList.setTextColor(qt.QColor(0,0,0))
        self.hostList.setFontItalic(False)
        self.hostList.insertPlainText(name + "\t") 
        self.hostList.setFontItalic(True)
        self.hostList.setTextColor(qt.QColor(130,130,130))
        self.hostList.insertPlainText(hostDictionary[name] + "\t" )
        self.hostList.setTextColor(qt.QColor(0,0,0))
        self.hostList.setFontItalic(False)
        if (self.settings.isDefault(name)):
            self.hostList.setFontItalic(True)
            self.hostList.setTextColor(qt.QColor(0,0,225))
            self.hostList.insertPlainText("default")

        currName = self.settings.getCurrUsername(name)
        if ( currName != ""):
            self.hostList.setFontItalic(True)
            self.hostList.setTextColor(qt.QColor(20,20,20))
            self.hostList.insertPlainText("\t(stored login): " + currName + "\n")

        else:
            self.hostList.insertPlainText("\n")
           
        self.hostDropdown.addItem(name)

        
    
  def addButtonClicked(self):   
    cancelButton = qt.QPushButton("Cancel")
    self.nameLine.clear()
    self.urlLine.clear()
       
    saveButton = qt.QPushButton("OK")
    saveButton.connect("clicked()", self.writeHost)    
        
    currLayout = qt.QFormLayout()
    currLayout.addRow("Name:", self.nameLine)
    currLayout.addRow("URL:", self.urlLine)
    currLayout.addRow(self.setDefault)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)
    
    self.addWindow = qt.QDialog(self.addButton)
    self.addWindow.setWindowTitle("XNATSettings")
    self.addWindow.setFixedWidth(300)
    self.addWindow.setLayout(masterForm)
    
    cancelButton.connect("clicked()", self.addWindow.close)
    self.currWindow = self.addWindow
    self.addWindow.show()
    
    self.prevName = None

  def rewriteHost(self):
    self.settings.deleteHost(self.prevName)
    self.prevName = None
    self.writeHost()

  def writeHost(self):
    modifiable = True
    try: 
        self.settings.defaultHosts[self.nameLine.text.strip("")]
        self.settings.deleteHost(self.nameLine.text.strip(""))
        modifiable = False
    except:   
        modStr = str(modifiable)
        checkStr = str(self.setDefault.isChecked())
    
    self.settings.saveHost(self.nameLine.text, self.urlLine.text, isModifiable = modifiable, isDefault = self.setDefault.isChecked())
    if self.setDefault.isChecked():
        self.settings.setDefault(self.nameLine.text)        
    if self.usernameLine.text != "":
        self.settings.setCurrUsername(self.nameLine.text, self.usernameLine.text)
    
    self.browser.addHosts()
    self.loadHosts() 
    self.currWindow.close()
    self.currWindow = None
    self.setDefault.setCheckState(0)
    self.nameLine.clear()
    self.urlLine.clear()
    self.usernameLine.clear()
    self.parent.show()    
        
  def editButtonClicked(self):
    str = self.hostList.selectedText()
    list = str.split("\t")

    cancelButton = qt.QPushButton("Cancel")
    self.nameLine.setText(list[0])
    self.urlLine.setText(list[1])

    try:
        self.settings.defaultHosts[list[0].strip("")]
        self.nameLine.setReadOnly(True)
        self.nameLine.setFont(self.utils.labelFontItalic)
        self.nameLine.setEnabled(False)
        self.urlLine.setReadOnly(True)
        self.urlLine.setFont(self.utils.labelFontItalic)
        self.urlLine.setEnabled(False)
    except:
        self.nameLine.setEnabled(True)
        self.urlLine.setEnabled(True)
       
    saveButton = qt.QPushButton("OK")
    saveButton.connect("clicked()", self.rewriteHost)    
        
    currLayout = qt.QFormLayout()
    self.prevName = self.nameLine.text
    currLayout.addRow("Edit Name:", self.nameLine)
    currLayout.addRow("Edit URL:", self.urlLine)
 
    if self.settings.isDefault(self.nameLine.text):
        self.setDefault.setCheckState(2)
    
    currLayout.addRow(self.setDefault)
    self.usernameLine.setText(self.settings.getCurrUsername(self.nameLine.text))
    
    spaceLabel = qt.QLabel("")
    unmLabel = qt.QLabel("Stored Username:")
    currLayout.addRow(spaceLabel)
    currLayout.addRow(unmLabel)
    currLayout.addRow(self.usernameLine)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(saveButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)
    
    self.editWindow = qt.QDialog(self.addButton)
    self.editWindow.setWindowTitle("Edit Host")
    self.editWindow.setFixedWidth(300)
    self.editWindow.setLayout(masterForm)
    
    cancelButton.connect("clicked()", self.editWindow.close)
    self.currWindow = self.editWindow
    self.editWindow.show()
    
  def deleteButtonClicked(self, message=None):
    cancelButton = qt.QPushButton("Cancel")
    str = self.hostList.selectedText()
    list = str.split("\t")
    
    errorLabel = None
    
    if message:
        errorLabel = qt.QTextEdit()
        errorLabel.setReadOnly(True)
        errorLabel.setTextColor(qt.QColor(255,0,0))
        errorLabel.setFontItalic(True)
        errorLabel.setFontWeight(100)    
        errorLabel.insertPlainText(list[0])
        errorLabel.setFontWeight(0)
        errorLabel.insertPlainText(" is a default host and cannot be deleted.")    
        errorLabel.setFixedHeight(50)
        errorLabel.setFrameShape(0)
    
    messageLabel = qt.QTextEdit()
    messageLabel.setReadOnly(True)
    messageLabel.insertPlainText("Are you sure you want to delete the host ") 
    messageLabel.setFontItalic(True)
    messageLabel.setFontWeight(100)    
    messageLabel.insertPlainText(list[0])

    messageLabel.setFontWeight(0)   
    messageLabel.insertPlainText(" ?")
    messageLabel.setFixedHeight(40)
    messageLabel.setFrameShape(0)

    hostLabel = qt.QLabel()
       
    okButton = qt.QPushButton("OK")
        
    currLayout = qt.QVBoxLayout()
    currLayout.addWidget(messageLabel)
    if errorLabel:
        currLayout.addWidget(errorLabel)
        okButton.setEnabled(False)
    else:
        okButton.connect("clicked()", self.deleteHost) 
    
    currLayout.addStretch(1)
    
    buttonLayout = qt.QHBoxLayout()
    buttonLayout.addStretch(1)
    buttonLayout.addWidget(cancelButton)
    buttonLayout.addWidget(okButton)
    
    masterForm = qt.QFormLayout()    
    masterForm.addRow(currLayout)
    masterForm.addRow(buttonLayout)
    
    self.deleteWindow = qt.QDialog(self.addButton)
    self.deleteWindow.setWindowTitle("Delete Host")
    self.deleteWindow.setLayout(masterForm)
    
    cancelButton.connect("clicked()", self.deleteWindow.close)
    self.currWindow = self.deleteWindow
    self.deleteWindow.show()
  
  def deleteHost(self):
    str = self.hostList.selectedText()
    list = str.split("\t");
    if self.settings.deleteHost(list[0]):
        self.loadHosts()
        self.deleteWindow.close()
    else:
        self.deleteWindow.close()
        self.deleteButtonClicked(list[0] + " is a default host and cannot be deleted")
    
    self.browser.addHosts()

class XNATSettings:
  """ Manager for handing the settings file.  Stored in QSettings standard through
      a file ('XNATSettings.ini')
  """
  def __init__(self, parent=None, rootDir=None, browser = None):    
    if not parent:
      self.parent = slicer.qMRMLWidget()
    else:
      self.parent = parent   
    self.browser = browser
    self.filepath = os.path.join(rootDir, 'XNATSettings.ini')
    self.database = qt.QSettings(self.filepath, qt.QSettings.IniFormat)
    self.defaultHosts = {'Central': 'https://central.xnat.org', 
                         'CNDA': 'https://cnda.wustl.edu'}  
    self.setup()
    self.currErrorMessage = ""
    
      
  def setup(self):
    if not os.path.exists(self.filepath): 
        print 'No Xnat settings found...creating new settings file: ' + self.filepath
        self.createDefaultSettings()
      
  def createDefaultSettings(self):  
    restPaths = ['']
    for name in self.defaultHosts:
         setDefault = True if name == 'Central' else False
         self.saveHost(name, self.defaultHosts[name], False, setDefault)    
    self.savePaths(restPaths, "REST")

  
  def hostNameAddressDictionary(self):
    self.database.beginGroup(hostTag)
    hostDict = {}        
    for childName in self.database.childGroups():
        hostDict[self.database.value(childName +"/"+ hostNameTag)] = self.database.value(childName +"/"+ hostAddressTag)
    self.database.endGroup()
    return hostDict

    
  def saveHost(self, hostName, hostAddress, isModifiable=True, isDefault=False):
    hostDict = self.hostNameAddressDictionary()
    hostNameFound = False
    if not hostAddress.startswith("http://") and not hostAddress.startswith("https://"):
        hostAddress ="http://" + hostAddress
    for name in hostDict:
        hostNameFound = True if str(name).lower() == str(hostName).lower() else False 
        
    if hostName == "" or hostAddress == "":
       blanks = [] 
       if hostName =="": blanks.append("Name")
       if hostAddress =="": blanks.append("URI")
       
       blankTxt = ""
       for i in range(0, len(blanks)):
            blankTxt += blanks[i]
            if i<len(blanks)-1: blankTxt+=", "
            
       qt.QMessageBox.warning( None, "Save Host", "Please leave no text field blank (%s)"%(blankTxt))
       return False    
    elif hostNameFound == True:
       qt.QMessageBox.warning( None, "Save Host", hostName + " is a name that's already in use.")
       hostFound = False
       return False
    else:
       self.database.setValue(hostTag + hostName + "/" + hostNameTag, hostName)
       self.database.setValue(hostTag + hostName + "/" + hostAddressTag, hostAddress)      
       for item in self.defaultHosts:
           if hostName.strip("") == item.strip(""):
               isModifiable = False
               break
       self.database.setValue(hostTag + hostName + "/" + hostIsModifiableTag, isModifiable)
       self.database.setValue(hostTag + hostName + "/" + hostIsDefaultTag, isDefault)
       self.database.setValue(hostTag + hostName + "/" + hostCurrUserTag, "")
       return True
   
  def savePaths(self, paths, pathType = "REST"): 
      if pathType == "REST":
          currTag = RESTPathTag       
      for path in paths:
          self.database.setValue(pathTag + currTag, path)
          
  def getPath(self, pathType = "REST"):
      if pathType == "REST":
          currTag = RESTPathTag      
      return self.database.value(pathTag + currTag, "")   
  
  def deleteHost(self, hostName): 
    if self.database.value(hostTag + hostName + "/" + hostIsModifiableTag, "")==0:
        return False
    else:
        print "Deleting host: " + hostName
        self.database.remove(hostTag + hostName)
        return True
    
  def setDefault(self, hostName):
    self.database.beginGroup(hostTag)      
    for childName in self.database.childGroups():
        self.database.setValue(childName +"/"+ hostIsDefaultTag, False)
    self.database.setValue(hostName +"/"+ hostIsDefaultTag, True)
    self.database.endGroup()



    
  def isDefault(self, hostName):
    if "1" in (self.database.value(hostTag + hostName + "/" + hostIsDefaultTag, "").strip()): 
        return True
    return False 



  
  def isModifiable(self, hostName):
    title = unicode(str(self.database.value(hostTag + hostName + "/" + hostIsModifiableTag, "")))
    import unicodedata
    return unicodedata.normalize('NFKD', title).encode('ascii','ignore')



  
  def getAddress(self, hostName):
    return self.database.value(hostTag + hostName + "/" + hostAddressTag, "")



  
  def setCurrUsername(self, hostName, username):
    self.database.beginGroup(hostTag)  
    self.database.setValue(hostName +"/" + hostCurrUserTag, username)
    self.database.endGroup()



    
  def getCurrUsername(self, hostName):
    return self.database.value(hostTag + hostName + "/" + hostCurrUserTag, "")

class HostLister(qt.QTextEdit):
    def __init__(self, parent=None): 
        qt.QTextEdit.__init__(self, parent)
        self.currText = None
        # TODO: Ideally we'd create a custom signal here instead of linking it
        #       to the popup.  CustomSingals are not easy to do, however.
        self.linkedWidget = None

    def mouseReleaseEvent(self, event):
        cursor = qt.QTextCursor(self.textCursor())
        cursor.select(qt.QTextCursor.LineUnderCursor)
        self.setTextCursor(cursor)
        if cursor.selectedText():
            self.currText = cursor.selectedText()
            if self.linkedWidget:
                self.linkedWidget.enableStuff(True)
        else:
            if self.linkedWidget:
                self.linkedWidget.enableStuff(False)
    def selectedText(self):
        return self.currText
