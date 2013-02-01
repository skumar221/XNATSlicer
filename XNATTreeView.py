# SLICER INCLUDES
from __main__ import vtk, ctk, qt, slicer

# PYTHON INCLUDES
import os
import sys
import shutil

# MODULE INCLUDES
from XNATFileInfo import *
from XNATMRMLParser import *
from XNATUtils import *
from XNATInstallWizard import *
from XNATSettings import *
from XNATLoadWorkflow import *
from XNATSaveDialog import *
from XNATSaveWorkflow import *

# PARENT CLASS INCLUDES
import XNATView


################################################################################
comment = """
              XNATTreeView is a subclass of the XNATView class.  It 
              uses QTreeWidget to describe the XNAT file system accessed,
              presenting them in a tree-node hierarchy.
              
              The view classes (and subclasses) ultimately communicate
              with the load and save workflows.   
# TODO : 
"""
#################################################################################


class XNATTreeView(XNATView.XNATView):
    """ Initiate globals.
    """  

    def setup(self):
        #=======================================================================
        # INIT TREEVIEW
        #=======================================================================
        self.viewWidget = qt.QTreeWidget()
        self.viewWidget.setHeaderHidden(False)       
        treeWidgetSize = qt.QSize(100, 200)
        self.viewWidget.setBaseSize(treeWidgetSize)
        
        #=======================================================================
        # TREEVIEW COLUMN SETUP
        #=======================================================================
        self.viewWidget.setColumnCount(3)
        self.column_name = 0
        self.column_category = 1
        self.column_size = 2
        columnLabels = []
        columnLabels.append("Name")
        columnLabels.append("Category")
        columnLabels.append("Size")
        self.viewWidget.setHeaderLabels(columnLabels)
        
        #=======================================================================
        # DEFINE FONTS
        #=======================================================================
        self.itemFont_folder = qt.QFont("Arial", self.utils.fontSize, 25, False)
        self.itemFont_file = qt.QFont("Arial", self.utils.fontSize, 75, False)
        self.itemFont_category = qt.QFont("Arial", self.utils.fontSize, 25, True)
        
        #=======================================================================
        # INIT TREE GLOBALS
        #=======================================================================
        self.dirText = None     
        self.currItem = None
        self.currLoadable = None
        
        #=======================================================================
        # INIT LOAD GLOBALS
        #=======================================================================
        self.currSceneName = None
        self.lastButtonClicked = None 
        
        #=======================================================================
        # INIT SAVE GLOBALS
        #=======================================================================
        self.saveScenePackageName = ""
        
        #=======================================================================
        # INIT CLEAR SCENE DIALOG
        #=======================================================================
        self.initClearDialog()
        #=======================================================================
        # INIT FOLDER MASKS
        #=======================================================================
        self.applySlicerFolderMask = True
        self.hideSlicerHelperFolders = True
                              
        
        self.deleteDialog = qt.QMessageBox()       
 
    def loadProjects(self):
        self.viewWidget.clear()
        self.browser.updateStatus(["","Retrieving projects. Please wait...",""])
        projects = self.XNATCommunicator.getFolderContents('/projects')
        projectItems = self.makeTreeItems(self.viewWidget, projects)
        #=======================================================================
        # INIT TREEVIEW COLUMNS
        #=======================================================================
        self.viewWidget.insertTopLevelItems(0, projectItems)
        
        #=======================================================================
        # TREEVIEW CLICKS
        #=======================================================================
        self.viewWidget.connect("itemExpanded(QTreeWidgetItem *)",
                                self.getChildrenExpanded)
        self.viewWidget.connect("itemClicked(QTreeWidgetItem *, int)",
                                self.treeItemClicked)
        
    def begin(self, XNATCommunicator):
        """ (INHERITED from XNATView) Called from XNATBroswer, 'begin' 
            initiates the tree-view to communicate with the XNATCommunicator 
            and also connects mouse clicks to various widget responses.
        """
        #=======================================================================
        # CALL PARENT
        #=======================================================================
        super(XNATTreeView, self).begin(XNATCommunicator)
        
        #=======================================================================
        # GET PROJECTS IN XNAT
        #=======================================================================
        self.loadProjects()
        self.browser.updateStatus(["", "Navigate project.", ""])
        self.addProjButton.setEnabled(True)
        
  
   
      
    def getItem_byPath(self, pathVal):
        items = self.viewWidget.findItems(os.path.basename(pathVal), 64)
        #print "PATHVAL: " + pathVal
        dirNames, dirTypes = self.utils.splitXNATPath(pathVal)
        dirNames.reverse()
        # CYCLE THROUGH PARENTS
        for item in items:             
            found=True
            for k,v in map(None, dirNames, reversed(self.getParents(item))):
                if (k != v.text(self.column_name)): # print "ASDF: " + k + "\t\t" + v.text(self.column_name)
                    found=False
                    break
            if found:
                return item
     
   
     
    def deleteButtonClicked(self, button=None):
        #print (self.utils.lf() + "Delete Clicked!")
        if button and button.text.lower().find('ok') > -1:         
            fileParent = self.viewWidget.currentItem().parent()
            delStr = self.getXNATDir(self.getParents(self.viewWidget.currentItem()))
            
            if ((not ('files' in self.viewWidget.currentItem().text(self.column_category))) or 
                (not (self.utils.slicerDirName in self.viewWidget.currentItem().text(self.column_category)))):
                delStr = os.path.dirname(delStr)
                
            self.XNATCommunicator.delete(delStr)   
            self.viewWidget.setCurrentItem(fileParent)
            self.getChildrenExpanded(self.viewWidget.currentItem())
        elif button and button.text.lower().find('cancel') > -1:
             return
        else:
            self.deleteDialog = qt.QMessageBox()
            self.deleteDialog.setIcon(qt.QMessageBox.Warning)
            self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from XNAT?"%(self.viewWidget.currentItem().text(self.column_name)))   
            self.deleteDialog.connect('buttonClicked(QAbstractButton*)', self.deleteButtonClicked)
            self.deleteDialog.addButton(qt.QMessageBox.Ok)
            self.deleteDialog.addButton(qt.QMessageBox.Cancel)    
            self.deleteDialog.show()
           
    def saveButtonClicked(self):        
        """ Conducts a series of steps (including the file naming workflow) 
            before actually saving the scene.
        """     
        #======================================================================   
        # GLOBALS
        #======================================================================
        self.lastButtonClicked = "save" 
        #======================================================================   
        # SESSION MANAGER
        #======================================================================
        if self.sessionManager.sessionArgs:
            #self.viewWidget.setCurrentItem(self.getItem_byPath(self.sessionManager.sessionArgs['saveLevel']))
            
            #self.sessionManager.sessionArgs.printAll("\nSESSION ARGS IN SAVE==========")
            self.makeRequiredSlicerFolders()
            #===================================================================
            # OPEN FILE SAVE DIALOG
            #===================================================================
            FileSaveDialog(self.browser, self, self.sessionManager.sessionArgs)
        #======================================================================
        # W/O SESSION MANAGER (UNLINKED SAVE)
        #======================================================================
        elif (not self.sessionManager.sessionArgs):
            #print (self.utils.lf() + "UPLOADING WITHOUT SESSION ARGS")
            fullPath = self.getXNATDir(self.getParents(self.viewWidget.currentItem()))
            #print fullPath
            remoteURI = self.browser.settings.getAddress(self.browser.hostDropdown.currentText) + fullPath
            sessionArgs = XNATSessionArgs(browser = self.browser, srcPath = fullPath)
            sessionArgs['sessionType'] = "scene upload - unlinked"
            sessionArgs.printAll()
            SaveUnlinkedDialog(self.browser, self, fullPath, sessionArgs)

    def makeRequiredSlicerFolders(self, path = None):       
        #=======================================================================
        # MAKE REQUIRED FOLDERS, TRIVIAL IF ALREADY THERE
        #=======================================================================
        if self.sessionManager.sessionArgs:
            self.XNATCommunicator.makeDir(os.path.dirname(self.sessionManager.sessionArgs['saveDir']))
            self.XNATCommunicator.makeDir(os.path.dirname(self.sessionManager.sessionArgs['sharedDir']))



    def beginSaveWorkflow(self, sessionArgs):
        #===================================================================
        # define args
        #===================================================================           
        #sessionArgs.printAll("\nBEGIN SAVE WORKFLOW***********************")         
        self.currItem = self.viewWidget.currentItem()   
        self.startNewSession(sessionArgs)
        self.makeRequiredSlicerFolders() 
        saveWorkflow = XNATSaveWorkflow(self.browser, self.XNATCommunicator, self.sessionManager.sessionArgs)
        saveWorkflow.saveScene()     
    
    def loadButtonClicked(self, button = None):
        #=======================================================================
        # INIT PARAMS
        #=======================================================================
        self.lastButtonClicked = "load"
        #print self.utils.lf() +  "load clicked!"
        
        
        #=======================================================================
        # CLEAR SCENE
        #=======================================================================
        if not button:
            if not self.utils.isCurrSceneEmpty():           
                self.initClearDialog()
                self.clearSceneDialog.connect('buttonClicked(QAbstractButton*)', self.loadButtonClicked) 
                self.clearSceneDialog.show()
                return
            
        #=======================================================================
        # BEGIN WORKFLOW
        #=======================================================================
        if (button and button.text.lower().find('yes') > -1) or self.utils.isCurrSceneEmpty():
            #===================================================================
            # clear scene
            #===================================================================
            self.sessionManager.clearCurrentSession()
            slicer.app.mrmlScene().Clear(0)
            #===================================================================
            # get tree related params
            #===================================================================
            currItem = self.viewWidget.currentItem()
            parents= self.getParents(currItem)
            #===================================================================
            # get xnat paths from tree
            #===================================================================
            fullPath = self.getXNATDir(self.getParents(currItem))
            remoteURI = self.browser.settings.getAddress(self.browser.hostDropdown.currentText) + fullPath
            #===================================================================
            # set download path
            #===================================================================
            dst = os.path.join(self.utils.downloadPath, currItem.text(self.column_name))
            #print (self.utils.lf() +  "fullPath: %s\nparentLeng: %s\ndst: %s"%(fullPath, str(len(parents)), dst))
           
            loader = None
            if (('files' in currItem.text(self.column_category)) or 
                (self.utils.slicerDirName in currItem.text(self.column_category))):
                if (currItem.text(self.column_name).endswith(self.utils.defaultPackageExtension)): 
                    loader = SceneLoader(self.browser)
                else:
                    loader = FileLoader(self.browser)
            else:
                loader = DICOMLoader(self.browser)
            #return
            #===================================================================
            # populate args
            #===================================================================
            args = {"XNATCommunicator": self.XNATCommunicator, 
                    "xnatSrc":fullPath, 
                    "localDst":dst, 
                    "folderContents": None}
            #===================================================================
            # load file or folder from xnat
            #===================================================================
            loadSuccessful = loader.load(args)            
        #=======================================================================
        # ENABLE WIDGET
        #=======================================================================
        #slicer.app.processEvents()
        self.viewWidget.setEnabled(True)
        self.lastButtonClicked = None

    
    
    def getParentItemByCategory(self, item, category):
        #print "GETTING PARENT ITEM! " + item.text(0) + " CATEGORY: " + category 
        parents = self.getParents(item)
        for p in parents:
            #print "P.text: " + p.text(0) + " " + p.text(1)
            if category in p.text(self.column_category):
                #print "FOUND PARENT ITEM!"
                return p
        return None 
        
    def getTreeItemType(self, item):
        #=======================================================================
        # IF STANDARD XNAT FOLDER, RETURN IT
        #=======================================================================
        for k, dictItem in self.utils.xnatDepthDict.iteritems():
            if item.text(self.column_category).strip(" ") == dictItem:
                return dictItem
            
        #=======================================================================
        # IF ITEM IS A RESOURCE FOLDER RETURN 'RESOURCES'
        #=======================================================================
        if item.text(self.column_category).strip(" ") == "resources":
            return "resources"
        
        #=======================================================================
        # IF ITEM IS A FILE RETURN 'FILE'
        #=======================================================================
        if item.text(self.column_category).strip(" ") == "files":
            return "files"
        
        #=======================================================================
        # IF ITEM IS SLICERFILE, GIVEN FOLDERMASK   
        #=======================================================================
        if self.applySlicerFolderMask:
            #===================================================================
            # if category is slicer, return "sliderFile" category
            #===================================================================
            if item.text(self.column_category).strip(" ") == self.utils.slicerDirName:
                return "slicerFile"
        
    def setEnabled(self, bool):
        """ (INHERITED from XNATView)  Enables or disables the view widget.
        """
        if bool: 
            self.viewWidget.setEnabled(True)
        else: 
            self.viewWidget.setEnabled(False)

    def initClearDialog(self):
        """ Initiates/resets dialog for window to clear the current scene.
        """
        #=======================================================================
        # REMOVE WINDOW
        #=======================================================================
        try: 
            self.clearSceneDialog.delete()
        except: pass
        #=======================================================================
        # DEFINE DIALOG BUTTONS
        #=======================================================================
        self.clearSceneDialog = qt.QMessageBox()
        self.clearSceneDialog.setStandardButtons(qt.QMessageBox.Yes | 
                                                 qt.QMessageBox.No)
        self.clearSceneDialog.setDefaultButton(qt.QMessageBox.No)
        self.clearSceneDialog.setText("In order to load your selection " + 
                                      "you have to clear the current scene." + 
                                      "\nAre you sure you want to clear?")
    
    def getXNATDepth(self, item):
        """ For use in the Category' column of a given tree node.
            Returns the depth level of where a tree item is in the XNAT 
            hierarchy: projects, subjects, experiments, scans and resources.
        """
        #=======================================================================
        # GET PARENTS
        #=======================================================================
        parents= self.getParents(item)  
        
        #=======================================================================
        # A: GET LEVEL BY PARENTS
        #=======================================================================
        returnStr = ""   
        try: 
            returnStr = str(self.utils.xnatDepthDict[len(parents)-1]).lower()
        #=======================================================================
        # IF A FAILS, DEFAULT TO RESOURCES
        #=======================================================================
        except:          
            returnStr = "resources"    
            
        #=======================================================================
        # LABEL SPACING
        #=======================================================================
        # NOTE:   The return string needs to have some spaces before it to 
        #         visually reflect where it is in the hierarchy.  This is for
        #         display purposes in the 'Category' column of the treeView.
        # 
        if "resources" in parents[len(parents)-2].text(self.column_category): 
            return self.getIndentByItemDepth(item) + "files"
        else:
            return self.getIndentByItemDepth(item) + returnStr
    
    def getIndentByItemDepth(self, item):
        """Returns an indent for labeling purposes based on depth of item in 
           the treeView.
        """
        parents= self.getParents(item)
        spaceStr = ""        
        #=======================================================================
        # RETURN SPACES BY PARENT LENGTH
        #=======================================================================
        for i in range(0, len(parents)-1): 
            spaceStr += "  "
        return spaceStr
                 
    def makeTreeItems(self, parent, childStrs, resourceStrs = None, slicerResourceStrs = None):
        """Creates a set of items to be put into the QTreeWidget based
           upon its parents, its children and the XNAT.
        """
        treeItems = []
        #=======================================================================
        # ADD CHILDREN
        #=======================================================================
        if childStrs:
            for itemStr in childStrs:
                if itemStr:
                    #print self.utils.lf() + "MAKING CHILD STRS: "
                    #===========================================================
                    # create item
                    #===========================================================
                    rowItem = qt.QTreeWidgetItem(parent)
                    rowItem.setText(self.column_name, itemStr)
                    #===========================================================
                    # define item style
                    #===========================================================
                    rowItem.setChildIndicatorPolicy(0)          
                    rowItem.setFont(self.column_name, self.itemFont_folder)                    
                    #===========================================================
                    # if item is at end of tree, add resource
                    #===========================================================
                    if self.getXNATDepth(rowItem).find('resources') >-1: 
                        resourceStrs = childStrs
                        break                  
                    #===========================================================
                    # set category column             
                    #===========================================================
                    rowItem.setText(self.column_category, self.getXNATDepth(rowItem))            
                    #===========================================================
                    # if file, disable expansion
                    #===========================================================
                    if "files" in rowItem.text(self.column_category):
                        rowItem.setChildIndicatorPolicy(1)
                        fullPath = self.getXNATDir(self.getParents(rowItem))
                        self.changeFontColor(rowItem, False, "grey", self.column_size)
                        rowItem.setFont(self.column_size, self.itemFont_category)
                        rowItem.setText(self.column_size, self.XNATCommunicator.getSize(fullPath)["mb"] + " MB")
                    #===========================================================
                    # set category aesthetics
                    #===========================================================
                    rowItem.setFont(self.column_category, self.itemFont_category)                  
                    #===========================================================
                    # if no folder masking, make appropriate aesthetic changes
                    #===========================================================
                    if not self.applySlicerFolderMask:
                        for slicerDir in self.utils.requiredSlicerFolders:
                            try:
                                if rowItem.parent().text(self.column_name) == slicerDir: 
                                    self.changeFontColor(rowItem, False, "green", self.column_name)
                                    continue
                            except Exception, e:
                                print (self.utils.lf() + "COLOR APPLY ERROR: " + str(e))               
                    #===========================================================
                    # set item color
                    #===========================================================
                    self.changeFontColor(rowItem, False, "grey", self.column_category)                
                    #===========================================================
                    # add item to tree
                    #===========================================================
                    treeItems.append(rowItem)
                    
        #=======================================================================
        # ADD RESOURCES
        #=======================================================================
        if resourceStrs:
            for itemStr in resourceStrs:
                #print self.utils.lf() +  "MAKING RESOURCE STRS: " + itemStr
                #===============================================================
                # create item
                #===============================================================
                rowItem = qt.QTreeWidgetItem(parent)
                rowItem.setText(self.column_name, itemStr)
                #===============================================================
                # define item style
                #===============================================================
                rowItem.setChildIndicatorPolicy(0)         
                rowItem.setFont(self.column_name, self.itemFont_folder)
                #===============================================================
                # set font color, if mask
                #===============================================================
                if not self.applySlicerFolderMask:
                    for slicerDir in self.utils.requiredSlicerFolders:
                        if itemStr == slicerDir: 
                            self.changeFontColor(rowItem, False, "green", self.column_name)
                            continue
                #===============================================================
                # define column category, aesthetics
                #===============================================================
                rowItem.setText(self.column_category, 
                                self.getIndentByItemDepth(rowItem) + "resources")
                rowItem.setFont(self.column_category, self.itemFont_category) 
                self.changeFontColor(rowItem, False, "grey", self.column_category)
                #===============================================================
                # append item to tree
                #===============================================================
                treeItems.append(rowItem)
                
        #=======================================================================
        # ADD RESOURCES WITH FOLDER MASK
        #=======================================================================
        if self.applySlicerFolderMask and slicerResourceStrs:
            for itemStr in slicerResourceStrs:
                #print (self.utils.lf() +  "SLICER RESOURCE STRS: " + itemStr)
                #===============================================================
                # hide helper folders.
                #===============================================================
                if self.hideSlicerHelperFolders: 
                    if slicerResourceStrs[itemStr] != self.utils.slicerDirName:
                        #print (self.utils.lf() +  "SKIPPING DISPLAYING: " + itemStr)
                        continue
                #===============================================================
                # create tree item, define aesthetics
                #===============================================================
                rowItem = qt.QTreeWidgetItem(parent)
                rowItem.setText(self.column_name, itemStr)
                rowItem.setChildIndicatorPolicy(1)         
                rowItem.setFont(self.column_name, self.itemFont_folder)
                #===============================================================
                # set item font color
                #===============================================================
                self.changeFontColor(rowItem, True, "green", self.column_name)
                #===============================================================
                # set item font category
                #===============================================================
                rowItem.setText(self.column_category, slicerResourceStrs[itemStr])
                rowItem.setFont(self.column_category, self.itemFont_category) 
                self.changeFontColor(rowItem, True, "green", self.column_category)

                rowItem.setFont(self.column_size, self.itemFont_category)
                self.changeFontColor(rowItem, False, "grey", self.column_size)
            
                fullPath = self.getXNATDir(self.getParents(rowItem))
                rowItem.setText(self.column_size, self.XNATCommunicator.getSize(fullPath)["mb"] + " MB")
                #===============================================================
                # add too tree          
                #===============================================================
                treeItems.append(rowItem)
                        
        return treeItems
         
    def getXNATDir(self, parents):
        """ Constructs a directory structure based on the default XNAT 
            organizational scheme, utilizing the tree hierarchy. Critical to 
            communication with XNAT.
            Ex. parents = [exampleProject, testSubj, testExpt, scan1, images], 
            then returns: 
            'projects/exampleProject/subjects/testSubj/experiments/testExpt/scans/scan1/resources/images'  
        """  
        #print self.utils.lf() +  ("Get XNATDir parent texts")
        
        #=======================================================================
        # INIT VARS      
        #=======================================================================
        isResource = False
        isSlicerFile = False
        dirStr = "/"        
        
        #=======================================================================
        # CONSTRUCT PRELIMINARY PATH
        #=======================================================================
        XNATDepth = 0        
        for item in parents:
            #===================================================================
            # for resource folders
            #===================================================================
            if 'resources' in item.text(self.column_category).strip(" "): 
                isResource = True            
            #===================================================================
            # for masked slicer folders
            #===================================================================
            elif ((self.utils.slicerDirName in item.text(self.column_category)) 
                  and self.applySlicerFolderMask): 
                isSlicerFile = True
            #===================================================================
            # construct directory string
            #===================================================================
            dirStr += "%s/%s/"%(item.text(self.column_category).strip(" "), 
                                item.text(self.column_name))
            XNATDepth+=1
            
        #=======================================================================
        # PATH FOR RESOURCES
        #=======================================================================
        if isResource:
            #===================================================================
            # append "files" if resources folder
            #===================================================================
            if 'resources' in parents[-1].text(self.column_category).strip(" "):
                dirStr += "files"
            #===================================================================
            # cleanup if at files level
            #===================================================================
            elif 'files'  in parents[-1].text(self.column_category).strip(" "):
                dirStr = dirStr[:-1]
            #===================================================================
            # if on a files
            #===================================================================
            else:
                dirStr =  "%s/files/%s"%(os.path.dirname(dirStr), 
                                         os.path.basename(dirStr))
                
        #=======================================================================
        # PATH FOR SLICER FILES
        #=======================================================================
        if isSlicerFile:
            #print self.utils.lf() + "IS SLICER FILE!" 
            self.currLoadable = "scene"
            dirStr = ("%s/resources/%s/files/%s"%(os.path.dirname(os.path.dirname(os.path.dirname(dirStr))),
                                                  self.utils.slicerDirName,
                                                  os.path.basename(os.path.dirname(dirStr))))
            #print self.utils.lf() + "DIR STr: " + dirStr
            
        #=======================================================================
        # PATH FOR NON-SLICER FILES    
        #=======================================================================
        else:
            if XNATDepth < 4: 
                dirStr += self.utils.xnatDepthDict[XNATDepth] 

        #print (self.utils.lf() +  "XNATDepth: %s\n\t\t\t\tConstructing XNATDir - %s"%(str(XNATDepth),dirStr)) 
        return dirStr
           
    def getTreeItemInfo(self, item):   
        """Disects a given tree item and returns various useful attributes."""
        #=======================================================================
        # CATEGORY TEXT    
        #=======================================================================
        itemText = item.text(self.column_name)
        #=======================================================================
        # ITEM EXTENSION
        #=======================================================================
        itemExt = itemText.partition(".")[2]     
        #=======================================================================
        # PATH BY PARENTS
        #=======================================================================
        fullPath = self.getXNATDir(self.getParents(item))
        
        #=======================================================================
        # CONSTRUCT PREDECESSOR PATHS
        #=======================================================================
        upFolders = fullPath.split("/")
        upFolders = upFolders[1:]
        upPaths = []      
        upPaths.append("/%s"%(upFolders[0]))
        for i in range(1, len(upFolders)-1):
            upPaths.append("%s/%s"%(upPaths[i-1], upFolders[i]))          
        upPaths.reverse()        
        upFolders.reverse()   
         
        return itemText, itemExt, fullPath, upPaths, upFolders   
    
    def navigateTo(self, navItem):
        self.viewWidget.setCurrentItem(navItem)
        
    def getTreeItemInBranch(self, item, targetName, routines = ['selected','parent','sibling','child','nephew']):
        """ Returns the equivalent "TreeItem" associated with "targetName" within
            the hierarchy of item.  Routines explained below.
        """  
        targetName = targetName.lower().strip("/")   
        #=======================================================================
        # IF NO ITEM
        #=======================================================================
        if not item:
            item = self.viewWidget.currentItem()                     
        #=======================================================================
        # TARGET IS CURRENT ITEM
        #=======================================================================
        if 'selected' in routines:
            if item.text(self.column_name).lower() == targetName:
                return item         
        #=======================================================================
        # TARGET IS PARENT ITEM
        #=======================================================================
        if 'parent' in routines:
            if item.parent():
                itemIter = item.parent()
                while itemIter:
                    if itemIter.text(self.column_name).lower() == targetName: return itemIter
                    itemIter = itemIter.parent() 
        #=======================================================================
        # TARGET IS SIBLING
        #=======================================================================
        if 'sibling' in routines:
            if item.parent():
                parentItem =  item.parent()
                for y in range(0, parentItem.childCount()):
                    if parentItem.child(y).text(self.column_name).lower() == targetName.lower():
                        return parentItem.child(y)
        #=======================================================================
        # TARGET IS CHILD
        #=======================================================================
        if 'child' in routines:
            for z in range(0, item.childCount()):
                if item.child(z).text(self.column_name).lower() == targetName.lower():
                    return item.child(z)
        #=======================================================================
        # TARGET IS NEPHEW
        #=======================================================================
        if 'nephew' in routines:
            return self.getTreeItemInBranch(item.parent(), targetName, routines=['sibling'])
        #=======================================================================
        # NULL RETURN  
        #=======================================================================
        return None
        
    def getParents(self, item):
        """Returns the parents of a specific treeNode 
            all the way to the "project" level
        """
        parents = []
        while(item):
          parents.insert(0, item)
          item = item.parent()
        return parents
    
    def getParentTexts(self, item):
        """Returns the parent text values of a specific 
            treeNode all the way to the "project" level
        """
        return [child.text(self.column_name) for child in self.getParents(item)]
    
    def determineExpanded(self, item):
        """Determines if the current treeItem is expanded
        """      
        if item.childIndicatorPolicy() == 0:
            self.getChildren(item, expanded = True) 

                
    def getChildrenExpanded(self, item):
        """ When the user interacts with the treeView, this is a hook 
            method that gets the branches of a treeItem and expands them 
        """ 
        self.treeItemClicked(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        #=======================================================================
        # GET CHILDREN ONLY IF AT FILE LEVEL
        #=======================================================================
        if not 'files' in item.text(self.column_category):
            self.getChildren(item, expanded = True) 

    def getChildrenNotExpanded(self, item):
        """ When the user interacts with the treeView, this is a hook 
            method that gets the branches of a treeItem and does not 
            expand them 
        """ 
        self.treeItemClicked(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.column_category):
            self.getChildren(item, expanded = False)

    def treeItemClicked(self, item, col):
        #=======================================================================
        # SET GLOBALS
        #=======================================================================
        if item==None:
            item = self.currItem
        else:
            self.currItem = item
        self.viewWidget.setCurrentItem(item)
        self.currLoadable = None
        
        #=======================================================================
        # DISABLE BUTTONS
        #=======================================================================
        self.saveButton.setEnabled(False)
        if self.sessionManager.sessionArgs:
            self.saveButton.setEnabled(True)
        
        self.loadButton.setEnabled(False)
        self.deleteButton.setEnabled(True)

        #=======================================================================
        # CHECK IF AT SAVABLE/LOADABLE LEVEL 
        #=======================================================================
        isSubject = 'subjects' in item.text(self.column_category).strip(" ")
        isResource = 'resources' in item.text(self.column_category).strip(" ")
        isExperment = 'experiments' in item.text(self.column_category).strip(" ")
        isScan = 'scans' in item.text(self.column_category).strip(" ")
        isFile = 'files' in item.text(self.column_category).strip(" ")
        isSlicerFile = self.utils.slicerDirName.replace("/","") in item.text(self.column_category).strip(" ")
        
        #=======================================================================
        # ENABLE LOAD/SAVE IF AT THE DEFAULT SAVE LEVEL
        #=======================================================================
        atEnableLevel = False
        while(item.parent()):
            if self.utils.defaultXNATSaveLevel in item.text(self.column_category).strip(" "):
                atEnableLevel = True
                break
            item = item.parent()
        if atEnableLevel:
            self.loadButton.setEnabled(True)
            self.saveButton.setEnabled(True)
        
        #=======================================================================
        # DETERMINE SLICERFILE, IF MASK ENABLED
        #=======================================================================
        if self.applySlicerFolderMask:
            if item.text(self.column_category) == self.utils.slicerDirName:
                #print self.utils.lf() + "IS FILE!"
                isFile = True
                
                
        #=======================================================================
        # FILE ITEM ROUTINES
        #=======================================================================
        if isFile or isSlicerFile:
            self.deleteButton.setEnabled(True)
            ext = item.text(self.column_name).rsplit(".")
            #===================================================================
            # check extension
            #===================================================================
            if (len(ext)>1):
                #===============================================================
                # recognizable extensions        
                #===============================================================
                if self.utils.isRecognizedFileExt(ext[1]):
                    self.loadButton.setEnabled(True)
                    #===========================================================
                    # scene package
                    #===========================================================
                    for ext_ in self.utils.packageExtensions:
                        if ext_.replace(".","") in ext[1]: 
                            #===================================================
                            # set currloadable to scene                        
                            #===================================================
                            self.currLoadable = "scene"
                            #print self.utils.lf() +  "FOUND SCENE! " + self.currLoadable
                            return
                    #===========================================================
                    # generic file
                    #===========================================================
                    else:
                        #=======================================================
                        # set currloadable to file
                        #=======================================================
                        self.currLoadable = "file"
                        return
        
        #=======================================================================
        # DEFAULT LOAD/SAVE LEVEL     
        #=======================================================================
        if self.utils.defaultXNATSaveLevel in item.text(self.column_category).strip(" "):
            self.loadButton.setEnabled(True)
            #===================================================================
            # set currloadable to mass_dicom
            #===================================================================
            self.currLoadable = "mass_dicom" 
            return
        
          
    def getChildren(self, item, expanded, setCurrItem = True):
        """ Gets the branches of a particular treeItem via an XNATCommunicator 
            Get call.
        """       
        #print self.utils.lf() +  "XNATTreeView:getChildren()"
        if item:
            #===================================================================
            # SET GLOBALS
            #===================================================================
            if setCurrItem: 
                self.currItem = item
            
            #===================================================================
            # REMOVE EXISTING CHILDREN FOR RELOAD
            #===================================================================
            self.viewWidget.setCurrentItem(item)       
            item.takeChildren()
            
            #===================================================================
            # GET PARENTS FOR DEPTH CALCS
            #===================================================================
            parents= self.getParents(item)
            parentTexts = self.getParentTexts(item)  
            
            #===================================================================
            # GET CURR XNAT PATH BY PARENTS       
            #===================================================================
            xnatDir = self.getXNATDir(parents) 
            
            #===================================================================
            # INIT CHILD-TRACKING VARS
            #===================================================================
            childStrs = []
            attr = ''
            callLabel = False
            resourceStrs = None
            slicerResourceContents = None
            children = None
            
            #===================================================================
            # SPECIAL CASES
            #===================================================================
            if (len(parents) < 3): 
                attr = 'label' # Special cases with XNAT
            elif len(parents) == 3: 
                attr = 'ID'  # SCAN level
                
            #===================================================================
            # IF ITEM IS NOT RESOURCES...
            #===================================================================
            if ((not 'resources' in item.text(self.column_category)) and
                (not self.utils.slicerDirName in item.text(self.column_category))): 
                resourceQuery = xnatDir
                #===============================================================
                # for any item above scan, set to parent
                #===============================================================
                if (len(parents) != 5): 
                    #print self.utils.lf() + "PARENTS LESS THAN 5:"
                    resourceQuery = os.path.dirname(resourceQuery) 
                #===============================================================
                # get the 'resources' directory contents
                #===============================================================
                resourceStrs = self.XNATCommunicator.getResources(resourceQuery)               
                def filterSlicerDirs(dirList):
                    """ Separates dirList into two parts:
                        (1) Ones that have names NOT equivalent to required slicer folders.
                        (2) Ones that do.
                        """
                    slicerDirs = []
                    otherDirs = []
                    for dirName in dirList:
                        foundSlicer = False
                        for slicerFolder in self.utils.requiredSlicerFolders:
                            if dirName == slicerFolder:
                                foundSlicer = True
                        if foundSlicer:
                            slicerDirs.append(dirName)
                        else:
                            otherDirs.append(dirName)
                    return otherDirs, slicerDirs
                #===============================================================
                # handle resources w/an enabled mask
                #===============================================================
                slicerResources = None
                if resourceStrs and self.applySlicerFolderMask:                          
                    #===========================================================
                    # call filter so we know what/what not to display
                    #===========================================================
                    resourceStrs, slicerResources = filterSlicerDirs(resourceStrs)
                    #print self.utils.lf() + " RESOURCE DIRS: %s\n\t\t\tSLICER DIRS: %s"%(resourceStrs, slicerResources)
                #===============================================================
                # create a dictionary for slicer files when mask is applied
                #===============================================================
                if slicerResources:
                    if len(slicerResources) > 0:
                        for slicerFolder in self.utils.requiredSlicerFolders:
                            currFolder = slicerFolder
                            slicerXNATDir =  "%s/resources/%s/files"%(os.path.dirname(xnatDir),currFolder)
                            #===================================================
                            # if the dictionary is not defined (no slicer folder in the xnat dir)
                            #===================================================
                            if not slicerResourceContents:
                                slicerResourceContents = {}   
                            #===================================================
                            # get the folder contents given mask
                            #===================================================
                            fileList =  self.XNATCommunicator.getFolderContents(slicerXNATDir)
                            for f in fileList:
                                slicerResourceContents[f] = currFolder
                                
            #===================================================================
            # GET FOLDER CONTENTS
            #===================================================================
            childNames = self.XNATCommunicator.getFolderContents(xnatDir)
            
            #===================================================================
            # CYCLE THROUGH CHILDREN
            #===================================================================            
            #print self.utils.lf() + "CHILDNAMES: " + str(childNames)
            if ((childNames and len(childNames) > 0) and (not 'files' in item.text(self.column_category)) and
               (not self.utils.slicerDirName in item.text(self.column_category).strip(" "))):
                for strF in childNames:
                    import urllib2
                    #print self.utils.lf() + "URL: \t\t\t" + str(urllib2.quote(strF))
                    #===========================================================
                    # get the attribute value of the item in XNAT, such as "filename".
                    #===========================================================
                    attrVal = self.XNATCommunicator.getItemValue(xnatDir  + "/" + str(urllib2.quote(strF)), attr)
                    #===========================================================
                    # if the attrVal is not available, create it
                    #===========================================================
                    if not attrVal:
                        attrVal =  str(urllib2.quote(strF))
                    #===========================================================
                    # if slicer mask, tag file as being in slicer folder                 
                    #===========================================================
                    if self.applySlicerFolderMask:
                        isSlicerFolder = False
                        for reqFolder in self.utils.requiredSlicerFolders:
                            if attrVal == reqFolder:
                                isSlicerFolder = True
                        if not isSlicerFolder:
                            childStrs.append(attrVal)
                    #===========================================================
                    # if no slicer mask, add children          
                    #===========================================================
                    else:
                        childStrs.append(attrVal)           
            #print self.utils.lf() + "CHILDSTRS: " + str(childStrs)
            
            #===================================================================
            # ADD CHILDREN TO TREE -- SLICER ITEMS TREATED SEPARATELY
            #===================================================================
            children = self.makeTreeItems(item, childStrs, resourceStrs, slicerResourceContents)
            
            #===================================================================
            # IF AT AND OF XNAT HEIRARCHY
            #===================================================================
            if len(parents) == 5:
                for child in children: 
                    child.setChildIndicatorPolicy(1)
                if self.isDICOMFolder(item):
                    self.currLoadable = "dicom"
                    
            #===================================================================
            # ADD CHILDREN TO TREE
            #===================================================================
            if children: 
                item.addChildren(children)
                
            #===================================================================
            # EXPAND, SET CURRENT
            #===================================================================
            item.setExpanded(True)
            self.viewWidget.setCurrentItem(item) 
                
    def isDICOMFolder(self, item):       
        dicomCount = 0
        for x in range(0, item.childCount()):          
            try:
                child = item.child(x)
                ext = child.text(self.column_name).rsplit(".")[1]            
                if self.utils.isDICOM(ext):
                    dicomCount +=1
            except Exception, e:
                pass        
        if dicomCount == item.childCount():
                return True
        return False
        
    def setCurrItemToChild(self, item = None, childFileName = None):
        #print self.utils.lf() + " SET CURRITEM TO CHILD " + self.currItem.text(self.column_name) 
        if not item:
            item = self.currItem     
        self.getChildrenExpanded(item)
        if childFileName:
            for x in range(0, item.childCount()):
                child = item.child(x)
                #print "CHILDNAME: %s"%(child.text(self.column_name))
                if child.text(self.column_name) == childFileName:
                    self.viewWidget.setCurrentItem(child)
                    self.currItem = child;
                    return   
        
    def changeFontColor(self, item, bold = True, color = "black", column = 0):
        b = qt.QBrush()
        c = qt.QColor(color)
        b.setColor(c)
        item.setForeground(column, b)

    def startNewSession(self, sessionArgs, method="currItem"):
        self.saveButton.setEnabled(True)
        if method=="currItem":            
            # Sometimes we have to reset the curr item
            if not self.viewWidget.currentItem(): 
                self.viewWidget.setCurrentItem(self.currItem)
            # Derive parameters based on currItem
            #sessionArgs.printAll("START NEW SESSION==================")
            self.sessionManager.startNewSession(sessionArgs)

    def selectItem_byPath(self, pathStr):
        def findChild(item, childName, expanded=True):
            for i in range(0, item.childCount()):
                if str(childName) in item.child(i).text(self.column_name):
                    if expanded:
                        self.getChildrenExpanded(item.child(i))
                    return item.child(i)
            
        pathDict = self.utils.makeXNATPathDictionary(pathStr)
        #print ("PATH DICT: " + str(pathDict))
        if not self.viewWidget.findItems(pathDict['projects'],1): self.loadProjects()
        self.viewWidget.setCurrentItem(self.viewWidget.findItems(pathDict['projects'],1)[0])
        self.getChildrenExpanded(self.viewWidget.currentItem())
    
        if (pathDict['subjects']):
            self.viewWidget.setCurrentItem(findChild(self.viewWidget.currentItem(), pathDict['subjects']))
            if (pathDict['experiments']):
                self.viewWidget.setCurrentItem(findChild(self.viewWidget.currentItem(), pathDict['experiments']))
                if (pathDict['scans']):
                    self.viewWidget.setCurrentItem(findChild(self.viewWidget.currentItem(), pathDict['scans']))
        if (pathDict['resources']):
            self.viewWidget.setCurrentItem(findChild(self.viewWidget.currentItem(), pathDict['resources']))
            if (pathDict['files']):
                self.viewWidget.setCurrentItem(findChild(self.viewWidget.currentItem(), pathDict['files']))





  




 
