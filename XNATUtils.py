from __future__ import with_statement
from __main__ import slicer, qt
import os
import zipfile
import tempfile
import platform
import inspect
import shutil

import datetime
import time 

XNATDirName = "data"
DEFAULTSCENENAME = "SlicerScene_"
DEFAULTXNATSAVELEVEL = "experiments"

MASTERPATH = os.path.join(os.path.dirname(os.path.abspath( __file__ )), XNATDirName)
#MASTERPATH = os.path.join(tempfile.gettempdir(), "XNATSlicer")

osType = ""
if slicer.app.os.lower() == "win": osType = "win"
elif slicer.app.os.lower() == "darwin" or slicer.app.os.lower() == "macosx": osType = "mac"
elif slicer.app.os.lower() == "linux": osType = "linux"

    
MODULEPATHS    =               {"home" : MASTERPATH,
                                "util": os.path.join(MASTERPATH, "Utils"),
                                "utilShared": os.path.join(MASTERPATH, "Utils" + os.sep + "SlicerShared"),
                                "remoteFile" : os.path.join(MASTERPATH, "RemoteFileCache"),
                                "project" : os.path.join(MASTERPATH, "Projects"),
                                "download" : os.path.join(MASTERPATH, "temp"),
                                "temp" : os.path.join(MASTERPATH, "temp"),
                                "tempUpload" : os.path.join(os.path.join(MASTERPATH, "temp"), "upload"),  
                                 "icons" : os.path.join(os.path.dirname(os.path.abspath( __file__ )), "icons"), 
                                 "pythonMods" : os.path.join(os.path.dirname(os.path.abspath( __file__ )), 
                                                             "python_mod" + os.sep + osType),
                                  "pyXNATCache" : os.path.join(MASTERPATH, "temp/pyxnatcache"),                        
                                }


LOCALMRMLEXTENSION = "-LOCALIZED"
CONDENSEDMRMLEXTENSION = "-CONDENSED"
REFERENCEDIRNAME = "reference/"

SLICERSHAREDDIRNAME = "Slicer-Shared"
SLICERSCENEDIRNAME = "Slicer"

SLICERHELPHERFOLDERS = [SLICERSHAREDDIRNAME]
REQUIREDSLICERFOLDERS = [SLICERSHAREDDIRNAME, SLICERSCENEDIRNAME]

RESTAPIFILE = "xdat-restClient-1.jar"
#REFERENCEDMRMLEXTENSION = "-REFERENCE"
REFERENCEDMRMLEXTENSION = ""
TEMPUPLOADPATH = os.path.join(MODULEPATHS["temp"], "upload")

DICOMEXTENSIONS  = [".dcm", ".ima"]
MRMLEXTENSIONS = [".mrml"]
SHARABLEEXTENSIONS = DICOMEXTENSIONS + [".nii", 
                                        ".nrrd", 
                                        ".img", 
                                        ".nhdr", 
                                        ".dc", 
                                        ".raw.gz", 
                                        ".gz", 
                                        ".vtk"]
DONOTCACHE = [".raw"]
PACKAGEEXTENSIONS = [".zip", ".mrb"]
DEFAULTPACKAGEEXTENSION = ".mrb"
OTHEREXTENSIONS = []

DECOMPRESSIBLES = [".gz", ".zip", ".tar"]

XNATROOT = "/data/archive"



#########################################################
#
# 
comment = """
  XNATUtils is the class that owns many of the default 
  directory strings and path manipulation efforts of the module.

# TODO : 
"""
#
#########################################################

