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
    """ Inherits the XnatView class.  Uses a "Tree" type
        approach to present the XNAT database hierarchy. 
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
        self.columns = { 'name': {'string' : 'Name', 'location' : 0}, 
                    'category': {'string' : 'Category', 'location' : 1}, 
                    'description': {'string' : 'Description' , 'location' : 2}, 
                    'size': {'string' : 'Size' , 'location' : 3} 
                   }
        self.viewWidget.setColumnCount(len(self.columns))
        headers = []
        for key in self.columns:
            headers.insert(self.columns[key]['location'], self.columns[key]['string'])
        self.viewWidget.setHeaderLabels(headers)


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



        
    def loadProjects(self, filters = None):
        """ Descriptor
        """
        self.viewWidget.clear()
        #print(self.browser.utils.lf(), "Retrieving projects. Please wait...","")


        if self.browser.XnatCommunicator.projectCache != None:
            projectContents = self.browser.XnatCommunicator.projectCache
        else:
            projectContents = self.browser.XnatCommunicator.getFolderContents(queryUris = ['/projects'], 
                                                                              metadataTags = self.browser.utils.XnatMetadataTags_projects,
                                                                              queryArguments = ['accessible'])

        
        #---------------------
        # Exit if no projects can be found.
        #---------------------
        if not projectContents: 
            return False

        
        
        #----------------------
        # Init TreeView
        #----------------------
        # The 'ID' tag is either 'ID' or 'id' and 
        # we need to test for both.
        try: 
            projContents = projectContents[self.getNameTagByLevel('projects')]
        except Exception, e:
            try: 
                projContents = projectContents[self.getNameTagByLevel('projects').lower()]
            except Exception, e:
                print self.browser.utils.lf(), str(e)
                return False
                

            
        #----------------------
        # Make tree Items from projects
        #----------------------           
        self.makeTreeItems(parentItem = self.viewWidget, 
                           children = projContents, 
                           metadata = {'__level' : ['projects' for p in projectContents['name']]}, 
                           expandible = [0 for p in projectContents['name']])
        self.viewWidget.connect("itemExpanded(QTreeWidgetItem *)", self.getChildrenExpanded)
        self.viewWidget.connect("itemClicked(QTreeWidgetItem *, int)", self.processTreeNode)
        return True



    
    
    def getNameTagByLevel(self, level):
        """ Descriptor
        """
        if level == 'projects':
            return 'ID'
        elif level == 'subjects':
            return 'label'
        elif level == 'experiments':
            return 'label'
        elif level == 'scans':
            return 'ID'
        elif level == 'files':
            return 'Name'
        
        


            

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
            if category in p.text(self.columns['category']['location']):
                return p
        return None 


            
            
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
        self.clearSceneDialog.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        self.clearSceneDialog.setDefaultButton(qt.QMessageBox.No)
        self.clearSceneDialog.setText("Clear the current scene?")


        
        
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
            if 'resources' in item.text(self.columns['category']['location']).strip(" "): 
                isResource = True            
            # for masked slicer folders
            elif ((self.browser.utils.slicerDirName in item.text(self.columns['category']['location'])) 
                  and self.applySlicerFolderMask): 
                isSlicerFile = True
            # construct directory string
            dirStr += "%s/%s/"%(item.text(self.columns['category']['location']).strip(" "), 
                                item.text(self.columns['name']['location']))
            XnatDepth+=1

            
        #------------------------
        # Modify if path has 'resources' in it
        #------------------------
        if isResource:         
            # append "files" if resources folder          
            if 'resources' in parents[-1].text(self.columns['category']['location']).strip(" "):
                dirStr += "files"           
            # cleanup if at files level            
            elif 'files'  in parents[-1].text(self.columns['category']['location']).strip(" "):
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
        itemText = item.text(self.columns['name']['location'])
        itemExt = itemText.partition(".")[2]     
        fullUri = self.getXnatDir(self.getParents(item))
        upFolders = fullUri.split("/")
        upFolders = upFolders[1:]
        upUris = []      
        upUris.append("/%s"%(upFolders[0]))
        for i in range(1, len(upFolders)-1):
            upUris.append("%s/%s"%(upUris[i-1], upFolders[i]))          
        upUris.reverse()        
        upFolders.reverse()   
        return itemText, itemExt, fullUri, upUris, upFolders   



    
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
        if not 'files' in item.text(self.columns['category']['location']):
            self.getChildren(item, expanded = True) 


            
            
    def getChildrenNotExpanded(self, item):
        """ When the user interacts with the treeView, this is a hook 
            method that gets the branches of a treeItem and does not 
            expand them 
        """ 
        self.processTreeNode(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.columns['category']['location']):
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
        isSubject = 'subjects' in item.text(self.columns['category']['location']).strip(" ")
        isResource = 'resources' in item.text(self.columns['category']['location']).strip(" ")
        isExperiment = 'experiments' in item.text(self.columns['category']['location']).strip(" ")
        isScan = 'scans' in item.text(self.columns['category']['location']).strip(" ")
        isFile = 'files' in item.text(self.columns['category']['location']).strip(" ")
        isSlicerFile = self.browser.utils.slicerDirName.replace("/","") in item.text(self.columns['category']['location']).strip(" ")


        
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
            if item.text(self.columns['category']['location']) == self.browser.utils.slicerDirName:
                isFile = True    


                
        #------------------------
        # File item routines
        #------------------------
        if isFile or isSlicerFile:
            ext = item.text(self.columns['name']['location']).rsplit(".")
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
        if self.browser.utils.defaultXnatSaveLevel in item.text(self.columns['category']['location']).strip(" "):
            self.currLoadable = "mass_dicom" 
            return



        
        
    def getXnatUriObject(self, item):    
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

        
        pathObj['childQueryUris'] = [xnatDir if not '/scans/' in xnatDir else xnatDir + "files"]
        pathObj['currUri'] = os.path.dirname(pathObj['childQueryUris'][0])  
        pathObj['currLevel'] = xnatDir.split('/')[-1] if not '/scans/' in xnatDir else 'files'

       
        #
        # Construct path dictionary
        #
        splitter = [ s for s in pathObj['currUri'].split("/") if len(s) > 0 ]
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
            


            
        pathObj['childCategory'] = os.path.basename(pathObj['childQueryUris'][0])

        
        #-----------------------------
        # For Slicer files at the experiment level
        #-------------------------------
        if pathObj['childQueryUris'][0].endswith('/scans'):
            pathObj['slicerQueryUris'] = []
            pathObj['slicerQueryUris'].append(pathObj['currUri'] + '/resources/Slicer/files')
            pathObj['slicerMetadataTag'] = 'Name'



        return pathObj


        
            
    def isDICOMFolder(self, item):       
        dicomCount = 0
        for x in range(0, item.childCount()):          
            try:
                child = item.child(x)
                ext = child.text(self.columns['name']['location']).rsplit(".")[1]            
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
                if child.text(self.columns['name']['location']) == childFileName:
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



            
    def selectItem_byUri(self, pathStr):
        def findChild(item, childName, expanded=True):
            for i in range(0, item.childCount()):
                if str(childName) in item.child(i).text(self.columns['name']['location']):
                    if expanded:
                        self.getChildrenExpanded(item.child(i))
                    return item.child(i)
                

        #------------------------
        # Break apart pathStr to its Xnat categories
        #------------------------
        pathDict = self.browser.utils.makeXnatUriDictionary(pathStr)


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
            pathObj = self.getXnatUriObject(item)
            currXnatLevel = pathObj['currLevel']
            
            #--------------------
            # Get folder Contents
            #--------------------      
            metadata = self.browser.XnatCommunicator.getFolderContents(pathObj['childQueryUris'], self.browser.utils.XnatMetadataTagsByLevel(currXnatLevel))
            childNames = metadata[self.getNameTagByLevel(currXnatLevel)]

            # Set the categories
            metadata['__level'] = [pathObj['childCategory'] for x in range(len(childNames))]

            
            #
            # Slicer Uris
            #
            if 'slicerQueryUris' in pathObj:
                # Children for slicer path
                slicerFolderContents = self.browser.XnatCommunicator.getFolderContents(pathObj['slicerQueryUris'], self.browser.utils.XnatMetadataTagsByLevel('files'))  
                slicerChildNames = slicerFolderContents[self.getNameTagByLevel('files')]
                childNames = childNames + slicerChildNames    
                metadata['__level'] = metadata['__level'] + ['Slicer' for x in range(len(slicerChildNames))]  

        
            #
            # Determine expandibility
            #    
            expandible = []
            for i in range(0, len(metadata['__level'])):
                 level = metadata['__level'][i]
                 #
                 # 'files' and 'Slicer' category
                 # immediately ruled as unexpandable (1).
                 #
                 if (level == 'files' or level == 'Slicer') :
                     expandible.append(1)
                 else:
                     expandible.append(0)

                     
            self.makeTreeItems(parentItem = item, children = childNames, metadata = metadata, expandible = expandible)
            
            item.setExpanded(True)
            self.viewWidget.setCurrentItem(item) 




    def condenseDicomsToOneName(self, names):
        returnName = names[0]
        stopIndex = len(returnName) - 1

        
        for i in range(1, len(names)):
            # cycle through characters in name.
            for j in range(0, len(names[i])):
                #print (j, names[i], returnName, len(names[i]), len(returnName))
                if j > len(returnName) - 1:
                    break
                elif j == len(returnName) - 1 or returnName[j] != names[i][j]:
                    stopIndex = j

        return [returnName[0:stopIndex] + "..."]
        
    
    def makeTreeItems(self, parentItem, children = [],  metadata = {}, expandible = None):
        """Creates a set of items to be put into the QTreeWidget based
           upon its parents, its children and the Xnat.
        """
        
        if len(children) == 0: return


        #----------------
        # Get the DICOM count if at 'scans'
        #----------------
        if (metadata['__level'][0] == 'files'):
            pathObj = self.getXnatUriObject(parentItem.parent())
            parentXnatLevel = pathObj['currLevel']
            if parentXnatLevel == 'scans':
                if self.isDICOMFolder(parentItem):                
                    children = self.condenseDicomsToOneName(children)
                    

        
        
        #------------------------
        # Add children to parentItem
        #------------------------
        treeItems = []
        for i in range(0, len(children)):
            rowItem = qt.QTreeWidgetItem(parentItem)

            #
            # Set text
            #
            rowItem.setText(self.columns['name']['location'], children[i])

            #
            # Set expanded (0 = expandable, 1 = not)
            #
            rowItem.setChildIndicatorPolicy(expandible[i])          
            
            #
            # Set category
            #
            rowItem.setText(self.columns['category']['location'], metadata['__level'][i])  

            #
            # Set aesthetics and metadata
            #
            rowItem.setFont(self.columns['name']['location'], self.itemFont_folder) 
            #rowItem.setFont(self.columns['size']['location'], self.itemFont_category)
            rowItem.setFont(self.columns['category']['location'], self.itemFont_category) 
            
            #self.changeFontColor(rowItem, False, "grey", self.columns['size']['location'])
            self.changeFontColor(rowItem, False, "grey", self.columns['category']['location'])
            
            if ('Slicer' in metadata['__level'][i] or 'files' in metadata['__level'][i]):
                self.changeFontColor(rowItem, False, "green", self.columns['name']['location'])
           
            #
            # Set size, if needed
            #
            #if sizes and isinstance(sizes, list) and len(sizes[i]) > 0:
            #    rowItem.setText(self.columns['size']['location'], self.browser.utils.bytesToMB(sizes[i]) + " MB")
            
    
            # Add to array
            treeItems.append(rowItem) 

            
        #    
        # For projects only
        #
        if str(parentItem.__class__) == "<class 'PythonQt.QtGui.QTreeWidget'>":
            parentItem.addTopLevelItems(treeItems)
            return
        
        parentItem.addChildren(treeItems)
