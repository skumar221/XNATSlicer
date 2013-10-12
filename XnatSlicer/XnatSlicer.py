import imp, os, inspect, sys, slicer



#
# Widget path needs to be globally recognized by Python.
# Appending to global path.
#
MODULE_PATH = os.path.normpath(os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe()))[0])))
#
# Inlcude testing folders.
#
sys.path.append(os.path.join(MODULE_PATH, 'Testing'))
#
# Include lib folder.
#
LIB_PATH = os.path.join(MODULE_PATH, "XnatSlicerLib")
sys.path.append(LIB_PATH)
#
# Include UI folder.
#
sys.path.append(os.path.join(LIB_PATH, 'ui'))
#
# Include utils folder.
#
sys.path.append(os.path.join(LIB_PATH, 'utils'))
#
# Include io folder.
#
sys.path.append(os.path.join(LIB_PATH, 'io'))



from XnatGlobals import *
from XnatFileInfo import *
from XnatAddProjEditor import *
from XnatLoadWorkflow import *
from XnatUtils import *
from XnatScenePackager import *
from XnatSessionManager import *
from XnatTimer import *
from XnatSettings import *
from XnatTreeView import *
from XnatIo import *
from XnatLoginMenu import *
from XnatButtons import *
from XnatView import *
from XnatPopup import *
from XnatDicomLoadWorkflow import *
from XnatSceneLoadWorkflow import *
from XnatFileLoadWorkflow import *
from XnatFilter import *
from XnatSlicerTest import *
from XnatError import *




comment = """
XnatSlicer.py contains the central classes for managing 
all of the XnatSlicer functions and abilities.  XnatSlicer.py
is the point where the module talks to Slicer, arranges the gui, and
registers it to the Slicer modules list.  It is where all of the 
XnatSlicerLib classes and methods come together.

TODO:
"""


class XnatSlicer:
  """ The class that ultimately registers the module
      with Slicer.
  """
  
  def __init__(self, parent):
      """ Init function.
      """

      #--------------------------------
      # Registers the title and relevant information
      # parameters to Slicer
      #--------------------------------
      parent.title = "XNATSlicer"
      parent.categories = ["XNATSlicer"]
      parent.dependencies = []
      parent.contributors = ["Sunil Kumar (Moka Creative, LLC), Dan Marcus (WashU-St. Louis), Steve Pieper (Isomics)"] 
      parent.helpText = """ The XNATSlicer 1.0"""
      parent.acknowledgementText = """Sunil Kumar for the Neuroinformatics Research Group - sunilk@mokacreativellc.com""" 
      self.parent = parent


      
      #--------------------------------
      # Add this test to the SelfTest module's list for discovery when the module
      # is created.  Since this module may be discovered before SelfTests itself,
      # create the list if it doesn't already exist.
      #--------------------------------
      try:
          slicer.selfTests
      except AttributeError:
          slicer.selfTests = {}
          slicer.selfTests['XnatSlicer'] = self.runTest
          
      def runTest(self):
          tester = XnatSlicerTest()
          tester.runTest()


          