class XNATUtils(object):
    
    def __init__(self, parent=None):        
        for item in MODULEPATHS:
            if not os.path.exists(MODULEPATHS[item]):       
                os.makedirs(MODULEPATHS[item])
                
        self.fontName = "Arial"
        self.fontSize = 10

        self.buttonSizeMed = qt.QSize(45, 45)
        self.buttonSizeSmall = qt.QSize(30, 30)
        
        self.xnatDepthDict = {0:"projects",
                              1:"subjects",
                              2:"experiments",
                              3:"scans"}
                
    @property
    def labelFontBold(self):
        return qt.QFont(self.fontName, self.fontSize, 100, False)
   
    @property
    def labelFont(self):
        return qt.QFont(self.fontName, self.fontSize, 10, False)
    
    @property
    def labelFontItalic(self):
        return qt.QFont(self.fontName, self.fontSize, 10, True)
     
    @property
    def XNATRoot(self):
        return XNATROOT
    
    @property
    def homePath(self):
        return MODULEPATHS["home"]
    
    @property
    def utilSharedPath(self):
        return MODULEPATHS["utilShared"]
    
    @property
    def iconPath(self):
        return MODULEPATHS["icons"]
    
    @property
    def utilPath(self):
        return MODULEPATHS["util"]
    
    @property
    def downloadPath(self):
        return MODULEPATHS["download"]
    
    @property
    def tempPath(self):
        return MODULEPATHS["temp"]
    
    @property
    def tempUploadPath(self):
        return MODULEPATHS["tempUpload"]
    
    @property
    def projectPath(self):
        return MODULEPATHS["project"]
    
    @property
    def remoteFilePath(self):
        return MODULEPATHS["remoteFile"] 
    
    @property
    def localizedMRMLExtension(self):
        return LOCALMRMLEXTENSION
    
    @property
    def referencedMRMLExtension(self):
        return REFERENCEDMRMLEXTENSION
    
    @property
    def condensedMRMLExtension(self):
        return REFERENCEDMRMLEXTENSION

    @property
    def defaultSceneName(self):
        return DEFAULTSCENENAME
    
    @property
    def referenceDirName(self):
        return REFERENCEDIRNAME
    
    @property
    def sharedDirName(self):
        return SLICERSHAREDDIRNAME
    
    @property
    def slicerDirName(self):
        return SLICERSCENEDIRNAME

    @property
    def defaultXNATSaveLevel(self):
        return DEFAULTXNATSAVELEVEL
        
    @property
    def RESTAPIFile(self):
        return RESTAPIFILE
    
    @property
    def requiredSlicerFolders(self):
        return REQUIREDSLICERFOLDERS
    
    @property
    def slicerHelperFolders(self):
        return slicerHelperFolders
    
    @property
    def pythonMods(self):
        return MODULEPATHS["pythonMods"]
    
    @property
    def osType(self):
        return osType
    
    @property
    def pyXNATCache(self):
        return MODULEPATHS["pyXNATCache"]
    
    @property
    def metadataFileName(self):
        return ".metadata"
    
    @property
    def defaultPackageExtension(self):
        return DEFAULTPACKAGEEXTENSION
    
    @property
    def packageExtensions(self):
        return PACKAGEEXTENSIONS
    
    @property
    def dicomDBBackupFN(self):
        return self.adjustPathSlashes(os.path.join(self.utilPath, "slicerDICOMDBBackup.txt")) 
    
    def removeDirsAndFiles(self, path):
        if os.path.exists(path):
            self.removeDir(path)
        if os.path.exists(path):
            os.rmdir(path)
           
    def appendFile(self, fileName, appendStr):
        name = os.path.splitext(fileName)[0]
        ext = os.path.splitext(fileName)[1]
        return name + appendStr + ext
    
    def removeDir(self, path, pattern=''):
        import re
        pattern = re.compile(pattern)
        if os.path.exists(path):
            for each in os.listdir(path):
                if pattern.search(each):
                    name = os.path.join(path, each)
                    try: os.remove(name)
                    except:
                        self.removeDir(name, '')
                        os.rmdir(name)
        else:
            print self.lf() + " ATTEMPTED TO REMOVE: %s but it does not exist!"%(path)
    
    def removeFilesInDir(self, theDir):
        for the_file in os.listdir(theDir):
            file_path = os.path.join(theDir, the_file)
            try:
                os.unlink(file_path)
                os.remove(file_path)
            except Exception, e:
                #print "Found directory '%s'. Removing files. Ref err: %s"%(file_path, str(e))
                if the_file.endswith("\\") or the_file.endswith("/"): 
                    self.removeFilesInDir(file_path)
     
    def shortenFileName(self, fn, maxLen = 20):
        basename = os.path.basename(fn)
        pre = basename.split(".")[0]
        if len(pre) > maxLen:
             baseneme = pre[0:8] + "..." + pre[-8:] + "." + basename.split(".")[1]
        return basename
    def removeFile(self, theFile):
        try:           
            os.unlink(theFile)
            os.remove(theFile)
        except Exception, e:
            pass
            #print "Cannot remove '%s' or it doesn't exist."%(theFile)
            
    def moveDirContents(self, srcDir, destDir, deleteSrc = True):
        newURIs = []
        #=======================================================================
        # MAKE DESTINATION DIR
        #=======================================================================
        if not os.path.exists(destDir): 
            os.mkdir(destDir)
        #=======================================================================
        # WALK THROUGH DIRECTORY       
        #=======================================================================
        for root, subFolders, files in os.walk(srcDir):
            for file in files:
                #===============================================================
                # id source folder and current URI
                #===============================================================
                srcFolder = os.path.basename(srcDir)
                currURI = os.path.join(root,file)
                newURI = os.path.join(destDir, file)
                #===============================================================
                # handle subdirs
                #===============================================================
                try:
                    #print (self.lf() + "ROOTSPLIT: " + str(root.split(srcFolder)))
                    folderBegin = root.split(srcFolder)[-1] 
                    if folderBegin.startswith("\\"): 
                        folderBegin = folderBegin[1:] 
                    if folderBegin.startswith("/"): 
                        folderBegin = folderBegin[1:]                 
                    if folderBegin and len(folderBegin) > 0:
                        newPath = os.path.join(destDir, folderBegin)
                        if not os.path.exists(newPath):
                            os.mkdir(newPath)
                        newURI = os.path.join(newPath, file)
                except Exception, e: 
                    print (self.lf() + "RootSplit Error: " + str(e))
                #===============================================================
                # send to dst                
                #===============================================================
                #print(self.lf() + " MOVING '%s' TO '%s'"%(currURI, newURI))
                shutil.move(currURI, newURI)
                newURIs.append(self.adjustPathSlashes(newURI))
        #=======================================================================
        # DELETE SOURCE HANDLING
        #=======================================================================
        if deleteSrc:
            if not srcDir.find(destDir) == -1:
                self.removeDirsAndFiles(srcDir)
        
        #print self.lf() +  "NEW URIS: " + str(newURIs)
        return newURIs
                                  
    def writeZip(self, packageDir, deleteFolders = False):
        zipURI = packageDir + ".zip"
        from contextlib import closing
        from zipfile import ZipFile, ZIP_DEFLATED
        import os
        # from: http://stackoverflow.com/questions/296499/how-do-i-zip-the-contents-of-a-folder-using-python-version-2-5
        assert os.path.isdir(packageDir)
        with closing(ZipFile(zipURI, "w", ZIP_DEFLATED)) as z:
            for root, dirs, files in os.walk(packageDir):
                for fn in files: #NOTE: ignore empty directories
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(packageDir)+len(os.sep):] #XXX: relative path
                    z.write(absfn, zfn)

        #slicer.app.processEvents()
        zipSize = os.path.getsize(zipURI)

        return zipURI
    
    def isSceneEmpty(self):
        #=======================================================================
        # GET THE CURRENT SCENE
        #=======================================================================
        currScene = slicer.app.mrmlScene()
        #=======================================================================
        # SEE IF THERE'S AT LEAST ONE STORABLE FILE
        #=======================================================================
        files = self.checkStorageNodeDirs(currScene)
        #=======================================================================
        # GET VOLUME NODES
        #=======================================================================
        volNodes = currScene.GetNodesByClass('vtkMRMLVolumeArchetypeStorageNode')
        #=======================================================================
        # IF NO STORAGE NODES OR VOLUME NODES
        #=======================================================================
        if len(files) == 0 and volNodes.GetNumberOfItems() == 0:
            return True
        #=======================================================================
        # IF NO URL WITH THE SCENE
        #=======================================================================
        if currScene.GetURL() == '':
            return True
        else: return False
    
    def checkStorageNodeDirs(self, currScene):
        """Determines if there's at least one storable node with at least one 
           filename associated with it. 
        """
        #=======================================================================
        # GET VOLUME STORAGE NODES
        #=======================================================================
        tempNode =  currScene.GetNodesByClass('vtkMRMLVolumeArchetypeStorageNode') # none GetItemAsObject(1)
        storageNode = None
        #=======================================================================
        # CYCLE THROUGH NODES, ID 'vtkMRMLVolumeArchetypeStorageNode', GET ONE OF THEM
        #=======================================================================
        for i in range(0,tempNode.GetNumberOfItems()):            
            if tempNode.GetItemAsObject(i).GetClassName() == 'vtkMRMLVolumeArchetypeStorageNode': 
                #print "Found the storage node!"
                storageNode = tempNode.GetItemAsObject(i)
                break
        #=======================================================================
        # GET FILENAMES ASSOCIATED WITH THE NODE
        #=======================================================================
        fileNames = []
        try: 
            for i in range(0, storageNode.GetNumberOfFileNames()):
                fileNames.append(storageNode.GetNthFileName(i))
        except Exception, e:
            pass
        return fileNames
    
    def writeDebugToFile(self, debugStr):
        f = open(os.path.join(self.homePath, "DebugLog.txt"), 'a')
        f.write(str(datetime.datetime.now()) + ": " + debugStr + "\n")            
        f.close()
        
    def isRecognizedFileExt(self, ext):
        if len(ext) > 0 and ext[0] != '.':   ext = "." + ext
        arr = (DICOMEXTENSIONS + 
               MRMLEXTENSIONS + 
               SHARABLEEXTENSIONS + 
               PACKAGEEXTENSIONS + 
               OTHEREXTENSIONS)
        for item in arr:
            if ext == item:
                return True
            elif ext.find(item)>-1:
                return True
            
        return False
    
