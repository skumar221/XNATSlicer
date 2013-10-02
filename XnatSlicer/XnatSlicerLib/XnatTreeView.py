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
        self.initColumns()


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


        

    def initColumns(self):
        """
        """
        self.columns = {}
        for key in self.browser.utils.XnatMetadataTags_all:
            self.columns[key] = {}

        #
        # Apply metadata key to the columns.  Manuplulate
        # the string values of the tags to make them more
        # human-readable.
        #
        for key in self.columns:
            strVal = key.replace('_',' ').title()
            strVal = strVal.replace('Pi', 'PI')
            strVal = strVal.replace('Uri', 'URI')
            strVal = strVal.replace(' 497', '')
            strVal = strVal.replace('Id', 'ID')
            self.columns[key]['displayname'] = strVal

            
        #
        # XnatLevel column is not part of the metadata set
        # so we're adding it.
        #  
        self.columns['MERGED_LABEL'] = {}  
        self.columns['MERGED_LABEL']['displayname'] = 'Name/ID/Label'   
        self.columns['XNAT_LEVEL'] = {}  
        self.columns['XNAT_LEVEL']['displayname'] = 'Level'      


        self.columnKeyOrder = {}
        
        self.columnKeyOrder['ALL'] = [
            'MERGED_LABEL',
            'XNAT_LEVEL',
        ]

        self.columnKeyOrder['LABELS'] = [
            'ID',
            'id',
            'name',
            'Name',
            'label',
        ]

        
        self.columnKeyOrder['projects'] = [
            'last_accessed_497',
            'insert_user',
            'pi',
            'insert_date',
            'description',
        #    'secondary_ID',
        #    'pi_lastname',
        #    'pi_firstname',
        #    'project_invs',	
        #    'project_access_img',	
        #    'user_role_497',	
        #    'quarantine_status'
        #    'URI',
        ]

        self.columnKeyOrder['subjects'] = [
            'insert_date',
            'insert_user',
            'totalRecords'
        #    'project',
        #    'URI',
        ]

        
        self.columnKeyOrder['experiments'] = [
            'insert_date',
            'totalRecords',
            'date',
        #   'project',
        #   'xsiType',
        #   'ID',
        #   'xnat:subjectassessordata/id',
        #   'URI',
        ]

        self.columnKeyOrder['scans'] = [
            'series_description',
            'note',
            'type',
        #   'xsiType',
        #   'quality',
        #   'xnat_imagescandata_id',
        #   'URI',
        ]

        self.columnKeyOrder['resources'] = [
            'element_name',
            'category',
        #    'cat_id',
        #    'xnat_abstractresource_id',
        #    'cat_desc'
        ]

        self.columnKeyOrder['files'] = [
            'Size',
            'file_format',
        #    'file_content',
        #    'collection',
        #    'file_tags',
        #    'cat_ID',
        #    'URI'
        ]


        self.columnKeyOrder['slicer'] = [
            'Size',
            'file_format',
        #    'file_content',
        #    'collection',
        #    'file_tags',
        #    'cat_ID',
        #    'URI'
        ]


        #
        # Create a union of all the self.columnKeyOrder arrays.
        #
        allHeaders = self.browser.utils.uniqify(self.columnKeyOrder['ALL'] + 
                                                # Leaving this out as it will become part of MERGED_LABELS
                                                #  self.columnKeyOrder['LABELS'] + 
                                                self.columnKeyOrder['projects'] + 
                                                self.columnKeyOrder['subjects'] + 
                                                self.columnKeyOrder['experiments'] + 
                                                self.columnKeyOrder['resources'] + 
                                                self.columnKeyOrder['scans'] + 
                                                self.columnKeyOrder['files'] + 
                                                self.columnKeyOrder['slicer']
                                                )

        self.viewWidget.setColumnCount(len(allHeaders))
        headerLabels = []
        for header in allHeaders:
            self.columns[header]['location'] = len(headerLabels)
            headerLabels.append( self.columns[header]['displayname'])
            
        self.viewWidget.setHeaderLabels(headerLabels)
        self.showColumnsByNodeLevel()



        
    def getMergedLabelTagByLevel(self, level):
        """
        """
        level = level.lower()
        if level == 'projects': 
            #
            # NOTE: this would be in all caps if there were no query arguments.
            # since we only query projects that the user has access to, we have to 
            # use a lowercase 'id'.
            #
            return 'id'
        elif level == 'scans':
            return 'ID'
        elif level == 'subjects' or level == 'experiments':
            return 'label'
        elif level == 'files' or level == 'slicer':
            return 'Name'           



        
    def setValuesToTreeNode(self, treeNode = None, metadata = None):
        """
        """
        level = metadata['XNAT_LEVEL']

        #print "METADATA", metadata
        
        for key in metadata:
            value = metadata[key]
            self.columns[key]['value'] = value
            if 'location' in self.columns[key]:
                treeNode.setText(self.columns[key]['location'], value)
                treeNode.setFont(self.columns[key]['location'], self.itemFont_folder) 
        #
        # Set the value for MERGED_LABEL
        #        
        value = metadata[self.getMergedLabelTagByLevel(level)]

        #
        # return out if value is not defined.
        #
        if not value or value == None or len(value) == 0:
            return

        
        self.columns['MERGED_LABEL']['value'] = value

        
        treeNode.setText(self.columns['MERGED_LABEL']['location'], value)

        
        
        #
        # Set aesthetics
        #
        treeNode.setFont(self.columns['MERGED_LABEL']['location'], self.itemFont_folder) 
        treeNode.setFont(self.columns['XNAT_LEVEL']['location'], self.itemFont_category) 
        self.changeFontColor(treeNode, False, "grey", self.columns['XNAT_LEVEL']['location'])
        if 'Slicer' in metadata['XNAT_LEVEL'] or 'files' in metadata['XNAT_LEVEL']:
            self.changeFontColor(treeNode, False, "green", self.columns['MERGED_LABEL']['location'])

        return treeNode


        
    def getColumn(self, value):
        return self.columns[value]['location']




    def resizeColumns(self):
        for key in self.columns:
            if 'location' in self.columns[key]:
                self.viewWidget.resizeColumnToContents(self.columns[key]['location'])


            
    def showColumnsByNodeLevel(self, level = None):
        """
        """
        #----------------------
        # Hide all
        #----------------------
        for i in range(0, len(self.columns)):
            self.viewWidget.hideColumn(i)


        #----------------------
        # Keep everything hidden if no level enetered.
        #----------------------
        if level == None or len(level) == 0:
            return

        def showByKeys(keys):
            for key in keys:
                #print key
                if key in self.columns and 'location' in self.columns[key]:
                    location = self.columns[key]['location']
                    self.viewWidget.showColumn(location)
                

        #----------------------
        # Required columns
        #----------------------
        showByKeys(self.columnKeyOrder['ALL'])


        #----------------------
        # Show columns by level
        #----------------------
        showByKeys(self.columnKeyOrder[level])



        #----------------------
        # Resize columns
        #----------------------
        self.resizeColumns()


            


            
    def loadProjects(self, filters = None):
        """ Descriptor
        """
        self.viewWidget.clear()
        #print(self.browser.utils.lf(), "Retrieving projects. Please wait...","")


        defaultFilterButton = self.browser.XnatButtons.buttons['filter']['accessed']

        
        #----------------------
        # Get the projects if they're cashed (session-based)
        # otherwise the the projects via the REST call.
        #----------------------
        if self.browser.XnatCommunicator.projectCache != None:
            projectContents = self.browser.XnatCommunicator.projectCache
        else:
            projectContents = self.browser.XnatCommunicator.getFolderContents(queryUris = ['/projects'], 
                                                                              metadataTags = self.browser.utils.XnatMetadataTags_projects,
                                                                              queryArguments = ['accessible'])

        
        #----------------------
        # If there are filters, apply them.  Generate
        # treeNode names based on this premise.
        #----------------------
        nameTag = self.getMergedLabelTagByLevel(level = 'projects')
        if filters:
            currFilters = filters 
        else:
            currFilters = ['accessed']
            self.browser.XnatButtons.setButtonDown(category = 'filter' , name = 'accessed', isDown = True, callSignals = False)
        projectNames = self.browser.XnatFilter.filter(contents = projectContents, outputTag = nameTag, filterTags = currFilters)


        
        #----------------------
        # Update the contents based on the filter
        #----------------------
        updatedContents = {}
        for name in projectNames:
            for i in range(0, len(projectContents['id'])):
                if projectContents['id'][i] == name:
                    for key in projectContents:
                        if not key in updatedContents:
                            updatedContents[key] = []
                        if i < len(projectContents[key]):
                            updatedContents[key].append(projectContents[key][i])
                    

                            
        #----------------------
        # Make tree Items from projects
        #----------------------                
        updatedContents['XNAT_LEVEL'] = ['projects' for p in projectNames]
        self.makeTreeItems(parentItem = self.viewWidget, 
                           children = projectNames, 
                           metadata = updatedContents, 
                           expandible = [0 for p in projectNames])
        self.showColumnsByNodeLevel('projects')
        self.viewWidget.connect("itemExpanded(QTreeWidgetItem *)", self.getChildrenExpanded)
        self.viewWidget.connect("itemClicked(QTreeWidgetItem *, int)", self.manageTreeNode)

        

        #-----------------------
        # If there are no project names on the default
        # filter (i.e. 'accessed'), then revert to all.
        # NOTE: this only applies when the 'filters' parameter
        # isn't specified.  If the the 'filters' paraemter of 'accessed'
        # is specified, but there are no project names, nothing 
        # will display.
        #------------------------
        if (not filters or len(filters) == 0) and (not projectNames or len(projectNames) == 0):
            if defaultFilterButton.isDown():
                defaultFilterButton.click()
            
       
        return True
        

            

    def makeRequiredSlicerFolders(self, path = None):  
        """
        """     
        if self.sessionManager.sessionArgs:
            self.browser.XnatCommunicator.makeDir(os.path.dirname(self.sessionManager.sessionArgs['saveDir']))
            self.browser.XnatCommunicator.makeDir(os.path.dirname(self.sessionManager.sessionArgs['sharedDir']))



            
    def getParentItemByXnatLevel(self, item, category):
        """ Returns a parent item based on it's Xnat category.  For instance, if
            you want the 'experiments' parent of an item, returns that parent item.
        """
        parents = self.getParents(item)
        for p in parents:
            if category in p.text(self.columns['XNAT_LEVEL']['location']):
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
            communication with Xnat. Ex. parents = [exampleProject, testSubj, 
            testExpt, scan1, images], then returns: 
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
            #         
            # For resource folders
            #
            if 'resources' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" "): 
                isResource = True    
            #
            # For masked slicer folders
            #
            elif ((self.browser.utils.slicerDirName in item.text(self.columns['XNAT_LEVEL']['location'])) 
                  and self.applySlicerFolderMask): 
                isSlicerFile = True
            #
            # Construct directory string
            #
            dirStr += "%s/%s/"%(item.text(self.columns['XNAT_LEVEL']['location']).strip(" "), 
                                item.text(self.columns['MERGED_LABEL']['location']))
            XnatDepth+=1


            
        #------------------------
        # Modify if path has 'resources' in it
        #------------------------
        if isResource:    
            #     
            # Append "files" if resources folder 
            #         
            if 'resources' in parents[-1].text(self.columns['XNAT_LEVEL']['location']).strip(" "):
                dirStr += "files" 
            #
            # Cleanup if at files level 
            #           
            elif 'files'  in parents[-1].text(self.columns['XNAT_LEVEL']['location']).strip(" "):
                dirStr = dirStr[:-1]  
            #
            # If on a files      
            #    
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
        self.manageTreeNode(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.columns['XNAT_LEVEL']['location']):
            self.getChildren(item, expanded = True) 


            
            
    def getChildrenNotExpanded(self, item):
        """ When the user interacts with the treeView, this is a hook 
            method that gets the branches of a treeItem and does not 
            expand them 
        """ 
        self.manageTreeNode(item, 0)
        self.viewWidget.setCurrentItem(item)
        self.currItem = item
        if not 'files' in item.text(self.columns['XNAT_LEVEL']['location']):
            self.getChildren(item, expanded = False)



            
    def manageTreeNode(self, item, col):
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
        isProject = 'project' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isSubject = 'subjects' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isResource = 'resources' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isExperiment = 'experiments' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isScan = 'scans' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isFile = 'files' in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")
        isSlicerFile = self.browser.utils.slicerDirName.replace("/","") in item.text(self.columns['XNAT_LEVEL']['location']).strip(" ")


        #-------------------------
        # Show columns
        #-------------------------
        if isProject:
            self.showColumnsByNodeLevel('projects')
        elif isSubject:
            self.showColumnsByNodeLevel('subjects')
        elif isResource:
            self.showColumnsByNodeLevel('resources')
        elif isExperiment:
            self.showColumnsByNodeLevel('experiments')
        elif isScan:
            self.showColumnsByNodeLevel('scans')
        elif isFile:
            self.showColumnsByNodeLevel('files')
        if isSlicerFile:
            self.showColumnsByNodeLevel('slicer')


            
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
            if item.text(self.columns['XNAT_LEVEL']['location']) == self.browser.utils.slicerDirName:
                isFile = True    


                
        #------------------------
        # File item routines
        #------------------------
        if isFile or isSlicerFile:
            ext = item.text(self.columns['MERGED_LABEL']['location']).rsplit(".")
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
        if self.browser.utils.defaultXnatSaveLevel in item.text(self.columns['XNAT_LEVEL']['location']).strip(" "):
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
            


            
        pathObj['childXnatLevel'] = os.path.basename(pathObj['childQueryUris'][0])

        
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
                ext = child.text(self.columns['MERGED_LABEL']['location']).rsplit(".")[1]            
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
                if child.text(self.columns['MERGED_LABEL']['location']) == childFileName:
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
                if str(childName) in item.child(i).text(self.columns['MERGED_LABEL']['location']):
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
            # SPECIAL CASE: this filters out image
            # folders with no images in them.
            #-------------------- 
            queryArguments = None
            if currXnatLevel == 'experiments':
                queryArguments = ['imagesonly']


                
            #--------------------
            # Get folder Contents
            #-------------------- 
            metadata = self.browser.XnatCommunicator.getFolderContents(pathObj['childQueryUris'], self.browser.utils.XnatMetadataTagsByLevel(currXnatLevel), queryArguments)
            childNames = metadata[self.getMergedLabelTagByLevel(currXnatLevel)]

            #--------------------
            # Set the categories
            #--------------------
            metadata['XNAT_LEVEL'] = [pathObj['childXnatLevel'] for x in range(len(childNames))]

            
            #--------------------
            # Slicer URIs
            #--------------------
            if 'slicerQueryUris' in pathObj:
                slicerMetadata = self.browser.XnatCommunicator.getFolderContents(pathObj['slicerQueryUris'], self.browser.utils.XnatMetadataTagsByLevel('files'))
                slicerChildNames = slicerMetadata[self.getMergedLabelTagByLevel('files')]
                prevLen = len(childNames)
                childNames = childNames + slicerChildNames  
                #
                # Merge slicerMetadata with metadata
                #
                for key in slicerMetadata:
                    if not key in metadata:
                        metadata[key] = [''] * prevLen
                    metadata[key] += metadata[key] + slicerMetadata[key]
                    if (key == 'Size'):
                        for i in range(0, len(metadata[key])):
                            if metadata[key][i]:
                                metadata[key][i] = '%s MB'%(self.browser.utils.bytesToMB(metadata[key][i])) 
                metadata['XNAT_LEVEL'] = metadata['XNAT_LEVEL'] + ['Slicer' for x in range(len(slicerChildNames))]  
                
        
            #
            # Determine expandibility
            #    
            expandible = []
            for i in range(0, len(metadata['XNAT_LEVEL'])):
                 level = metadata['XNAT_LEVEL'][i]
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
        """
        """
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
        if (metadata['XNAT_LEVEL'][0] == 'files'):
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
            treeNode = qt.QTreeWidgetItem(parentItem)
            #
            # Set expanded (0 = expandable, 1 = not)
            #
            treeNode.setChildIndicatorPolicy(expandible[i])   
            #
            # Set other metadata
            #
            treeNodeMetadata = {}
            for key in metadata:
                if i < len(metadata[key]):
                    treeNodeMetadata[key] = metadata[key][i]
            treeNode = self.setValuesToTreeNode(treeNode, treeNodeMetadata)
            #
            # Add to array
            #
            if treeNode:
                treeItems.append(treeNode) 

            
        #    
        # For projects only
        #
        if str(parentItem.__class__) == "<class 'PythonQt.QtGui.QTreeWidget'>":
            parentItem.addTopLevelItems(treeItems)
            return
        
        parentItem.addChildren(treeItems)
