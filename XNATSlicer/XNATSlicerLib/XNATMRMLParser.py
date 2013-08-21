from __main__ import vtk, ctk, qt, slicer

import os
import sys
import datetime
import time
import StringIO
import xml.etree.ElementTree as ET
import codecs
import shutil


from XNATFileInfo import *
from XNATUtils import *
from XNATScenePackager import *
from XNATTimer import *



comment = """
  XNATMRMLParser handles the parsing of the MRML file (XML-based) and either changes the paths of the remotely
  linked files to local directories, or the opposite.  In order to do this the file needs to be parsed and strings
  need to be manipulated.  
  
  One major issue here is the fact that Python 2.6.6's DOM parsers do not work on Windows.  Because of this, a 
  separate parser had to be written for the purpose of handling the MRML files.  In future releases of Slicer,
  assuming a later version of Python is installed, the hope is that we can use Python's native DOM parser,
  such as ElementTree.  When that happens, apped the following code to the include list above:
  
  import xml.etree.ElementTree as ET # currently does not work on Windows machines!
  
# TODO : 
"""



class XNATMRMLParser(object):
    """XNATMRMLParser is the class that parses and changes strings in a given .mrml file
    """



    
    def __init__(self, browser=None):    
        """ Descriptor
        """     
        self.browser = browser

        
        self.useCache = True
        self.useCacheMsgBox = None
        self.resetUseCacheMsgBox()
        
        self.tempLocalFileMap = None
        self.tempNewFilename = None
        self.cacheList = None
        
        self.TESTWRITE = False



        
    def changeValues(self, filename, newFilename, replaceValues, 
                     otherReplaceValues, removeOriginalFile = False, 
                     debug = True):
        """ Descriptor
        """

        
        print (self.browser.utils.lf(), "Changing values in the mrml.") 


        
        #------------------------
        # CONCATENATE ALL REPLACE VALUES
        #------------------------
        dicoms = []
        compLines = []
        if otherReplaceValues:
            replaceValues.update(otherReplaceValues)


            
        #------------------------
        # CREATE NEW MRML, BACKUP OLD
        #------------------------
        if filename == newFilename:
            bkpFN = filename.split(".")[0] + ".BKP"
            shutil.copy(filename,bkpFN)
            self.browser.utils.removeFile(filename)
            slicer.app.processEvents()
            filename = bkpFN


            
        #------------------------
        # INIT XML PARSER
        #------------------------
        elementTree = ET.parse(codecs.open(filename, encoding="UTF-8"))
        root = elementTree.getroot()
        iterator = root.getiterator()
        for subelement in iterator:
            if subelement.keys():
                for name, value in subelement.items():

                    
                    # if no strings to be changed, at least make sure filepaths are relative
                    if replaceValues == {}:
                        if os.path.basename(os.path.dirname(value)).lower() == "data":
                            #print self.browser.utils.lf() + " CHANGING NAME WITH DATA FORMAT: %s\tOLD: %s\tNEW:%s"%(subelement.attrib[name], value, "./Data/" + os.path.basename(value))
                            subelement.attrib[name] = "./Data/%s"%(os.path.basename(value))

                            
        print (self.browser.utils.lf(), "Writing a new element tree in the mrml.")


        
        #------------------------
        # write new mrml
        #------------------------
        elementTree.write(newFilename)     

        
        ### For testing purposes #############################################################
        #if self.TESTWRITE:
        #    z = open(filename,"r")
        #    oldlines = z.readlines()
        #    z.close()
        #    self.makeMrmlReadable(str(newFilename).split(".")[0]+"BEFORE", oldlines)
        #    self.makeMrmlReadable(str(newFilename).split(".")[0]+"AFTER", lines)      
        ######################################################################################


        
        #------------------------
        # return the dicom files, if necessary
        #------------------------
        print (self.browser.utils.lf(), "Done writing new mrml!")
        return {"dicoms": dicoms}        




        
    def localizeRemoteMRMLLinks(self, filename, downloadRemoteLinks = True):   
        """Used for the 'load' workflow.  This changes remote URIs (ones with the 
           http and https perefixes) .  
        """
        #------------------------
        # INIT DICTIONARY
        #------------------------
        self.cacheList = []
        fileNameKey = "fileName"
        fileListMemberKey = "fileListMember"
        remoteLocalFileMap = {}     
        compLines = []
        
        #------------------------
        # BEGIN MRML PARSING
        #------------------------
        elementTree = ET.parse(codecs.open(filename, encoding="UTF-8"))
        root = elementTree.getroot()
        iterator = root.getiterator()
        for subelement in iterator:
            if subelement.keys():
                for name, value in subelement.items():              
                    #===========================================================
                    # if the URI has a remote prefix, begin algorithm
                    #===========================================================            
                    if ("http://" in value) or ("https://" in value):
                        print self.browser.utils.lf() +  "\t\tName: '%s', Value: '%s'"%(name, value)  
                        #=======================================================
                        # removes the https://www.host.*** prefix
                        #=======================================================
                        _localURI =  self.browser.utils.adjustPathSlashes("%s%s"%(self.browser.utils.remoteFilePath,
                                                                          str(qt.QUrl(value).path()).split('archive')[1]))                 
                        print (self.browser.utils.lf() +  "GIVEN URL: " + value + 
                               " INITIAL PATH VALUE: " + _localURI)
                        #=======================================================
                        # creates a new local URI based on the module cache paths
                        #=======================================================
                        tempFileInfo = XNATFileInfo(remoteURI = value, localURI = _localURI)
                        newValue = tempFileInfo.localURI
                        #=======================================================
                        # special case for handling .raw files
                        #=======================================================
                        if _localURI.endswith("raw"): #special case                
                            newValue = os.path.join(os.path.join(tempFileInfo.localDirName, 
                                                                 tempFileInfo.basenameNoExtension), 
                                                    tempFileInfo.basename)                      
                            print (self.browser.utils.lf() + "FOUND RAW: " + self.browser.utils.adjustPathSlashes(newValue))
                        #=======================================================
                        # makes sure path slashes are all forward
                        #=======================================================
                        newValue = self.browser.utils.adjustPathSlashes(newValue)
                        if "win" in sys.platform: 
                            newValue = newValue.replace('\\', '/')                                                                           
                        #=======================================================
                        # if the value does not exist in the map...
                        #=======================================================
                        if not value in remoteLocalFileMap: 
                            #===================================================
                            # if no map value, create raw file map values
                            #===================================================
                            print (self.browser.utils.lf() +  ("DICTIONARY: Adding new val."))
                            if tempFileInfo.localURI.endswith('raw'):
                               print self.browser.utils.lf() +  "RAW EXTENSION"                               
                               remoteLocalFileMap[value] = "%s/%s/%s"%(tempFileInfo.localDirName,  
                                                                       os.path.basename(tempFileInfo.localURI).split(".")[0],
                                                                       os.path.basename(tempFileInfo.localURI)) 
                               remoteLocalFileMap[value + ".gz"] = "%s/%s%s"%(tempFileInfo.localDirName,  
                                                                              os.path.basename(tempFileInfo.localURI).split(".")[0], 
                                                                              ".raw.gz")
                            #===================================================
                            # for nodes other than raw files, define its map value 
                            #===================================================
                            else:
                               print self.browser.utils.lf() +  "OTHER EXTENSION"
                               remoteLocalFileMap[value] = tempFileInfo.localURI
                               tempFN = os.path.basename(tempFileInfo.localURI).split(".")[0]
                               tempFolder = os.path.basename(os.path.dirname(tempFileInfo.localURI))
                               print self.browser.utils.lf() +  "TEMPFN %s TEMPFOLDER %s"%(tempFN, tempFolder)
                               if tempFN == tempFolder:
                                   remoteLocalFileMap[value] = "%s%s"%(os.path.dirname(tempFileInfo.localURI), 
                                                                       os.path.basename(tempFileInfo.localURI).split(".")[1])
                            #===================================================
                            # debugging calls
                            #===================================================
                            print self.browser.utils.lf() +  "VALUE: %s and LOCAL %s"%(value, remoteLocalFileMap[value])                      
                            compLines.append("OLDWORD - READ1: '" + value + "'")
                            compLines.append("NEWWORD - READ1: '" + remoteLocalFileMap[value]+ "'\n")
                        #=======================================================
                        # set new mrml values
                        #=======================================================
                        subelement.attrib[name] = remoteLocalFileMap[value]
                    #===========================================================
                    # If there's a local prefix to the string, and it's in the data directory
                    # of the scene...    
                    #===========================================================
                    elif os.path.basename(os.path.dirname(value)).lower() == 'data':
                        ext = os.path.basename(value).split(".")[1]                   
                        newValue = "./Data/%s"%(os.path.basename(value))                
                        compLines.append("DATAOLD - READ2: '" + value + "'")
                        compLines.append("DATANEW - READ2: '" + newValue + "'\n")
                        subelement.attrib[name] = newValue
        #------------------------
        # GENERATE NEW FILENAME
        #------------------------
        newFilename = filename.replace("-remotized.mrml", self.browser.utils.localizedMRMLExtension + ".mrml") 
        newFilename = os.path.normpath(newFilename)
        #------------------------
        # CHANGES DIRECTOR CHARS FOR WINDOWS
        #------------------------
        if sys.platform.find("win") > -1:
            newFilename.replace('\\', '/')
        #------------------------
        # PRINT LINES FOR DEBUGGING
        #------------------------
        for line in compLines:
            print self.browser.utils.lf() +  "COMPLINE: " + line
        #------------------------
        # WRITE NEW MRML
        #------------------------
        slicer.app.processEvents()      
        elementTree.write(newFilename) 
        slicer.app.processEvents()
        
        #------------------------
        # MAKE, RETURN NEW FILENAMES
        #------------------------
        self.currLoadManager.newMRMLFile = newFilename
        print self.browser.utils.lf() +  "MRML PARSE FILENAME: " + filename     
        print "*****************" + self.browser.utils.lf() + "MRML PARSER: " + str(remoteLocalFileMap)
        return newFilename, remoteLocalFileMap


    
    
    def resetUseCacheMsgBox(self):
        """Message box workflow for using the cached files instead of redownloading."""
        self.useCacheMsgBox = qt.QMessageBox()
        self.useCacheMsgBox.setText("It appears that some of the DICOM images in this scene are locally cached.  "+
                                    "Would you like the widget to use them when possible?");
        self.useCacheMsgBox.setInformativeText("NOTE: This will potentially save you load time.");
        self.useCacheMsgBox.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        self.useCacheMsgBox.setDefaultButton(qt.QMessageBox.Yes)


        

    def toggleUseCache(self, button):
        """Toggles the "use cache" yes/no window."""
        newDict = {}
        if button.text.lower().find('yes') > -1: 
            self.useCache = True
        elif button.text.lower().find('no') > -1: self.useCache = False
        text = "User opted to use cache." if self.useCache else "User selected to opt out of using cache."
        print self.browser.utils.lf() + (text)

        for item in self.cacheList:
            self.tempLocalFileMap[str(item)] = None
        self.downloadRemoteURIs(self.tempLocalFileMap, self.tempNewFilename)


        

    def makeMrmlReadable(self, filename, lines = None):
        """Makes MRML files more readable to humans (i.e. linebreaks).
        """
        if not lines:
            z = open(filename,"r")
            lines = z.readlines()
            z.close()
            
        f = open(filename,'w' )
        for line in lines:
            words = line.split()
            for word in words:
                word = word.rstrip()
                if len(word)>0:     
                    #word = word.strip() 
                    f.write(word + '\n')
        f.close()

            
