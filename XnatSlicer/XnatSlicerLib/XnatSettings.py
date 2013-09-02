from __main__ import vtk, qt, ctk, slicer


import os
import glob
import sys


from XnatSettingsPopup import *



comment = """
XnatSettings is the class that manages storable settings for the
XnatSlicer module.  The class is activated by clicking the wrench
icon in the XnatSlicer browser.
"""






hostTag = 'Hosts/'
hostNameTag = 'FullName/'
hostAddressTag =   'Address/'
hostUsernameTag = 'Username/'
hostIsModifiableTag = 'IsModifiable/'
hostIsDefaultTag = 'IsDefault/'
hostCurrUserTag = 'CurrUser/'
RESTPathTag = 'RESTPath/'
pathTag = 'Paths/'






class XnatSettings:
  """ Manager for handing the settings file.  Stored in QSettings standard through
      'XnatSettings.ini')
  """



  
  def __init__(self, parent=None, rootDir=None, browser = None):    
    if not parent:
      self.parent = slicer.qMRMLWidget()
    else:
      self.parent = parent   
    self.browser = browser
    self.filepath = os.path.join(rootDir, 'XnatSettings.ini')
    self.database = qt.QSettings(self.filepath, qt.QSettings.IniFormat)
    self.defaultHosts = {'Central': 'https://central.xnat.org', 
                         'CNDA': 'https://cnda.wustl.edu'}  
    self.setup()
    self.currErrorMessage = ""
    


    
  def setup(self):
    """ Determine if there is an XnatSettings.ini file.
    """
    if not os.path.exists(self.filepath): 
        print 'No Xnat settings found...creating new settings file: ' + self.filepath
        self.createDefaultSettings()



        
  def createDefaultSettings(self):  
    """ Constructs a default database from the code.
    """
    restPaths = ['']
    for name in self.defaultHosts:
         setDefault = True if name == 'Central' else False
         self.saveHost(name, self.defaultHosts[name], False, setDefault)    
    self.savePaths(restPaths, "REST")


    
  
  def getHostNameAddressDictionary(self):
    """ Queries the database for hosts and creates
        a dictionary of key 'name' and value 'address'
    """
    self.database.beginGroup(hostTag)
    hostDict = {}        
    for childName in self.database.childGroups():
        hostDict[self.database.value(childName +"/"+ hostNameTag)] = self.database.value(childName +"/"+ hostAddressTag)
    self.database.endGroup()
    return hostDict



  
  def saveHost(self, hostName, hostAddress, isModifiable=True, isDefault=False):
    """ Writes host to the QSettings.ini database.
    """
    
    hostDict = self.getHostNameAddressDictionary()
    hostNameFound = False

    
    # Check to see if its a valid http URL, modify if not
    if not hostAddress.startswith("http://") and not hostAddress.startswith("https://"):
        hostAddress ="http://" + hostAddress

        
    # Check if the host name exists.
    for name in hostDict:
        hostNameFound = True if str(name).lower() == str(hostName).lower() else False 

        
    # Check for blanks, return warning window if there are any.
    if hostName == "" or hostAddress == "":
       blanks = [] 
       if hostName == "": 
           blanks.append("Name")
       if hostAddress == "": 
           blanks.append("URI")
       
       blankTxt = ""
       for i in range(0, len(blanks)):
            blankTxt += blanks[i]
            if i<len(blanks)-1: blankTxt+=", "
            
       qt.QMessageBox.warning( None, "Save Host", "Please leave no text field blank (%s)"%(blankTxt))
       return False    

    
    # Return warning window if host name already used.
    elif hostNameFound == True:
       qt.QMessageBox.warning( None, "Save Host", hostName + " is a name that's already in use.")
       hostFound = False
       return False

    
    # Otherwise, save.
    else:
       self.database.setValue(hostTag + hostName + "/" + hostNameTag, hostName)
       self.database.setValue(hostTag + hostName + "/" + hostAddressTag, hostAddress)

       # Don't write over default hosts.
       for defaultHostName in self.defaultHosts:
           if hostName.strip("") == defaltHostName.strip(""):
               isModifiable = False
               break

       # Is modifiable.
       self.database.setValue(hostTag + hostName + "/" + hostIsModifiableTag, isModifiable)

       # Is default.
       self.database.setValue(hostTag + hostName + "/" + hostIsDefaultTag, isDefault)

       # Curr user.
       self.database.setValue(hostTag + hostName + "/" + hostCurrUserTag, "")
       return True



    
  def savePaths(self, paths, pathType = "REST"): 
    """ As stated.
    """
    if pathType == "REST":
        currTag = RESTPathTag       
    for path in paths:
        self.database.setValue(pathTag + currTag, path)



          
  def getPath(self, pathType = "REST"):
    """ As stated.
    """
    if pathType == "REST":
        currTag = RESTPathTag      
    return self.database.value(pathTag + currTag, "")   



  
  def deleteHost(self, hostName): 
    """ As stated.
    """
    if self.database.value(hostTag + hostName + "/" + hostIsModifiableTag, ""):
        self.database.remove(hostTag + hostName)
        return True
    return False



    
  def setDefault(self, hostName):
    """ As stated.
    """
    self.database.beginGroup(hostTag)      
    for childName in self.database.childGroups():
        self.database.setValue(childName +"/"+ hostIsDefaultTag, False)
    self.database.setValue(hostName +"/"+ hostIsDefaultTag, True)
    self.database.endGroup()



    
  def isDefault(self, hostName):
    """ As stated.
    """   
    dbVal =  '%s'%(self.database.value(hostTag + hostName + "/" + hostIsDefaultTag, ""))
    if '1' in dbVal or 'True' in dbVal: 
        return True
    return False 



  
  def isModifiable(self, hostName):
    """ As stated.
    """
    title = unicode(str(self.database.value(hostTag + hostName + "/" + hostIsModifiableTag, "")))
    import unicodedata
    return unicodedata.normalize('NFKD', title).encode('ascii','ignore')



  
  def getAddress(self, hostName):
    """ As stated.
    """
    return self.database.value(hostTag + hostName + "/" + hostAddressTag, "")



  
  def setCurrUsername(self, hostName, username):
    """ As stated.
    """
    self.database.beginGroup(hostTag)  
    self.database.setValue(hostName +"/" + hostCurrUserTag, username)
    self.database.endGroup()



    
  def getCurrUsername(self, hostName):
    """ As stated.
    """
    return self.database.value(hostTag + hostName + "/" + hostCurrUserTag, "")

  

        
  def addHosts(self):
      """ Adds and stores the entered host
      """

      # Clear drowpdown.
      self.browser.XnatLoginMenu.hostDropdown.clear()

      # Populate dropdown.
      hostDict = self.browser.settings.getHostNameAddressDictionary()
      for name in hostDict:     
          self.browser.XnatLoginMenu.hostDropdown.addItem(name)
          
          
      # Loop through to find default host
      if not self.browser.XnatLoginMenu.currHostName:
          for i in range(0, len(hostDict.keys())):    
              if int(self.browser.settings.isDefault(hostDict.keys()[i]))>0:
                  self.browser.XnatLoginMenu.hostDropdown.setCurrentIndex(i)
                  self.browser.XnatLoginMenu.currHostName = hostDict.keys()[i]
                  break  