class XnatSlicerWidget:
    """  The class that manages all of the XNATSlicer-specific
         libraries.
    """
    
    def __init__(self, parent = None):
        """ Init function.
        """
        if not parent:
            self.parent = slicer.qMRMLWidget()
            self.parent.setLayout(qt.QVBoxLayout())
            self.parent.setMRMLScene(slicer.mrmlScene)
        else:
            self.parent = parent
        if not parent:
            self.setup()
            self.parent.show()



        #--------------------------------
        # Init Xnat GLOBALS
        #--------------------------------
        self.GLOBALS = XnatGlobals() 


        
        #--------------------------------
        # Init Xnat Utils
        #--------------------------------
        self.utils = XnatUtils(self)   



        #--------------------------------
        # Construct all needed directories
        # if not there...
        #--------------------------------
        self.utils.constructNecessaryModuleDirectories()

        
        
        #--------------------------------
        # Set the layout
        #--------------------------------
        self.layout = self.parent.layout()

        
        
        #--------------------------------
        # Collapse the 'Data Probe' button.
        #--------------------------------
        dataProbeButton = slicer.util.findChildren(text='Data Probe')[0]
        dataProbeButton.setChecked(False)


        
        #--------------------------------
        # Xnat settings
        #--------------------------------
        self.settings = XnatSettings(slicer.qMRMLWidget(), self.GLOBALS.LOCAL_URIS['settings'], self)
        self.settingsPopup = XnatSettingsWindow(self)


            
        #--------------------------------
        # Xnat Communicator
        #--------------------------------
        self.XnatIo = XnatIo()


      
        #--------------------------------
        # Xnat Filter
        #--------------------------------
        self.XnatFilter = XnatFilter(self)
        

        
        #--------------------------------
        # Login Menu
        #--------------------------------
        self.XnatLoginMenu = XnatLoginMenu(parent = self.parent, MODULE = self)
        self.XnatLoginMenu.loadDefaultHost()   


      
        #--------------------------------
        # Viewer
        #--------------------------------
        self.XnatView = XnatTreeView(parent = self.parent, MODULE = self)  
        
        
        
        #--------------------------------
        # Xnat Buttons
        #--------------------------------
        self.XnatButtons = XnatButtons(self.parent, MODULE=self)  
        
        
        
        #--------------------------------
        # Popups
        #--------------------------------
        self.downloadPopup = XnatDownloadPopup(MODULE = self)
        #self.uploadPopup = XnatDownloadPopup(MODULE = self)

                
        
        #--------------------------------
        # LoadWorkflows
        #--------------------------------
        self.XnatSceneLoadWorkflow = XnatSceneLoadWorkflow(self)
        self.XnatFileLoadWorkflow = XnatFileLoadWorkflow(self)
        self.XnatDicomLoadWorkflow = XnatDicomLoadWorkflow(self)
        
        
        
        #--------------------------------
        # Init gui
        #--------------------------------
        self.initGUI()
        
        
        
        #--------------------------------
        # Listeners/observers from gui
        #--------------------------------
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndCloseEvent, self.sceneClosedListener)
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.EndImportEvent, self.sceneImportedListener)



        #--------------------------------
        # Tester
        #--------------------------------
        self.tester = XnatSlicerTest(self)



        #--------------------------------
        # Clean the temp dir
        #--------------------------------
        self.cleanCacheDir(200)


        
        self.parent.show()


      

      
    def onReload(self, moduleName = "XnatSlicer"):
      """ Generic reload method for any scripted module.
          ModuleWizard will subsitute correct default moduleName.
          Provided by Slicer.
      """
      
      widgetName = moduleName + "Widget"


      #--------------------------------
      # Reload the source code:
      # - set source file path
      # - load the module to the global space
      #--------------------------------
      filePath = eval('slicer.modules.%s.path' % moduleName.lower())
      p = os.path.dirname(filePath)
      if not sys.path.__contains__(p):
        sys.path.insert(0,p)
      fp = open(filePath, "r")
      globals()[moduleName] = imp.load_module(
          moduleName, fp, filePath, ('.py', 'r', imp.PY_SOURCE))
      fp.close()


      
      #--------------------------------
      # Rebuild the widget:
      # - find and hide the existing widget
      # - create a new widget in the existing parent
      #--------------------------------
      parent = slicer.util.findChildren(name='%s Reload' % moduleName)[0].parent()
      for child in parent.children():
        try:
          child.hide()
        except AttributeError:
          pass


        
      #--------------------------------  
      # Remove spacer items.
      #--------------------------------
      item = parent.layout().itemAt(0)
      while item:
        parent.layout().removeItem(item)
        item = parent.layout().itemAt(0)


        
      #--------------------------------
      # Create new widget inside existing parent.
      #--------------------------------
      globals()[widgetName.lower()] = eval('globals()["%s"].%s(parent)' % (moduleName, widgetName))
      globals()[widgetName.lower()].setup()



      
    def onReloadAndTest(self, moduleName = "ScriptedExample"):
        """ Also provided by Slicer.  Runs the tests on the
            reload.
        """
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
        #print("'Close Scene' called. Resetting Xnat session data.")    
        self.XnatView.sessionManager.clearCurrentSession()  



        
    def sceneImportedListener(self, caller, event): 
        """Actions for when the user imports a scene from the GUI.
           NOTE: This technically is not used, as the user must refer to files from an 
           Xnat location. Nonetheless, it is implemented in the event that it is needed.
        """
        if self.XnatView.lastButtonClicked == None:
            #print("'Import Data' called. Resetting Xnat session data.")
            self.XnatView.sessionManager.clearCurrentSession() 
    

            
            
    def initGUI(self):  
        """ As stated.
        """
                
        #--------------------------------
        # Main Collapsible Button
        #--------------------------------
        mainCollapsibleButton = ctk.ctkCollapsibleButton()
        mainCollapsibleButton.text = "XNATSlicer"



        #--------------------------------
        # Login Group Box
        #--------------------------------
        self.loginGroupBox = ctk.ctkCollapsibleGroupBox()
        self.loginGroupBox.setTitle("Login")


        
        #--------------------------------
        # Tools Group Box
        #--------------------------------
        self.toolsGroupBox = ctk.ctkCollapsibleGroupBox()
        self.toolsGroupBox.setTitle("Tools")



        #--------------------------------
        # Viewer Group Box
        #--------------------------------
        self.viewerGroupBox = ctk.ctkCollapsibleGroupBox()
        self.viewerGroupBox.setTitle("Viewer")


        
        
        #--------------------------------
        # Add all sections to parent layout.
        #--------------------------------
        self.layout.addWidget(mainCollapsibleButton)



        #--------------------------------
        # DEFINE: Main layout
        #--------------------------------        
        self.mainLayout = qt.QVBoxLayout()


        
        #--------------------------------
        # LOGIN layout.
        #--------------------------------        
        self.loginGroupBox.setLayout(self.XnatLoginMenu.loginLayout)
        self.loginGroupBox.setChecked(True)
        self.mainLayout.addWidget(self.loginGroupBox)



        #--------------------------------
        # Viewer layout.
        #--------------------------------   
        self.viewerLayout = qt.QGridLayout()  
        #
        # Search Row
        #
        self.searchRowLayout = qt.QStackedLayout()
        self.searchRowLayout.setStackingMode(1)
        self.searchBox = qt.QLineEdit()
        self.searchBox.connect("returnPressed()", self.XnatView.searchEntered)


        searchButton = qt.QPushButton("Search:")
        size = qt.QSize(26,26)
        searchButton.setFixedSize(size)
        searchButton.setStyleSheet("background: none")
        #searchButton.setStyleSheet("border: none")

        
        self.searchRowLayout.addWidget(self.searchBox)
        self.searchRowLayout.addWidget(searchButton)
        searchButton.setStyleSheet('qproperty-alignment: AlignRight')
        
        
        self.searchRowLayout.setAlignment(searchButton, 0x0002)
        #
        # Load / Save Buttons
        #
        self.loadSaveButtonLayout = qt.QVBoxLayout()
        self.loadSaveButtonLayout.addWidget(self.XnatButtons.buttons['io']['load'])#, 2, 0)
        self.loadSaveButtonLayout.addWidget(self.XnatButtons.buttons['io']['save'])#, 0, 0) 
        #
        # Add widgets to layout
        #
        self.viewerLayout.addLayout(self.searchRowLayout, 0, 0, 1, 1)
        self.viewerLayout.addWidget(self.XnatView.viewWidget, 2, 0)
        self.viewerLayout.addLayout(self.loadSaveButtonLayout, 2, 1)
        #
        # Add viewer layout to group box and main layout.
        #
        self.viewerGroupBox.setLayout(self.viewerLayout)
        self.viewerGroupBox.setChecked(True)
        self.viewerGroupBox.setEnabled(False)
        self.mainLayout.addWidget(self.viewerGroupBox)
        


        #--------------------------------
        # Tools layout.
        #-------------------------------- 
        self.toolsLayout = qt.QHBoxLayout()
        self.toolsLayout.addWidget(self.XnatButtons.buttons['io']['delete'])
        self.toolsLayout.addSpacing(15)
        self.toolsLayout.addWidget(self.XnatButtons.buttons['io']['addProj'])
        self.toolsLayout.addSpacing(15)
        self.toolsLayout.addWidget(self.XnatButtons.buttons['io']['test'])
        self.toolsLayout.addStretch()
        #
        # Filter
        #
        self.toolsLayout.addStretch()
        filterLabel = qt.QLabel("Project filter:")
        self.toolsLayout.addWidget(filterLabel)
        self.toolsLayout.addSpacing(15)
        self.toolsLayout.addWidget(self.XnatButtons.buttons['filter']['accessed'])
        #
        # Add tools layout to group box and main layout.
        #
        self.toolsGroupBox.setLayout(self.toolsLayout)
        self.toolsGroupBox.setChecked(False)
        self.toolsGroupBox.setEnabled(False)
        self.mainLayout.addWidget(self.toolsGroupBox)



        #--------------------------------
        # Add main layout to main collapsible button.
        #-------------------------------- 
        self.mainLayout.addStretch()
        mainCollapsibleButton.setLayout(self.mainLayout)
       


        
        
    def cleanCacheDir(self, maxSize):
        """ Empties contents of the temp directory based upon maxSize
        """
        import math
        folder = self.GLOBALS.CACHE_URI
        folder_size = 0


        
        #--------------------------------
        # Loop through files to get file sizes.
        #--------------------------------
        for (path, dirs, files) in os.walk(folder):
          for file in files:
            folder_size += os.path.getsize(os.path.join(path, file))
        #print ("XnatSlicer Data Folder = %0.1f MB" % (folder_size/(1024*1024.0)))


        
        #--------------------------------
        # If the folder size exceeds limit, remove contents.
        #--------------------------------
        folder_size = math.ceil(folder_size/(1024*1024.0))
        if folder_size > maxSize:
            self.utils.removeFilesInDir(folder)    




                
    def beginXnat(self):
        """ Opens the view class linked to the Xnat REST API.
            Runs a test for the relevant libraries (i.e. SSL)
            before allowing the login process to begin.
        """

        #--------------------
        # Can SSL be imported?
        #--------------------
        print("XnatSlicer Module: Checking if SSL is installed...")
        try:      
            import ssl
            httplib.HTTPSConnection
            print("XnatSlicer Module: SSL is installed!")

            

        #--------------------
        # If not, kick back OS error
        #--------------------
        except Exception, e:
            strs = "XnatSlicer cannot operate on this system as SSL is not installed."
            print("XnatSlicer Module: %s"%(strs))
            qt.QMessageBox.warning(slicer.util.mainWindow(), "No SSL", "%s"%(strs))
            return
                

        
        #--------------------
        # Init communicator.
        #--------------------
        self.XnatIo.setup(MODULE = self, 
                                    host = self.settings.getAddress(self.XnatLoginMenu.hostDropdown.currentText), 
                                    user = self.XnatLoginMenu.usernameLine.text, password=self.XnatLoginMenu.passwordLine.text)

        

        #--------------------
        # Begin communicator
        #--------------------
        self.XnatView.begin()


      

    def onLoginSuccessful(self):
        """ Enables the relevant collapsible 
            group boxes. 
        """

        #--------------------
        # Minimize the login group box.
        #--------------------      
        self.loginGroupBox.setChecked(False)

        

        #--------------------
        # Maximize and enable the viewer group box.
        #--------------------      
        self.viewerGroupBox.setChecked(True)
        self.viewerGroupBox.setEnabled(True)


        
        #--------------------
        # Maximize and enable the tools group box.
        #--------------------      
        self.toolsGroupBox.setChecked(False)
        self.toolsGroupBox.setEnabled(True)



        
    def onLoginFaled(self):
        """ Disable the relevant collapsible 
            group boxes. 
        """

        #--------------------
        # Maximize the login group box.
        #--------------------      
        self.loginGroupBox.setChecked(True)

        

        #--------------------
        # Minimize and disable the viewer group box.
        #--------------------      
        self.viewerGroupBox.setChecked(False)
        self.viewerGroupBox.setEnabled(False)


        
        #--------------------
        # Minimize and disable the tools group box.
        #--------------------      
        self.toolsGroupBox.setChecked(False)
        self.toolsGroupBox.setEnabled(False)
