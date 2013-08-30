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
      a file ('XnatSettings.ini')
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
    self.database.beginGroup(hostTag)      
    for childName in self.database.childGroups():
        self.database.setValue(childName +"/"+ hostIsDefaultTag, False)
    self.database.setValue(hostName +"/"+ hostIsDefaultTag, True)
    self.database.endGroup()



    
  def isDefault(self, hostName):

    dbVal =  '%s'%(self.database.value(hostTag + hostName + "/" + hostIsDefaultTag, ""))
    if '1' in dbVal or 'True' in dbVal: 
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

  

        
  def addHosts(self):
      """ Adds and stores the entered host
      """
      self.browser.XnatLoginMenu.hostDropdown.clear()
      hostDict = self.browser.settings.hostNameAddressDictionary()
      for name in hostDict:     
          self.browser.XnatLoginMenu.hostDropdown.addItem(name)
          
          
      # Loop through to find default host
      if not self.browser.XnatLoginMenu.currHostName:
          for i in range(0, len(hostDict.keys())):    
              if int(self.browser.settings.isDefault(hostDict.keys()[i]))>0:
                  self.browser.XnatLoginMenu.hostDropdown.setCurrentIndex(i)
                  self.browser.XnatLoginMenu.currHostName = hostDict.keys()[i]
                  break  
