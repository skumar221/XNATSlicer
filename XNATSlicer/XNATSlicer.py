
#-------------------------
# Widget path needs to be globally recognized by python
#-------------------------
import os, inspect, sys
WIDGETPATH = os.path.normpath(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe()))[0])))
WIDGETPATH = os.path.join(WIDGETPATH, "XNATSlicerLib")
sys.path.append(WIDGETPATH)

from XNATFileInfo import *
from XNATAddProjEditor import *
from XNATLoadWorkflow import *
from XNATUtils import *
from XNATInstallWizard import *
from XNATScenePackager import *
from XNATSessionManager import *
from XNATTimer import *
from XNATSettings import *
from XNATTreeView import *
from XNATCommunicator import *
from XNATLoginMenu import *
from XNATButtons import *
from XNATView import *
from XNATPopup import *
from DICOMLoadWorkflow import *
from SceneLoadWorkflow import *
from FileLoadWorkflow import *



comment = """
"""






class XNATSlicer:
  def __init__(self, parent):

      parent.title = "XNATSlicer"
      parent.categories = ["XNATSlicer"]
      parent.dependencies = []
      parent.contributors = ["Sunil Kumar (WashU-St. Louis, Dan Marcus (WashU-St. Louis), Steve Pieper (Isomics)"] 
      parent.helpText = """ The XNATSlicer Browser 1.0"""
      parent.acknowledgementText = """Sunil Kumar - NRG - kumars@mir.wustl.edu""" 
      self.parent = parent
      
      # Add this test to the SelfTest module's list for discovery when the module
      # is created.  Since this module may be discovered before SelfTests itself,
      # create the list if it doesn't already exist.
      try:
          slicer.selfTests
      except AttributeError:
          slicer.selfTests = {}
          slicer.selfTests['XNATSlicer'] = self.runTest
          
      def runTest(self):
          tester = XNATSlicerTest()
          tester.runTest()

#
# qXNATSlicerWidget
#




