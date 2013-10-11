from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys

from XnatSettingsWindow import *



comment = """
XnatSettings is the class that manages storable settings for the
XnatSlicer module.  The class is activated by clicking the wrench
icon in the XnatSlicer browser.  XnatSettings utilizes the qt.QSettings
object to write to a settings database called 'XnatSettings.ini'.  As
the formate of the database indicates, the storage method is .ini, which
utilizes key-value pairs under a single header.


Ex:

[Central]
FullName=Central
Address=https://central.xnat.org
IsModifiable=False
CurrUser=user
IsDefault=True


TODO:
"""


#--------------------
# Global tags.  Do not Delete.
#--------------------
hostTag = 'Hosts'
hostNameTag = 'FullName'
hostAddressTag =   'Address'
hostUsernameTag = 'Username'
hostIsModifiableTag = 'IsModifiable'
hostIsDefaultTag = 'IsDefault'
hostCurrUserTag = 'CurrUser'
RESTPathTag = 'RESTPath'
pathTag = 'Paths'



class XnatSettings:
  """ Manager for handing the settings file.  Stored in QSettings standard through
      'XnatSettings.ini'
  """



  
  def __init__(self, parent = None, rootDir = None, browser = None):    
    """ Init function.
    """
    if not parent:
      self.parent = slicer.qMRMLWidget()
    else:
      self.parent = parent   
      
    self.browser = browser
    self.filepath = os.path.join(rootDir, 'XnatSettings.ini')

    #--------------------
    # OS specific database settings
    #--------------------
    dbFormat = qt.QSettings.IniFormat 

        
    self.database = qt.QSettings(self.filepath, dbFormat)
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
    """ Constructs a default database based on
        the 'self.defaultHosts' parameter.
    """
    restPaths = ['']
    for name in self.defaultHosts:
         default = True if name == 'Central' else False
         modifiable = True if name != 'Central' else False
         print modifiable, name
         self.saveHost(name, self.defaultHosts[name], isModifiable = modifiable, isDefault = default)    
    self.savePaths(restPaths, "REST")


    
  
  def getHostNameAddressDictionary(self):
    """ Queries the database for hosts and creates
        a dictionary of key 'name' and value 'address'
    """
    hostDict = {}        
    for key in self.database.allKeys():
        if hostAddressTag in key:
            hostDict[key.split("/")[0].strip()] = self.database.value(key)
    return hostDict



  
  def saveHost(self, hostName, hostAddress, isModifiable=True, isDefault=False):
    """ Writes host to the QSettings.ini database.
    """
    
    hostDict = self.getHostNameAddressDictionary()
    hostNameFound = False


    
    #--------------------
    # Check to see if 'hostAddress' is a valid http URL, 
    # modify if not.
    #--------------------
    if not hostAddress.startswith("http://") and not hostAddress.startswith("https://"):
        hostAddress ="http://" + hostAddress



    #--------------------
    # Check if the host name exists.
    #--------------------
    for name in hostDict:
        hostNameFound = True if str(name).lower() == str(hostName).lower() else False 



    #--------------------
    # If there are blank fields, return warning window...
    #--------------------
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

    

    #--------------------
    # Else if the host name is already used, return warning window, then exit...
    #--------------------
    elif hostNameFound == True and isModifiable == True:
       qt.QMessageBox.warning( None, "Save Host", hostName + " is a name that's already in use.")
       hostFound = False
       return False


    #--------------------
    # Otherwise, save host.
    #--------------------
    else:
        #
        # Remove existing.
        #
        self.database.remove(hostName)
        #
        # Start group.
        #
        self.database.beginGroup(hostName)
        self.database.setValue(hostNameTag, hostName)
        self.database.setValue(hostAddressTag, hostAddress)
        #
        # Set isModifiable.
        #
        self.database.setValue(hostIsModifiableTag, str(isModifiable))
        #
        # Set currUser.
        #
        self.database.setValue(hostCurrUserTag, "")
        #
        # Set isDefault to 'False' (first pass)
        #
        self.database.setValue(hostIsDefaultTag, str(False))
        self.database.endGroup()
        #
        # (second pass) conuct the setDefault function.
        #
        if isDefault: 
            self.setDefault(hostName)
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
    if self.database.value(hostName + "/" + hostIsModifiableTag, ""):
        self.database.remove(hostName)
        return True
    return False



    
  def setDefault(self, hostName):
    """ As stated.
    """

    #--------------------
    # Cycle through database...
    #--------------------
    for key in self.database.allKeys():
        #
        # Find keys that have the 'isDefault' tag (all of them)...
        #
        if hostIsDefaultTag in key:
            #
            # If there's a match in with hostName, then 
            # save the 'setDefault' to database.
            #
            tHost = key.split("/")[0].strip()
            retVal = True if hostName == tHost else False
            self.database.beginGroup(tHost)
            self.database.setValue(hostIsDefaultTag, str(retVal))
            self.database.endGroup()



    
  def getDefault(self):
    """ As stated.  Cycle through all
        database keys to find the default hosts.
    """   
    for key in self.database.allKeys():
        if hostIsDefaultTag in key and self.database.value(key) == 'True':
            return key.split("/")[0].strip()



    
  def isDefault(self, hostName):
    """ As stated.  Determines if a given host name
        is also a defaulted host name.
    """   

    self.database.beginGroup(hostName)
    dbVal =  '%s'%(self.database.value(hostName + "/" + hostIsDefaultTag, ""))
    dbVal = dbVal.lower()
    retVal = False
    if '1' in dbVal or 'true' in dbVal or dbVal == True: 
        retVal = True
    self.database.endGroup() 
    return retVal



  
  def isModifiable(self, hostName):
    """ As stated.  Determines if a given host
        can be modified by the user.
    """
    title = unicode(str(self.database.value(hostName + "/" + hostIsModifiableTag, "")))
    import unicodedata
    return unicodedata.normalize('NFKD', title).encode('ascii','ignore')



  
  def getAddress(self, hostName):
    """ As stated.
    """
    return self.database.value(hostName + "/" + hostAddressTag, "")



  
  def setCurrUsername(self, hostName, username):
    """ As stated.
    """
    self.database.beginGroup(hostName)  
    self.database.setValue(hostCurrUserTag, username)
    self.database.endGroup()



    
  def getCurrUsername(self, hostName):
    """ As stated.
    """
    for key in self.database.allKeys():
        if hostCurrUserTag in key and hostName in key:
            return self.database.value(key)
 


 
