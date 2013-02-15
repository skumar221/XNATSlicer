from __main__ import qt#, slicer

import os
import sys
from XNATUtils import *


#########################################################
#
# 
comment = """
  XNATFileInfo is a class that primarily deals with metadata and string 
  manipulation of various files pertinent to the XNATWorkflow.  Relevant 
  characteristics include: remoteURI (ie, its XNAT origin), localURI (where 
  it is cached locally), basename, extension, etc.  XNATFiles can be further 
  specialized for manipulation relative to that files use in the given 
  workflow -- uploading, downloading, etc.  
  
# TODO : Create children classes of XNATFileInfo -- right now it tries to 
handle everything.
"""
#
#########################################################

FILEINFO = {}

class XNATFileInfo(object):
    def __init__(self, remoteURI, localURI):

        localURI = localURI.replace("//", "/").replace("\\\\", "/").replace("\\", "/")
        # Full remote filename. (path included) Ex. for "http://foo/file.exe" returns "http://foo/file.exe"
        FILEINFO["remoteURI"]           = remoteURI
        FILEINFO["remoteURINoHost"]     = qt.QUrl(remoteURI).path()
        FILEINFO["remoteHost"]     = qt.QUrl(remoteURI).host()
        # Remote path (no filename). Ex. for "http://foo/file.exe" returns "http://foo"
        FILEINFO["remoteDirName"]          = os.path.dirname(remoteURI)
        # Filename only with extension. Ex. for "c:/foo/file.exe" returns "file.exe"
        FILEINFO["remoteBasename"]            = os.path.basename(remoteURI)
        
        # Full local filename. (path included) Ex. for "c:/download/file.exe" returns "c:/download/file.exe"
        FILEINFO["localURI"]            = localURI
        # Local path (no filename). Ex. for "c:/foo/file.exe" returns "c:/foo"
        FILEINFO["localDirName"]           = os.path.dirname(localURI)
        # Filename only with extension. Ex. for "c:/foo/file.exe" returns "file.exe"
        FILEINFO["localBasename"]             = os.path.basename(localURI)
        
        if FILEINFO["remoteBasename"] == FILEINFO["localBasename"]:
            FILEINFO["basename"] = os.path.basename(localURI)
            FILEINFO["basenameNoExtension"] = FILEINFO["basename"].split(".")[0]
            FILEINFO["extension"]           = "." + FILEINFO["basename"].split(".")[1]

    
    @property    
    def remoteURI(self):
        return FILEINFO["remoteURI"] 
    
    @property    
    def remoteURINoHost(self):
        return FILEINFO["remoteURINoHost"] 
    
    @property 
    def localURI(self):
        return FILEINFO["localURI"]
    
    @property 
    def remoteDirName(self):
        return FILEINFO["remoteDirName"]
    
    @property 
    def localDirName(self):
        return FILEINFO["localDirName"]
    
    @property 
    def basename(self):
        return FILEINFO["basename"]
    
    @property 
    def basenameNoExtension(self):
        return FILEINFO["basenameNoExtension"]
    
    @property 
    def extension(self):
        return FILEINFO["extension"]
    
    @property 
    def remoteHost(self):
        return FILEINFO["remoteHost"]
    
    @remoteHost.setter
    def remoteHost(self, remoteHost):
        FILEINFO["remoteHost"] = remoteHost