class XNATSlicerWidget:
    def __init__(self, parent = None):
      if not parent:
          self.parent = slicer.qMRMLWidget()
          self.parent.setLayout(qt.QVBoxLayout())
          self.parent.setMRMLScene(slicer.mrmlScene)
      else:
          self.parent = parent
      if not parent:
          self.setup()
          self.parent.show()
        
      self.utils = XNATUtils()    
      self.layout = self.parent.layout()


      
      #--------------------------------
      # Xnat settings
      #--------------------------------
      self.settings = XNATSettings(slicer.qMRMLWidget(), self.utils.utilPath, self)


      
      #--------------------------------
      # Login Menu
      #--------------------------------
      self.XNATLoginMenu = XNATLoginMenu(parent = self.parent, browser = self)  


      
      #--------------------------------
      # Viewer
      #--------------------------------
      self.XNATView = XNATTreeView(parent = self.parent, browser = self)  


      
      #--------------------------------
      # XNAT Buttons
      #--------------------------------
      self.XNATButtons = XNATButtons(self.parent, browser=self)  


      
      #--------------------------------
      # Popups
      #--------------------------------
      self.statusPopup = None
      self.progressPopup = None
      self.downloadPopup = XNATDownloadPopup(browser = self)
      #self.uploadPopup = XNATDownloadPopup(browser = self)


      
      #--------------------------------
      # Layouts
      #--------------------------------
      self.browserLayout = None
      self.loginLayout = None
      self.XNATViewLayout = qt.QGridLayout()



      #--------------------------------
      # LoadWorkflows
      #--------------------------------
      self.SceneLoadWorkflow = SceneLoadWorkflow(self)
      self.FileLoadWorkflow = FileLoadWorkflow(self)
      self.DICOMLoadWorkflow = DICOMLoadWorkflow(self)

      
      
      #--------------------------------
      # Init gui
      #--------------------------------
      self.initGUI()


      
      #--------------------------------
      # Listeners/observers from gui interaction
      #--------------------------------
      slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.sceneClosedListener)
      slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndImportEvent, self.sceneImportedListener)
      self.parent.show()


      

      
    def onReload(self,moduleName="XNATSlicer"):
      """Generic reload method for any scripted module.
      ModuleWizard will subsitute correct default moduleName.
      """
      import imp, sys, os, slicer
    
      widgetName = moduleName + "Widget"
    
      # reload the source code
      # - set source file path
      # - load the module to the global space
      filePath = eval('slicer.modules.%s.path' % moduleName.lower())
      p = os.path.dirname(filePath)
      if not sys.path.__contains__(p):
        sys.path.insert(0,p)
      fp = open(filePath, "r")
      globals()[moduleName] = imp.load_module(
          moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
      fp.close()
    
      # rebuild the widget
      # - find and hide the existing widget
      # - create a new widget in the existing parent
      parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
      for child in parent.children():
        try:
          child.hide()
        except AttributeError:
          pass
      # Remove spacer items
      item = parent.layout().itemAt(0)
      while item:
        parent.layout().removeItem(item)
        item = parent.layout().itemAt(0)
      # create new widget inside existing parent
      globals()[widgetName.lower()] = eval(
          'globals()["%s"].%s(parent)' % (moduleName, widgetName))
      globals()[widgetName.lower()].setup()



      
    def onReloadAndTest(self,moduleName="ScriptedExample"):
      try:
        self.onReload()
        evalString = 'globals()["%s"].%sTest()' % (moduleName, moduleName)
        tester = eval(evalString)
        tester.runTest()
      except Exception, e:
        import traceback
        traceback.print_exc()
        qt.QMessageBox.warning(slicer.util.mainWindow(), 
            "Reload and Test", 'Exception!\n\n' + str(e) + "\n\nSee Python Console for Stack Trace")
    


        
    def sceneClosedListener(self, caller, event):
        """Actions for when the user closes a scene from the GUI.
        """ 
        #print("'Close Scene' called. Resetting XNAT session data.")    
        self.XNATView.sessionManager.clearCurrentSession()  



        
    def sceneImportedListener(self, caller, event): 
        """Actions for when the user imports a scene from the GUI.
           NOTE: This technically is not used, as the user must refer to files from an 
           XNAT location. Nonetheless, it is implemented in the event that it is needed.
        """
        if self.XNATView.lastButtonClicked == None:
            #print("'Import Data' called. Resetting XNAT session data.")
            self.XNATView.sessionManager.clearCurrentSession() 
    

            
            
    def initGUI(self):  

        self.XNATLoginMenu.initGUI()
        
        #--------------------------------
        # Login Section
        #--------------------------------
        loginCollapsibleButton = ctk.ctkCollapsibleButton()
        loginCollapsibleButton.text = "XNAT Login"

        
        #--------------------------------
        # Browser Section
        #--------------------------------
        browserCollapsibleButton = ctk.ctkCollapsibleButton()
        browserCollapsibleButton.text = "XNAT TreeView"

        

        
        #--------------------------------
        # Add all sections to parent layout.
        #--------------------------------
        self.layout.addWidget(loginCollapsibleButton)
        self.layout.addWidget(browserCollapsibleButton)

        
        #--------------------------------
        # Define section layouts.
        #--------------------------------
        self.loginLayout = qt.QVBoxLayout(loginCollapsibleButton)
        self.browserLayout = qt.QVBoxLayout(browserCollapsibleButton) 


        
        #--------------------------------
        # XNAT Window
        #--------------------------------
        self.viewerLayout = qt.QVBoxLayout()
        self.cleanTempDir(500)


        
        #--------------------------------
        # Load/Save button
        #--------------------------------
        self.buttonColumnLayout = qt.QVBoxLayout()
        self.buttonColumnLayout.addWidget(self.XNATButtons.buttons['load'])#, 2, 0)
        self.buttonColumnLayout.addWidget(self.XNATButtons.buttons['save'])#, 0, 0) 
        self.buttonRowLayout = qt.QHBoxLayout()
        self.buttonRowLayout.addWidget(self.XNATButtons.buttons['delete'])
        self.buttonRowLayout.addSpacing(15)
        self.buttonRowLayout.addWidget(self.XNATButtons.buttons['addProj'])
        self.buttonRowLayout.addStretch()


        
        #--------------------------------
        # XNATViewer
        #--------------------------------
        self.XNATViewLayout.addWidget(self.XNATView.viewWidget, 0, 0)
        self.XNATViewLayout.addLayout(self.buttonColumnLayout, 0, 1)
        self.XNATViewLayout.addLayout(self.buttonRowLayout, 1, 0)
        

        
        #--------------------------------
        # Apply to globals
        #--------------------------------      
        self.loginLayout.addLayout(self.XNATLoginMenu.loginLayout)
        self.browserLayout.addLayout(self.XNATViewLayout)



        
        
    def cleanTempDir(self, maxSize):
        """ Empties contents of the temp directory based upon maxSize
        """
        import math
        folder = self.utils.tempPath
        folder_size = 0
        

        # Loop through files to get file sizes.
        for (path, dirs, files) in os.walk(folder):
          for file in files:
            folder_size += os.path.getsize(os.path.join(path, file))
        print ("XNATSlicer Data Folder = %0.1f MB" % (folder_size/(1024*1024.0)))


        # If the folder size exceeds limit, remove contents
        folder_size = math.ceil(folder_size/(1024*1024.0))
        if folder_size > maxSize:
            self.utils.removeFilesInDir(self.utils.tempPath)    
            self.utils.removeFilesInDir(self.utils.tempUploadPath)   




                
    def beginXNAT(self):
        """ Opens the view class linked to the XNATRestAPI
        """
        

        # Can the relevant libraries be imported?
        print("XNATSlicer Module: Seeing if SSL is installed...")
        try:      
            import ssl
            httplib.HTTPSConnection
            print("XNATSlicer Module: SSL is installed!")

            
        # If not, kick back OS error
        except Exception, e:
            strs = "XNATSlicer is currently not is supported for this operating system (%s).  XNATSlicer currently works on the following operating systems: %s."%(self.utils.osType, 'Win64')
            print("XNATSlicer Module: %s"%(strs))
            qt.QMessageBox.warning(slicer.util.mainWindow(), "Unsupported OS", "%s"%(strs))
            return
                

        # Init communicator.
        self.XNATCommunicator = XNATCommunicator(browser = self, 
                                server = self.settings.getAddress(self.XNATLoginMenu.hostDropdown.currentText), 
                                user = self.XNATLoginMenu.usernameLine.text, password=self.XNATLoginMenu.passwordLine.text, 
                                cachedir = self.utils.pyXNATCache)


        # Begin communicator
        try:
            self.XNATView.begin()
        except Exception, e:
            print("XNATSlicer Module: %s"%(str(e)))
            qt.QMessageBox.warning(slicer.util.mainWindow(), "Login error!", "%s"%('There appears to be a login error.'))



    
class XNATSlicerTest(unittest.TestCase):
    """
    This is the test case for your scripted module.
    """
    
    def delayDisplay(self,message,msec=1000):
      """This utility method displays a small dialog and waits.
      This does two things: 1) it lets the event loop catch up
      to the state of the test so that rendering and widget updates
      have all taken place before the test continues and 2) it
      shows the user/developer/tester the state of the test
      so that we'll know when it breaks.
      """
      print(message)
      self.info = qt.QDialog()
      self.infoLayout = qt.QVBoxLayout()
      self.info.setLayout(self.infoLayout)
      self.label = qt.QLabel(message,self.info)
      self.infoLayout.addWidget(self.label)
      qt.QTimer.singleShot(msec, self.info.close)
      self.info.exec_()
    
    def setUp(self):
      """ Do whatever is needed to reset the state - typically a scene clear will be enough.
      """
      slicer.mrmlScene.Clear(0)
    
    def runTest(self):
      """Run as few or as many tests as needed here.
      """
      self.setUp()
      self.test_XNATSlicer1()
    
    def test_XNATSlicer1(self):
      """ Ideally you should have several levels of tests.  At the lowest level
      tests sould exercise the functionality of the logic with different inputs
      (both valid and invalid).  At higher levels your tests should emulate the
      way the user would interact with your code and confirm that it still works
      the way you intended.
      One of the most important features of the tests is that it should alert other
      developers when their changes will have an impact on the behavior of your
      module.  For example, if a developer removes a feature that you depend on,
      your test should break so they know that the feature is needed.
      """
    
      self.delayDisplay("Starting the test")
      #
      # first, get some data
      #
      import urllib
      downloads = (
          ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
          )
    
      for url,name,loader in downloads:
        filePath = slicer.app.temporaryPath + '/' + name
        if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
          print('Requesting download %s from %s...\n' % (name, url))
          urllib.urlretrieve(url, filePath)
        if loader:
          print('Loading %s...\n' % (name,))
          loader(filePath)
      self.delayDisplay('Finished with download and loading\n')
    
      volumeNode = slicer.util.getNode(pattern="FA")
      logic = XNATSlicerLogic()
      self.assertTrue( logic.hasImageData(volumeNode) )
      self.delayDisplay('Test passed!')
