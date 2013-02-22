from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys
import platform
from XNATUtils import *

from XNATUtils import textStatusBar


  #=============================================================================
  # XNATInstallWizard takes the user through the external libraries 
  # install process.  For now this is for Win64.  The wizard 
  # fetches the external libraries using setuptools and 
  # injects the runtime ssl files.
  # 
  # External libraries include: PyXNAT, lxml, httplib2
  # 
  # TODO : 
  #=============================================================================

class XNATInstallWizard(object):
    def __init__(self):
        self.utils = XNATUtils()
        self.wizard = qt.QWizard()
        self.os_system = ""
        self.os_release = ""
        self.os_machine = ""
        self.introDialog = qt.QMessageBox()
        self.introDialog.setStandardButtons(qt.QMessageBox.Ok | 
                                            qt.QMessageBox.Cancel)
        self.introDialog.setIcon(2)
        self.introDialog.setDefaultButton(qt.QMessageBox.Ok)
        self.introDialog.setText("Before you can browse XNAT, " + 
                                 "the module will install the necessary " + 
                                 "Python libraries. After completion, " + 
                                 "you won't see this wizard again.")            
        self.introDialog.connect('buttonClicked(QAbstractButton*)', 
                                 self.introDialog_next)
        self.checkPermissionsDialog = qt.QMessageBox()
        self.checkPermissionsDialog.setTextFormat(1)
        self.checkPermissionsDialog.setIcon(2)
        self.checkPermissionsDialog.setStandardButtons(qt.QMessageBox.Ok | 
                                                       qt.QMessageBox.Cancel)
        self.checkPermissionsDialog.setDefaultButton(qt.QMessageBox.Ok)
        self.permissionsText = ("Please make sure you have " + 
                                "FULL read/write permissions " + 
                                "for the Slicer install directory '<b>%s</b>'."%(str(slicer.app.slicerHome)) + 
                                "\n\nInstructions on how to do this " + 
                                "are here: <a href=\"http://www.slicer.org/slicerWiki/index.php/Documentation/4.2/Extensions/XNATSlicer\">http://www.slicer.org/slicerWiki/index.php/Documentation/4.2/Extensions/XNATSlicer</a>")
        self.checkPermissionsDialog.setText(self.permissionsText)
        self.checkPermissionsDialog.connect('buttonClicked(QAbstractButton*)', 
                                            self.checkPermissionsDialog_next)

        self.installStatusDialog = textStatusBar(slicer.qMRMLWidget())
        self.installStatusDialog.textField.setFixedSize(400, 600)
        self.restartDialog = qt.QMessageBox()
        self.restartDialog.setStandardButtons(qt.QMessageBox.Ok | 
                                              qt.QMessageBox.Cancel)
        
        self.restartDialog.setDefaultButton(qt.QMessageBox.Ok)
        self.restartDialog.setText("Slicer must restart in order " + 
                                   "for the new libraries to be recognized.")
        self.restartDialog.connect('buttonClicked(QAbstractButton*)', 
                                   self.restartDialog_next)
        
        self.fileDialog = qt.QFileDialog()
        self.fileDialog.setFileMode(4)
        
        self.installMessages = []
        self.installMessageLen = 30

        for i  in range(0, self.installMessageLen):
            self.installMessages.append("")
    
        self.installDir = None  
        self.isInstalled = True        
        self.installPaths = {}
        self.modPaths = {}
        
        self.copyFiles = []
        files = os.listdir(self.utils.pythonMods_Win64)
        for fileN in files:
            if fileN.find(".") > -1:
                self.copyFiles.append(os.path.join(self.utils.pythonMods_Win64, 
                                                   fileN))

    def pyXNATInstalled(self):
        
        slicerRoot = slicer.app.slicerHome
        if slicerRoot.lower().endswith('slicer-build'):
            pyRoot = os.path.join(os.path.dirname(slicer.app.slicerHome), 'python-build')
        else:
            pyRoot = os.path.join(slicer.app.slicerHome, 'lib/Python')
            
        pyRoot = self.utils.adjustPathSlashes(pyRoot)
        self.installPaths = {
            "pyRoot": pyRoot ,     
            "pyDLLs": os.path.join(pyRoot, 
                                   'DLLs'),
            "pylibs": os.path.join(pyRoot, 
                                   'libs'),      
            "pySitePackages": os.path.join(pyRoot, 
                                           'Lib/site-packages'),
            "pyDistUtils": os.path.join(pyRoot, 
                                        'Lib/distutils'),
            "pyDistUtils_Cmd": os.path.join(pyRoot, 
                                            'Lib/distutils/command'), 
            "pyDistUtils_Tests": os.path.join(pyRoot, 
                                              'Lib/distutils/tests'),
            "ez_setup_loc": os.path.join(pyRoot, "Lib")     
        }
        
        self.modPaths = {
                         "pyDLLs": os.path.join(self.utils.pythonMods_Win64, 
                                                "DLLs"),
                         "pylibs": os.path.join(self.utils.pythonMods_Win64, 
                                                "libs"),
                         "pyDistUtils": os.path.join(self.utils.pythonMods_Win64, 
                                                     "Lib/distutils"),
                         "pyDistUtils_Cmd": os.path.join(self.utils.pythonMods_Win64, 
                                                         "Lib/distutils/command"),
                         "pyDistUtils_Tests": os.path.join(self.utils.pythonMods_Win64, 
                                                           "Lib/distutils/tests"),
                         }
        #=======================================================================
        # STEP 1: See if directories even exist
        #=======================================================================
        for val in self.installPaths:
            if not os.path.exists(self.installPaths[val]): 
                return False
        #=======================================================================
        # STEP 2: Make sure the distutils directory has the correct files
        #=======================================================================
        dirList = os.listdir(self.modPaths["pyDistUtils"])
        for fileN in dirList:
            if not os.path.exists(os.path.join(self.installPaths["pyDistUtils"], 
                                               os.path.basename(fileN))):
                print ("DISTUTIL CHECK")
                return False   
        #=======================================================================
        # STEP 3: Make sure the libs directory has the correct files
        #=======================================================================
        dirList = os.listdir(self.modPaths["pylibs"])
        for fileN in dirList:
            if not os.path.exists(os.path.join(self.installPaths["pylibs"], 
                                               os.path.basename(fileN))):
                print ("FILE CHECK")
                return False    
        #=======================================================================
        # STEP 4: Make sure the libs directory has the correct files
        #===============================================================+=======
        dirList = os.listdir(self.modPaths["pyDLLs"])
        for fileN in dirList:
            if not os.path.exists(os.path.join(self.installPaths["pyDLLs"], 
                                               os.path.basename(fileN))):
                print ("DLL")
                return False
        return True
    
    def beginWizard(self):
        self.introDialog.show()
        
    def moveAndInstallLibs_win64(self):
        #=======================================================================
        # STEP 1: Create directories
        #=======================================================================
        for val in self.installPaths:
            if not os.path.exists(self.installPaths[val]):
                try: 
                    os.mkdir(self.utils.adjustPathSlashes(self.installPaths[val]))
                except Exception, e:
                    print ("makdDir error in XNATSlicer install: " + str(e))
                    self.installStatusDialog.textField.close()
                    s = "It looks like you didn't set your permissions correctly.  "
                    newText = "<font color=\"red\"><b>" + s + "</b></font>" + self.permissionsText
                    self.checkPermissionsDialog.setText(newText)
                    self.checkPermissionsDialog.show()
                    return
                self.installStatusDialog.showMessage("Creating directory: '%s'"%
                                                     (self.installPaths[val]))
        #=======================================================================
        # STEP 2: Move installer files to appropriate folders
        #=======================================================================
        import shutil
        for val in self.installPaths:
            try: 
                dirList = os.listdir(os.path.normpath(str(self.modPaths[val])))               
                for fileN in dirList:
                    if val == "pyDistUtils": print(fileN)
                    fileN = os.path.join(self.modPaths[val], fileN)
                    if fileN.find(".") > -1:
                        if not os.path.exists(os.path.join(self.installPaths[val], 
                                                           os.path.basename(fileN))):                        
                            shutil.copy(fileN, os.path.join(self.installPaths[val], 
                                                            os.path.basename(fileN)))
                            self.installStatusDialog.showMessage("Copying file '%s' to '%s' "%
                                                                 (fileN, os.path.join(self.installPaths[val], 
                                                                                      os.path.basename(fileN))))
                            print ("Copying file '%s' to '%s' "%
                                   (fileN, os.path.join(self.installPaths[val], 
                                                        os.path.basename(fileN))))
            except Exception, e:
                print "Warning: " + str(e) + "\n"  
        #=======================================================================
        # STEP 3: Move copy only files to their appropriate locations      
        #=======================================================================
        for fileN in self.copyFiles:
            if fileN.find("ez_setup.py") > -1:
                shutil.copy(fileN, os.path.join(self.installPaths["ez_setup_loc"], 
                                                os.path.basename(fileN)))
                self.installStatusDialog.showMessage("Copying file '%s' to '%s' "%
                                                     (fileN, os.path.join(self.installPaths[val], 
                                                                          os.path.basename(fileN))))
            else: 
                shutil.copy(fileN, os.path.join(self.installPaths["pyRoot"], os.path.basename(fileN)))
                self.installStatusDialog.showMessage("Copying file '%s' to '%s' "%
                                                     (fileN, os.path.join(self.installPaths[val], 
                                                                          os.path.basename(fileN))))
        #=======================================================================
        # STEP 4: Initiate subprocess calls
        #=======================================================================
        fileN = os.path.join(self.installPaths["pyRoot"], "ez_setup.py")
        self.installStatusDialog.showMessage("Running '%s' "%(fileN))
        import subprocess
        import ez_setup
        print ez_setup.main("")        
        slicer.app.processEvents()
        easyInst = os.path.join(self.installPaths["pyRoot"], "Scripts/easy_install")
        #=======================================================================
        # STEP 5: Construct and run command
        #=======================================================================
        command = "\"" + os.path.normpath(easyInst) + "\"" + " httplib2"      
        self.beginProcess(command, "httplib2")
        slicer.app.processEvents()

        command = ("\"" + os.path.normpath(easyInst) + "\"" 
                   + " " + "\"" + 
                   os.path.normpath(os.path.join(self.installPaths["pyRoot"], 
                                                                "lxml-2.2.8-py2.6-win-amd64.egg")) + "\"")
        self.beginProcess(command, "lxml")
        slicer.app.processEvents()#test

        command = "\"" + os.path.normpath(easyInst) + "\"" +  " pyxnat"
        self.beginProcess(command, "pyxnat")
        slicer.app.processEvents()
        self.restartDialog.show()


    def beginProcess(self, command, desc = ""):
        """"Utilizes qt.QProcess to execute commands.
        """
        process = qt.QProcess()
        self.installStatusDialog.showMessage("Installing '%s'..."%(desc))
        print "Calling '%s'."%(command)
        process.start(command)
        process.waitForFinished(360000)
        self.installStatusDialog.showMessage("Done installing '%s'!"%(desc))
        
    def introDialog_next(self, button):
        if (button.text.lower().find('yes') > -1 or 
            button.text.lower().find('ok') > -1):
            self.checkPermissionsDialog.show()
        elif (button.text.lower().find('no') > -1 or 
              button.text.lower().find('cancel')> -1):
            qt.QMessageBox.warning( None, 'XNAT Slicer', 
                                    'Without installing the Python libraries, ' + 
                                    'you will not be able to use XNAT Slicer!') 
            return  

    def checkPermissionsDialog_next(self, button):
        if (button.text.lower().find('yes') > -1 or 
            button.text.lower().find('ok') > -1):
            self.installStatusDialog.textField.show()
            if self.utils.osType == "win":
                self.moveAndInstallLibs_win64() 
            
        elif (button.text.lower().find('no') > -1 
              or button.text.lower().find('cancel')> -1):
            return

    def installStatusDialog_next(self, button):
        if (button.text.lower().find('yes') > -1 or 
            button.text.lower().find('ok') > -1):
            pass 
        elif (button.text.lower().find('no') > -1 or 
              button.text.lower().find('cancel')> -1):
            return
        
    def restartDialog_next(self, button):
        if (button.text.lower().find('yes') > -1 or 
            button.text.lower().find('ok') > -1):
            slicer.app.restart()
        elif (button.text.lower().find('no') > -1 or 
              button.text.lower().find('cancel')> -1):
            return

    
