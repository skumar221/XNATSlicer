from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import urllib2

import XnatView



comment = """
XnatTreeView is a class of the XnatView class.  It 
uses QTreeWidget to describe the Xnat file system accessed,
presenting them in a tree-node hierarchy.

The view classes (and subclasses) ultimately communicate
with the load and save workflows.   
"""







class XnatTreeView(XnatView.XnatView):
    """ Initiate globals.
    """  



    
    def setup(self):

        
        #----------------------
        # TreeView
        #----------------------
        self.viewWidget = qt.QTreeWidget()
        self.viewWidget.setHeaderHidden(False)       
        treeWidgetSize = qt.QSize(100, 200)
        self.viewWidget.setBaseSize(treeWidgetSize)


        #----------------------
        # TreeView Columns
        #----------------------
        self.viewWidget.setColumnCount(3)
        self.column_name = 0
        self.column_category = 1
        self.column_size = 2
        columnLabels = []
        columnLabels.append("Name")
        columnLabels.append("Category")
        columnLabels.append("Size")
        self.viewWidget.setHeaderLabels(columnLabels)


        #----------------------
        # Fonts
        #----------------------
        self.itemFont_folder = qt.QFont("Arial", self.browser.utils.fontSize, 25, False)
        self.itemFont_file = qt.QFont("Arial", self.browser.utils.fontSize, 75, False)
        self.itemFont_category = qt.QFont("Arial", self.browser.utils.fontSize, 25, True)

        
        #----------------------
        # Tree-related globals
        #----------------------
        self.dirText = None     
        self.currItem = None
        self.currLoadable = None        

        
        #----------------------
        # Scene globals
        #----------------------
        self.lastButtonClicked = None 

        
        #----------------------
        # Clear Scene dialog
        #----------------------
        self.initClearDialog()

        
        #----------------------
        # Folder masks
        #----------------------
        self.applySlicerFolderMask = True
        self.hideSlicerHelperFolders = True

        
        #----------------------
        # Delete dialog
        #----------------------
        self.deleteDialog = qt.QMessageBox()       



        
    def loadProjects(self):
        """ Descriptor
        """
        self.viewWidget.clear()
        #print(self.browser.utils.lf(), "Retrieving projects. Please wait...","")
        projects, sizes = self.browser.XnatCommunicator.getFolderContents(['/projects'], 'ID')
        
        if not projects: return False

        
        #----------------------
        # Init TreeView
        #----------------------
        self.makeTreeItems(parentItem = self.viewWidget, 
                           children = projects, 
                           categories = ['projects' for p in projects], 
                           expandible = [0 for p in projects])

        self.viewWidget.connect("itemExpanded(QTreeWidgetItem *)",
                                self.getChildrenExpanded)
        self.viewWidget.connect("itemClicked(QTreeWidgetItem *, int)",
                                self.processTreeNode)
        return True


    



            

    def makeRequiredSlicerFolders(self, path = None):       
        if self.sessionManager.sessionArgs:
            self.browser.XnatCommunicator.makeDir(os.path.dirname(self.sessionManager.sessionArgs['saveDir']))
            self.browser.XnatCommunicator.makeDir(os.path.dirname(self.sessionManager.sessionArgs['sharedDir']))



            
    def getParentItemByCategory(self, item, category):
        """ Returns a parent item based on it's Xnat category.  For instance, if
           you want the 'experiments' parent of an item, returns that parent item.
        """
        parents = self.getParents(item)
        for p in parents:
            if category in p.text(self.column_category):
                return p
        return None 


    
    
    def getTreeItemType(self, item):
        
        #------------------------
        # Standard Xnat folder
        #------------------------
        for k, dictItem in self.browser.utils.xnatDepthDict.iteritems():
            if item.text(self.column_category).strip(" ") == dictItem:
                return dictItem

            
        #------------------------
        # Resource folder
        #------------------------
        if item.text(self.column_category).strip(" ") == "resources":
            return "resources"

        
        #------------------------
        # File
        #------------------------
        if item.text(self.column_category).strip(" ") == "files":
            return "files"       

        
        #------------------------
        # Slicer file 
        #------------------------
        if self.applySlicerFolderMask:
            if item.text(self.column_category).strip(" ") == self.browser.utils.slicerDirName:
                return "slicerFile"


            
            
    def setEnabled(self, bool):
        """ (INHERITED from XnatView)  Enables or disables the view widget.
        """
        self.viewWidget.setEnabled(bool)



            
    def initClearDialog(self):
        """ Initiates/resets dialog for window to clear the current scene.
        """
        try: 
            self.clearSceneDialog.delete()
        except: pass
        self.clearSceneDialog = qt.QMessageBox()
        self.clearSceneDialog.setStandardButtons(qt.QMessageBox.Yes | 
                                                 qt.QMessageBox.No)
        self.clearSceneDialog.setDefaultButton(qt.QMessageBox.No)
        self.clearSceneDialog.setText("In order to load your selection " + 
                                      "you have to clear the current scene." + 
                                      "\nAre you sure you want to clear?")



        
    def getXnatDepth(self, item):
        """ For use in the Category' column of a given tree node.
            Returns the depth level of where a tree item is in the Xnat 
            hierarchy: projects, subjects, experiments, scans and resources.
        """
        parents= self.getParents(item)  
        returnStr = ""   
        try: 
            returnStr = str(self.browser.utils.xnatDepthDict[len(parents)-1]).lower()
        except:          
            returnStr = "resources"    

            
        # NOTE:   The return string needs to have some spaces before it to 
        #         visually reflect where it is in the hierarchy.  This is for
        #         display purposes in the 'Category' column of the treeView.

        
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
        for i in range(0, len(parents)-1): 
            spaceStr += "  "
        return spaceStr



    
    def getXnatDir(self, parents):
        """ Constructs a directory structure based on the default Xnat 
            organizational scheme, utilizing the tree hierarchy. Critical to 
            communication with Xnat.
            Ex. parents = [exampleProject, testSubj, testExpt, scan1, images], 
            then returns: 
            'projects/exampleProject/subjects/testSubj/experiments/testExpt/scans/scan1/resources/images'  
        """  
        isResource = False
        isSlicerFile = False
        dirStr = "/"        

        
        #------------------------
        # Construct preliminary path
        #------------------------
        XnatDepth = 0        
        for item in parents:          
            # for resource folders
            if 'resources' in item.text(self.column_category).strip(" "): 
                isResource = True            
            # for masked slicer folders
            elif ((self.browser.utils.slicerDirName in item.text(self.column_category)) 
                  and self.applySlicerFolderMask): 
                isSlicerFile = True
            # construct directory string
            dirStr += "%s/%s/"%(item.text(self.column_category).strip(" "), 
                                item.text(self.column_name))
            XnatDepth+=1

            
        #------------------------
        # Modify if path has 'resources' in it
        #------------------------
        if isResource:         
            # append "files" if resources folder          
            if 'resources' in parents[-1].text(self.column_category).strip(" "):
                dirStr += "files"           
            # cleanup if at files level            
            elif 'files'  in parents[-1].text(self.column_category).strip(" "):
                dirStr = dirStr[:-1]          
            # if on a files          
            else:
                dirStr =  "%s/files/%s"%(os.path.dirname(dirStr), 
                                         os.path.basename(dirStr))  

                
        #------------------------
        # Modify for Slicer files
        #------------------------
        if isSlicerFile:
            #print self.browser.utils.lf() + "IS SLICER FILE!" 
            self.currLoadable = "scene"
            dirStr = ("%s/resources/%s/files/%s"%(os.path.dirname(os.path.dirname(os.path.dirname(dirStr))),
                                                  self.browser.utils.slicerDirName,
                                                  os.path.basename(os.path.dirname(dirStr))))   

            
        #------------------------
        # For all others  
        #------------------------
        else:
            if XnatDepth < 4: 
                dirStr += self.browser.utils.xnatDepthDict[XnatDepth] 
        return dirStr



    
    def getTreeItemInfo(self, item):   
        """Disects a given tree item and returns various useful attributes."""
        itemText = item.text(self.column_name)
        itemExt = itemText.partition(".")[2]     
        fullPath = self.getXnatDir(self.getParents(item))
        upFolders = fullPath.split("/")
        upFolders = upFolders[1:]
        upPaths = []      
        upPaths.append("/%s"%(upFolders[0]))
        for i in range(1, len(upFolders)-1):
            upPaths.append("%s/%s"%(upPaths[i-1], upFolders[i]))          
        upPaths.reverse()        
        upFolders.reverse()   
        return itemText, itemExt, fullPath, upPaths, upFolders   



    
    def getParents(self, item):
        """Returns the parents of a specific treeNode 
            all the way to the "project" level
        """
        parents = []
        while(item):
          parents.insert(0, item)
          item = item.parent()
        return parents




    
    def determineExpanded(self, item):
        """Determines if the current treeItem is expanded
        """      
        if item.childIndicatorPolicy() == 0:
            self.getChildren(item, expanded = True) 



            
    def getChildrenExpanded(self, item):
        """ When the user interacts with the treeView, this is a hook 
            method that gets the branches of a treeItem and expands them 
        """ 
        self.processTreeNode(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.column_category):
            self.getChildren(item, expanded = True) 


            
            
    def getChildrenNotExpanded(self, item):
        """ When the user interacts with the treeView, this is a hook 
            method that gets the branches of a treeItem and does not 
            expand them 
        """ 
        self.processTreeNode(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.column_category):
            self.getChildren(item, expanded = False)



            
    def processTreeNode(self, item, col):
        """ The purpose of this function
        """
        if item==None:
            item = self.currItem
        else:
            self.currItem = item

            
        self.viewWidget.setCurrentItem(item)
        self.currLoadable = None

        

        #------------------------
        # Check if at saveable/loadable level 
        #------------------------
        isSubject = 'subjects' in item.text(self.column_category).strip(" ")
        isResource = 'resources' in item.text(self.column_category).strip(" ")
        isExperiment = 'experiments' in item.text(self.column_category).strip(" ")
        isScan = 'scans' in item.text(self.column_category).strip(" ")
        isFile = 'files' in item.text(self.column_category).strip(" ")
        isSlicerFile = self.browser.utils.slicerDirName.replace("/","") in item.text(self.column_category).strip(" ")


        
        #------------------------
        # Enable load/save at the default save level
        #------------------------
        self.browser.XnatButtons.setEnabled('save', False)
        self.browser.XnatButtons.setEnabled('load', False)
        self.browser.XnatButtons.setEnabled('delete', False)
        self.browser.XnatButtons.setEnabled('addProj', True)
        
        if isExperiment or isScan:
            self.browser.XnatButtons.setEnabled('save', True)
            self.browser.XnatButtons.setEnabled('load', True)
            
        elif isFile or isSlicerFile or isResource:
            self.browser.XnatButtons.setEnabled('save', True)
            self.browser.XnatButtons.setEnabled('load', True)
            self.browser.XnatButtons.setEnabled('delete', True)


            
        #------------------------
        # If mask is enabled, determine if item is a slicer file
        #------------------------
        if self.applySlicerFolderMask:
            if item.text(self.column_category) == self.browser.utils.slicerDirName:
                isFile = True    


                
        #------------------------
        # File item routines
        #------------------------
        if isFile or isSlicerFile:
            ext = item.text(self.column_name).rsplit(".")
            # check extension
            if (len(ext)>1):
                # recognizable extensions        
                if self.browser.utils.isRecognizedFileExt(ext[1]):
                    # scene package
                    for ext_ in self.browser.utils.packageExtensions:
                        if ext_.replace(".","") in ext[1]: 
                            # set currloadable to scene                        
                            self.currLoadable = "scene"
                            return
                    # generic file
                    else:
                        # set currloadable to file
                        self.currLoadable = "file"
                        return   


                    
        #------------------------
        # User is at the default load/save level, default loader is dicom     
        #------------------------
        if self.browser.utils.defaultXnatSaveLevel in item.text(self.column_category).strip(" "):
            self.currLoadable = "mass_dicom" 
            return



        
        
    def getXnatPathObject(self, item):    
        """ Decriptor
        """
        pathObj = {}
        pathObj['pathDict'] = {
            'projects' : None,
            'subjects' : None,
            'experiments' : None,
            'scans' : None,
            'Slicer' : None
        }

        
        pathObj['parents'] = self.getParents(item)
        xnatDir = self.getXnatDir(pathObj['parents'])
    
        pathObj['childQueryPaths'] = [xnatDir if not '/scans/' in xnatDir else xnatDir + "files"]
        pathObj['currPath'] = os.path.dirname(pathObj['childQueryPaths'][0])        
       
        #
        # Construct path dictionary
        #
        splitter = [ s for s in pathObj['currPath'].split("/") if len(s) > 0 ]
        for i in range(0, len(splitter)):
            key = splitter[i]
            if key in pathObj['pathDict'] and i < len(splitter) - 1:
                pathObj['pathDict'][key] = splitter[i+1]

        
        pathObj['childMetadataTag'] = 'label'
        pathObj['currMetadataTag'] = 'label'
        parlen = len(pathObj['parents'])

        
        # print "\n\n%s %s"%(self.browser.utils.lf(), parlen)
        
        if parlen == 3: 
            pathObj['childMetadataTag'] = "ID"  # SCAN level
        elif parlen > 3:
            pathObj['currMetadataTag'] = 'ID'
            pathObj['childMetadataTag'] = 'Name'
            


            
        pathObj['childCategory'] = os.path.basename(pathObj['childQueryPaths'][0])

        
        #-----------------------------
        # For Slicer files at the experiment level
        #-------------------------------
        if pathObj['childQueryPaths'][0].endswith('/scans'):
            pathObj['slicerQueryPaths'] = []
            pathObj['slicerQueryPaths'].append(pathObj['currPath'] + '/resources/Slicer/files')
            pathObj['slicerMetadataTag'] = 'Name'



        return pathObj


        
            
    def isDICOMFolder(self, item):       
        dicomCount = 0
        for x in range(0, item.childCount()):          
            try:
                child = item.child(x)
                ext = child.text(self.column_name).rsplit(".")[1]            
                if self.browser.utils.isDICOM(ext):
                    dicomCount +=1
            except Exception, e:
                pass        
        if dicomCount == item.childCount():
                return True
        return False



    
    def setCurrItemToChild(self, item = None, childFileName = None):
        if not item:
            item = self.currItem     
        self.getChildrenExpanded(item)
        if childFileName:
            for x in range(0, item.childCount()):
                child = item.child(x)
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
        if method=="currItem":            
            
            # Sometimes we have to reset the curr item
            if not self.viewWidget.currentItem(): 
                self.viewWidget.setCurrentItem(self.currItem)
                
            # Derive parameters based on currItem
            self.sessionManager.startNewSession(sessionArgs)



            
    def selectItem_byPath(self, pathStr):
        def findChild(item, childName, expanded=True):
            for i in range(0, item.childCount()):
                if str(childName) in item.child(i).text(self.column_name):
                    if expanded:
                        self.getChildrenExpanded(item.child(i))
                    return item.child(i)
                

        #------------------------
        # Break apart pathStr to its Xnat categories
        #------------------------
        pathDict = self.browser.utils.makeXnatPathDictionary(pathStr)


        #------------------------
        # Reload projects if it can't find the project initially
        #------------------------
        if not self.viewWidget.findItems(pathDict['projects'],1): 
            self.loadProjects()


        #------------------------
        # Start by setting the current item at the project level, get its children
        #------------------------
        self.viewWidget.setCurrentItem(self.viewWidget.findItems(pathDict['projects'],1)[0])
        self.getChildrenExpanded(self.viewWidget.currentItem())


        #------------------------
        # Proceed accordingly to its lower levels
        #------------------------
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





    
        
    def getChildren(self, item, expanded, setCurrItem = True):
            """ Gets the branches of a particular treeItem via an XnatCommunicator 
            Get call.
            """       
    
            #--------------------
            # Selected Item management
            #--------------------  
            if not item: return
            if setCurrItem: self.currItem = item
            self.viewWidget.setCurrentItem(item)              

            
            #--------------------
            # Remove existing children for reload
            #--------------------
            item.takeChildren()

            
            #--------------------
            # Get path obj
            #--------------------           
            pathObj = self.getXnatPathObject(item)

            
            #--------------------
            # Get childNames
            #-------------------- 
            
            #
            # Other paths
            #
            childNames, sizes = self.browser.XnatCommunicator.getFolderContents(pathObj['childQueryPaths'],  metadataTag = pathObj['childMetadataTag'])
            pathObj['childCategories'] = [pathObj['childCategory'] for x in range(len(childNames))]
            
            #
            # Slicer Paths
            #
            if 'slicerQueryPaths' in pathObj:
                
                # Children for slicer path
                childNames2, sizes2 = self.browser.XnatCommunicator.getFolderContents(pathObj['slicerQueryPaths'], metadataTag = pathObj['slicerMetadataTag'])  
                 
                # Sizes
                if sizes and sizes2:
                    sizes = sizes + sizes2
                else:
                    sizes = ["" for x in range(len(childNames))]
                    if sizes2: 
                        sizes += sizes2
                        
                # Categories
                pathObj['childCategories'] = pathObj['childCategories'] + ['Slicer' for x in range(len(childNames2))]
                
                # put children together
                childNames = childNames + childNames2        


            #
            # Determine expandibility
            #    
            expandible = []
            for c in pathObj['childCategories']:
                expandible.append(1 if ('Slicer' in c or 'files' in c) else 0)
               
 
            self.makeTreeItems(parentItem = item, 
                               children = childNames, 
                               categories = pathObj['childCategories'], 
                               sizes = sizes, 
                               expandible = expandible)
            item.setExpanded(True)
            self.viewWidget.setCurrentItem(item) 





    
    def makeTreeItems(self, parentItem, children = [], categories = 'xnatFolder', sizes = None, expandible = None):
        """Creates a set of items to be put into the QTreeWidget based
           upon its parents, its children and the Xnat.
        """
        
        if len(children) == 0: return
        
        
        #------------------------
        # Add children to parentItem
        #------------------------
        treeItems = []
        for i in range(0, len(children)):
            rowItem = qt.QTreeWidgetItem(parentItem)

            #
            # Set text
            #
            rowItem.setText(self.column_name, children[i])

            #
            # Set expanded (0 = expandable, 1 = not)
            #
            rowItem.setChildIndicatorPolicy(expandible[i])          
            
            #
            # Set category
            #
            rowItem.setText(self.column_category, categories[i])  

            #
            # Set aesthetics and metadata
            #
            rowItem.setFont(self.column_name, self.itemFont_folder) 
            rowItem.setFont(self.column_size, self.itemFont_category)
            rowItem.setFont(self.column_category, self.itemFont_category) 
            
            self.changeFontColor(rowItem, False, "grey", self.column_size)
            self.changeFontColor(rowItem, False, "grey", self.column_category)
            if ('Slicer' in categories[i] or 'files' in categories[i]):
                self.changeFontColor(rowItem, False, "green", self.column_name)
           
            #
            # Set size, if needed
            #
            if sizes and isinstance(sizes, list) and len(sizes[i]) > 0:
                rowItem.setText(self.column_size, self.browser.utils.bytesToMB(sizes[i]) + " MB")
            
    
            # Add to array
            treeItems.append(rowItem) 

            
        #    
        # For projects only
        #
        if str(parentItem.__class__) == "<class 'PythonQt.QtGui.QTreeWidget'>":
            parentItem.addTopLevelItems(treeItems)
            return
        
        parentItem.addChildren(treeItems)