#    def isSharable(self, ext = None):
#        return self.isExtension(ext, SHARABLEEXTENSIONS)
    
    def isExtension(self, ext, extList):      
        if len(ext) > 0 and ext[0] != '.':    ext = "." + ext
        for val in extList:
            if ext.lower().find(val.lower())>-1: return True
        return False
    
    def isDICOM(self, ext = None):
        return self.isExtension(ext, DICOMEXTENSIONS)
    
    def isMRML(self, ext = None):     
        return self.isExtension(ext, MRMLEXTENSIONS)
    
    def isSharable(self, ext = None, fullFileName = None):
       if ext:     
           return self.isExtension(ext, SHARABLEEXTENSIONS)
       else:
           for extVal in SHARABLEEXTENSIONS:
               if fullFileName.endswith(extVal): 
                   return True
           return False

    def isScenePackage(self, ext = None):
       return self.isExtension(ext, PACKAGEEXTENSIONS)
   
    

    def getParentPath(self, remotePath, levelName):
        """ Returns the parent path based on the entered level
        """ 
        remotePath = os.path.dirname(qt.QUrl(remotePath).path())
        pathLayers = remotePath.rsplit("/")
        i = 0
        for layer in pathLayers:
            if layer == levelName:
                i+=1
                break
            i+=1
        
        parentPath = ""
        for y in range(0,i):
            parentPath+=pathLayers[y] + "/"
        
        #print "PATH AT LAYER: " + parentPath
        return parentPath
    
    def isCurrSceneEmpty(self):
        """Determines if the scene is empty based on the visible node count.
        """
        #=======================================================================
        # GET PARAMS
        #=======================================================================
        visibleNodes = []    
        origScene = slicer.app.applicationLogic().GetMRMLScene()
        origURL = origScene.GetURL()
        origRootDirectory = origScene.GetRootDirectory()
        #=======================================================================
        # CYCLE THRU NODES TO GET VISIBLE NODES
        #=======================================================================
        for i in range(0, origScene.GetNumberOfNodes()):
            mrmlNode = origScene.GetNthNode(i);
            if mrmlNode:
                try:
                    #===========================================================
                    # get visible nodes
                    #===========================================================
                    if (str(mrmlNode.GetVisibility()) == "1" ):
                        #print "The %sth node of the scene is visible: %s"%(str(i), mrmlNode.GetClassName())
                        visibleNodes.append(mrmlNode)
                except Exception, e:
                    pass
        #print "NUMBER OF VISIBLE NODES: %s"%(str(len(visibleNodes)))        
        #=======================================================================
        # RETURN TRUE IF THERE ARE NO VISIBLE NODES, ELSE RETURN FALSE
        #=======================================================================
        if (len(visibleNodes) == 1) and (visibleNodes[0].GetClassName() == "vtkMRMLViewNode"):
            return True
        elif (len(visibleNodes) < 1):
            return True
        
        return False
  
    def doNotCache(self, filename):
        for ext in DONOTCACHE:
            if filename.endswith(ext):
                return True
        return False
    
    def isDecompressible(self, filename):
        for ext in DECOMPRESSIBLES:
            if filename.endswith(ext):
                return True
        return False
    
    def decompressFile(self, filename, dest = None):
        #print ("UNZIPPING %s"%(filename))
        
        if filename.endswith(".zip"):
            import zipfile
            z = zipfile.ZipFile(filename)      
            if not dest: dest = os.path.dirname(filename)
            z.extractall(dest)
        elif filename.endswith(".gz"):
            import gzip 
            a = gzip.GzipFile(filename, 'rb')
            content = a.read()
            a.close()                                            #open the file
            f = open(filename.split(".gz")[0], 'wb')
            f.write(content) # read and print the contents of the file      
            f.close()
      
    def lowerCaseAll(self, strList):
        for i in range(0, len(strList)):
            strList[i] = strList[i].lower()  
        return strList   

    def getCurrImageNodes(self, packageDir = None):
        #=======================================================================
        # GET CURR SCENE AND NODES
        #=======================================================================
        currScene = slicer.app.mrmlScene()
        ini_nodeList = currScene.GetNodes()
        #=======================================================================
        # INIT PARAMS
        #=======================================================================
        unmodifiedImageNodes = []
        modifiedImageNodes = []
        allImageNodes = []
        #=======================================================================
        # IF NO DIRECTORY GIVEN...
        #=======================================================================
        if not packageDir:
            
            #===================================================================
            # cycle through nodes
            #===================================================================
            for x in range(0,ini_nodeList.GetNumberOfItems()):
                nodeFN = None
                node = ini_nodeList.GetItemAsObject(x)
                try:              
                      #==============================================================
                      # see if node has a filename
                      #==============================================================
                      nodeFN = node.GetFileName()
                      #print "nodeFN: " + nodeFN
                except Exception, e:
                      pass 
                #===============================================================
                # if there is a filename...                 
                #===============================================================
                if nodeFN:
                    #===========================================================
                    # get extension
                    #===========================================================
                    nodeExt = '.' + nodeFN.split(".", 1)[1]                      
                    #print ("Determining if a modified image: %s and it's extension %s" %(nodeFN, nodeExt))
                    #===========================================================
                    # see if file is sharable
                    #===========================================================
                    if self.isSharable(nodeExt):
                        allImageNodes.append(nodeFN)
                        try:
                            #===================================================
                            # see if node has been modified since read, allocate
                            # to unmodified.
                            #===================================================
                            if not node.GetModifiedSinceRead():
                                 #print("Appending %s to unmodifiedImageNodes:" %(nodeFN))
                                 if unmodifiedImageNodes.count(nodeFN) == 0:
                                     unmodifiedImageNodes.append(nodeFN)
                        except Exception, e:
                            print "Unmodified node error: %s"%(str(e))
        #=======================================================================
        # ALLOCATE FOR MODIFIED IMAGE NODES
        #=======================================================================
        for _node in allImageNodes:
            if  unmodifiedImageNodes.count(_node) == 0:
                modifiedImageNodes.append(_node)   
                 
        return unmodifiedImageNodes, modifiedImageNodes, allImageNodes
    
    def getDateTimeStr(self):
            
        strList = str(datetime.datetime.today()).rsplit(" ")
        timeStr = strList[1]
        timeStr = timeStr.replace(":", " ")
        timeStr = timeStr.replace(".", " ")
        timeList = timeStr.rsplit(" ")
        shortTime = timeList[0]+ "-" + timeList[1]
        return strList[0] + "_" + shortTime
        
    def createSceneName(self):   
        strList = str(datetime.datetime.today()).rsplit(" ")
        timeStr = strList[1]
        timeStr = timeStr.replace(":", " ")
        timeStr = timeStr.replace(".", " ")
        timeList = timeStr.rsplit(" ")
        shortTime = timeList[0]+ "-" + timeList[1]
        tempFilename = self.defaultSceneName + self.getDateTimeStr()
        return tempFilename
            
    def adjustPathSlashes(self, str):
        return str.replace("\\", "/").replace("//", "/")

    def replaceForbiddenChars(self, fn, replaceStr=None):
        if not replaceStr: replaceStr = "_"
        fn = fn.replace(".", replaceStr)
        fn = fn.replace("/", replaceStr)
        fn = fn.replace("\\", replaceStr)
        fn = fn.replace(":", replaceStr)
        fn = fn.replace("*", replaceStr)
        fn = fn.replace("?", replaceStr)
        fn = fn.replace("\"", replaceStr)
        fn = fn.replace("<", replaceStr)
        fn = fn.replace(">", replaceStr)
        fn = fn.replace("|", replaceStr)
        return fn

    def getSlicerDirAtLevel(self, currDir, xnatLevel = DEFAULTXNATSAVELEVEL, findNearest = False):
        #=======================================================================
        # LOCAL VARS
        #=======================================================================
        slicerDir = ""
        counter = 0
        #print self.lf() + " CURR DIR: " + currDir
        #print self.lf() + " DEPTH DICT LENGHT: " + str(len(self.xnatDepthDict))
        #=======================================================================
        # METHOD 1: BASED ON CURRENT FOLDER LOCATION
        #=======================================================================
        if findNearest:
            currDir = os.path.dirname(currDir)
            pathStr = currDir.split("/")
            findCount = False
            counter = 0
            depthCounter = 0
            #===================================================================
            # cycle through path folders
            #===================================================================
            for p in pathStr:
                slicerDir += p + "/"
                #===============================================================
                # cycle through xnatDepthDict
                #===============================================================
                for key, value in self.xnatDepthDict.iteritems():
                    if value == p: 
                      depthCounter +=1
                #===============================================================
                # end of xnat hierarchy
                #===============================================================
                if depthCounter == len(self.xnatDepthDict):
                    #print "SLICERDIR: " + slicerDir
                    slicerDir += pathStr[counter+1]  
                    break
                counter+=1
        #=======================================================================
        # BASED ON XNATLEVEL (i.e., if xnatLevel = 'experiments')
        #=======================================================================
        else:
            pathStr = currDir.split("/")
            for val in pathStr:
                if len(val) >0:
                    slicerDir += val + "/"
                    if val == xnatLevel:
                        slicerDir += pathStr[counter+1]
                        break
                counter+=1   
        #=======================================================================
        # APPEND WITH THE SCICER RESOURCE
        #=======================================================================
        if not slicerDir.endswith("/"):
            slicerDir+="/"    
        slicerDir += "resources/%s/files/"%(self.slicerDirName) 
        #print "SLICERDIR2: " + slicerDir
        return slicerDir
    
    def lf(self, msg=""):
        """Returns the current line number in our program."""

        frame,filename,line_number,function_name,lines,index= inspect.getouterframes(inspect.currentframe())[1]
        #print(frame,filename,line_number,function_name,lines,index)
        returnStr = "\n"
        try:
            returnStr = "%s (%s) %s: %s"%(os.path.basename(filename), function_name, line_number, msg)
        except Exception, e:
            print "Line Print Error: " + str(e)
        return "\n" + returnStr
    
    def removeZeroLenStrVals(self, arr):
        for p in arr: 
            if (len(p)==0):
                arr.remove(p)
        
        return arr
    
    def splitXNATPath(self, path):
        dirNames = []
        dirTypes = []
        pathArr = self.removeZeroLenStrVals(path.strip().split("/"))
        startVal = 0
        # GET FOLDER NAMES 
        for i in range(0, len(pathArr)): 
            if (pathArr[i]=='project'):
                dirTypes.append[pathArr[i]]
                startVal = i+1
            if ((i-startVal)%2-1 == 0):
                dirNames.append(pathArr[i])
            else:
                dirTypes.append(pathArr[i])     
        return dirNames, dirTypes
    
    def getSaveTuple(self, filepath=None):
        saveLevelDir = None
        sharedDir = None
        slicerDir = None
        if filepath:
            lSplit, rSplit = filepath.split(self.defaultXNATSaveLevel + "/")
            saveLevelDir = (lSplit + self.defaultXNATSaveLevel + "/" + rSplit.split("/")[0])
            slicerDir = saveLevelDir + "/resources/" + self.slicerDirName + "/files"
            sharedDir = saveLevelDir + "/resources/" + self.sharedDirName + "/files"
        return saveLevelDir, slicerDir, sharedDir

    def checkArrayElementsAreEqual(self, iterator):
      try:
         iterator = iter(iterator)
         first = next(iterator)
         return all(first == rest for rest in iterator)
      except StopIteration:
         return True

    def makeXNATPathDictionary(self, path):
        pathDict = {"projects":None, "subjects":None, "experiments":None, "scans":None, "resources":None, "files":None}
        pathList = path.split("/")
        for i in range(0, len(pathList)):
            for k, v in self.xnatDepthDict.iteritems():
                if pathList[i] == v:
                    if (i+1) < len(pathList):
                        pathDict[pathList[i]] = pathList[i+1]
        return pathDict


     
class textStatusBar(object):
    def __init__(self, parent = None, overwriteMode = False, size = 7):
        
        self.textField = qt.QTextEdit()
        self.textField.setReadOnly(True)
        self.textField.setAcceptRichText(True)
        #self.textField.setFixedHeight(60)
        self.size = size 
        self.textField.setFont(qt.QFont("Arial", self.size, 0, False))
        self.overwriteMode = overwriteMode
        self.textField.setFixedHeight(60)
    
    def showMessage(self, text, italAll = False, boldAll = False, fontSize = 7):
        
#        if fontSize != self.size:
#            text = "<font size = " + str(fontSize) +  ">" + text + "</font>"        
#        if italAll: text = "<i>" +  text + "</i>"
#        if boldAll: text = "<b>" + text + "</b>"

        newText = text#.replace(" ", "")      
        if not self.overwriteMode: self.textField.append(newText)
        else: self.textField.setText(newText)


        #except Exception, e:
#    print ("PRINT FILE SIZE ERROR: %s"%(str(e)))
#raise

    def go(self, fileURIs):
        #print "GOING!"
        t = Thread(target=self.printFileSize, args=(fileURIs[0],))
        t.start()
