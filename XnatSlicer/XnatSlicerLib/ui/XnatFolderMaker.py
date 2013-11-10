from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import re
import urllib2

from XnatUtils import *




comment = """
XnatFolderMaker is used for creating new projects/folders within a given
Xnat host.  It manages talking to a given XnatIo and its associated
string inputs. 

TODO : 
"""




class XnatFolderMaker(qt.QWidget):
    """ Described above.
    """
    
    def __init__(self, parent, MODULE = None):
        """ Init function.
        """

        super(XnatFolderMaker, self).__init__()
        self.hide()
        self.setFixedWidth(500)
        
        #--------------------
        # Public vars.
        #--------------------        
        self.MODULE = MODULE

        

        self.dropdowns = {}
        self.lineEdits = {}
        self.errorLines = {}

        
        #--------------------
        # Make 'projects' dropdown
        #--------------------        
        self.projLabel = qt.QLabel("Project")
        self.dropdowns['projects'] = qt.QComboBox()

      
        self.dropdowns['projects'].connect("currentIndexChanged(QString)", self.populateSubjectDropdown)


        
        #--------------------
        # Make project lineEdit for foldername entry
        #-------------------- 
        self.lineEdits['projects'] = qt.QLineEdit()
        self.lineEdits['projects'].connect("textEdited(QString)", self.onProjectLineEdited)
        self.errorLines['projects'] = qt.QLabel()
        self.errorLines['projects'].setTextFormat(1)


        
        #--------------------
        # Make subject dropdown
        #--------------------         
        self.subjLabel = qt.QLabel("Subject")
        self.dropdowns['subjects'] = qt.QComboBox()


        
        #--------------------
        # Make subject lineEdit for foldername entry
        #--------------------  
        self.lineEdits['subjects'] = qt.QLineEdit()
        self.lineEdits['subjects'].connect("textEdited(const QString&)", self.onSubjectLineEdited)


        
        #--------------------
        # Make subject errorLabel
        #--------------------          
        self.errorLines['subjects'] = qt.QLabel()
        self.errorLines['subjects'].setTextFormat(1)



        #--------------------
        # Make experiment label, lineEdit and Error
        #--------------------   
        self.exptLabel = qt.QLabel("Experiment")
        self.lineEdits['experiments'] = qt.QLineEdit()
        self.errorLines['experiments'] = qt.QLabel()
        self.errorLines['experiments'].setTextFormat(1)



        #--------------------
        # Construct the layout for the modal
        #--------------------
        self._layout = qt.QGridLayout()
        existingCol = qt.QLabel("Existing")
        newCol = qt.QLabel("Add New")



        self.xsiList = qt.QComboBox()
        self.xsiList.addItems([key for key, value in self.MODULE.GLOBALS.XNAT_XSI_TYPES.iteritems()])
        


        #--------------------
        # Add all of the widgets.
        #--------------------
        self._layout.addWidget(existingCol, 0, 1)
        self._layout.addWidget(newCol, 0, 2)
        self._layout.addWidget(self.projLabel, 1, 0)
        self._layout.addWidget(self.dropdowns['projects'], 1, 1)
        self._layout.addWidget(self.lineEdits['projects'], 1, 2)
        self._layout.addWidget(self.errorLines['projects'], 2, 2)
        self._layout.addWidget(self.subjLabel, 3, 0)
        self._layout.addWidget(self.dropdowns['subjects'], 3, 1)
        self._layout.addWidget(self.lineEdits['subjects'], 3, 2)
        self._layout.addWidget(self.errorLines['subjects'], 4, 2)
        self._layout.addWidget(self.exptLabel, 5, 0)
        self._layout.addWidget(self.lineEdits['experiments'], 5, 2)
        self._layout.addWidget(self.errorLines['experiments'], 6, 2)
        self._layout.addWidget(self.xsiList, 5, 1)



        
        #--------------------
        # Create the necessary buttons.
        #--------------------
        self.createButton = qt.QPushButton()
        self.createButton.setText("Create")
        self.cancelButton = qt.QPushButton()
        self.cancelButton.setText("Cancel")
        buttonRow = qt.QDialogButtonBox()
        buttonRow.addButton(self.cancelButton, 2)
        buttonRow.addButton(self.createButton, 0)

        buttonRow.connect('clicked(QAbstractButton*)', self.onCreateButtonClicked)
        self._layout.addWidget(buttonRow, 7, 2)
        
        self.setLayout(self._layout)
        
        self.setWindowTitle("Add Folder to Xnat")
        self.setWindowModality(2)
        

        
        self.lineEdits['projects'].installEventFilter(self)
        self.lineEdits['subjects'].installEventFilter(self)
        self.lineEdits['experiments'].installEventFilter(self)

        self.dropdowns['projects'].installEventFilter(self)
        self.dropdowns['subjects'].installEventFilter(self)




        
    def eventFilter(self, ob, event):
        """
        """
        if ob == self.dropdowns['projects']:
  
            if event.type() == qt.QEvent.MouseButtonRelease:
                self.lineEdits['projects'].clear()
                #
                # Removes the focus box.  For good UX.
                #
                self.setLineEditsEnabled(False)
                self.setLineEditsEnabled(True)
                self.setDropdownsEnabled(True)

                
        elif ob == self.dropdowns['subjects']:
            if event.type() == qt.QEvent.MouseButtonRelease:
                self.lineEdits['subjects'].clear()
                #
                # Removes the focus box.  For good UX.
                #
                self.setLineEditsEnabled(False)
                self.setLineEditsEnabled(True)
                self.setDropdownsEnabled(True)


        elif ob == self.lineEdits['projects']:
            if event.type() == qt.QEvent.FocusIn:
                self.setDropdownsEnabled(False)

                
        elif ob == self.lineEdits['subjects']:
            if event.type() == qt.QEvent.FocusIn:
                self.setDropdownsEnabled(False, ['subjects'])
                if len(self.lineEdits['projects'].text) == 0:
                    self.setLineEditsEnabled(True)



        elif ob == self.lineEdits['experiments']:
            if event.type() == qt.QEvent.FocusIn:
                return
            #print "EXDPERIMENT FOCUSED"
            #   self.setDropdownsEnabled(True)
            #   self.setLineEditsEnabled(True)

                

            
    def show(self):
        """
        """


        for key, widget in self.lineEdits.iteritems():
            widget.clear()

            

        qt.QWidget.show(self)
        self.projectList = []
        def addToList(item):
            self.projectList.append(item.text(0))            
        self.MODULE.XnatView.loopProjectNodes(addToList)

        
        #--------------------
        # Use the currently selected View item to 
        # derive the project dropdowns.
        #--------------------           
        currProject = None
        currSubject = None
        proj = ""
        if (self.MODULE.XnatView.currentItem() != None):
            currProject = self.MODULE.XnatView.getParentItemByXnatLevel(self.MODULE.XnatView.currentItem(), "projects")
            currSubject = self.MODULE.XnatView.getParentItemByXnatLevel(self.MODULE.XnatView.currentItem(), "subjects")
            proj = currProject.text(self.MODULE.XnatView.columns['MERGED_LABEL']['location'])
            self.dropdowns['projects'].setCurrentIndex(self.dropdowns['projects'].findText(proj))
        else:
            proj = self.dropdowns['projects'].currentText 


            
        #--------------------
        # Populate the subject dropdown and set 
        # the index on the subject dropdown accordingly.
        #--------------------
        self.populateSubjectDropdown(proj) 
        if currSubject:
            self.dropdowns['subjects'].setCurrentIndex(self.dropdowns['subjects'].findText(currSubject.text(self.MODULE.XnatView.columns['MERGED_LABEL']['location'])))

            

        print self.projectList
        self.dropdowns['projects'].clear()
        self.dropdowns['projects'].addItems(self.projectList) 

        


        
            
    def populateSubjectDropdown(self, projectName):
        """ Utilizes 'XnatIo' to query for the subjects within a given
            project, provided by the argument.
        """

        if not projectName or len(projectName) == 0:
            return
        #--------------------
        # Get the raw subjects
        #--------------------
        subjs_raw = self.MODULE.XnatIo.getFolderContents('/projects/' + projectName + '/subjects', ['label'])
        subjs_name = []

        #print "\n\n*****************projectName: ", projectName
        print subjs_raw

        #--------------------
        # Add subjects to dropdown
        #--------------------
        for r in subjs_raw['label']:
            subjs_name.append(self.MODULE.XnatIo.getItemValue('/projects/' + projectName + '/subjects/' + str(urllib2.quote(r)), 'label'))
        self.dropdowns['subjects'].clear()
        self.dropdowns['subjects'].addItems(subjs_name)



    





    def onCreateButtonClicked(self,button):
        """ Callback if the create button is clicked. Communicates with
            XNAT to create a folder. Details below.  
        """
        
        #--------------------
        # If OK is clicked....
        #--------------------
        if 'create' in button.text.lower():

            #--------------------
            # Clear errors
            #--------------------
            self.errorLines['experiments'].setText("")
            self.errorLines['subjects'].setText("")
            self.errorLines['projects'].setText("")

            

            #--------------------
            # Construct URI based on XNAT rules.
            #--------------------
            xnatUri = "/projects/"
            if len(self.lineEdits['projects'].text)>0:
                xnatUri += self.lineEdits['projects'].text
                if len(self.lineEdits['subjects'].text)>0:
                    xnatUri += "/subjects/" + self.lineEdits['subjects'].text
                    if len(self.lineEdits['experiments'].text)>0:
                        xnatUri += "/experiments/" + self.lineEdits['experiments'].text
            else:
                xnatUri += self.dropdowns['projects'].currentText
                if len(self.lineEdits['subjects'].text)>0:
                    xnatUri += "/subjects/" + self.lineEdits['subjects'].text
                    if len(self.lineEdits['experiments'].text)>0:
                        xnatUri += "/experiments/" + self.lineEdits['experiments'].text
                else:
                    xnatUri += "/subjects/" + self.dropdowns['subjects'].currentText
                    if len(self.lineEdits['experiments'].text)>0:
                        xnatUri += "/experiments/" + self.lineEdits['experiments'].text
                        #
                        # IMPORTANT: Add the xsi for experiments
                        #
                        xnatUri += '?xsiType=' + self.MODULE.GLOBALS.XNAT_XSI_TYPES[self.xsiList.currentText]



            print self.MODULE.utils.lf(), xnatUri

            self.MODULE.XnatIo.makeFolder(xnatUri)
            slicer.app.processEvents()
            self.close()
            self.MODULE.XnatView.selectItem_byUri(xnatUri.split('?')[0])
            
            
            print ("%s creating %s "%(self.MODULE.utils.lf(), xnatUri))
            
            

                
        elif 'cancel' in button.text.lower():
            self.close()




    def setLineEditsEnabled(self, enabled = True, keys = None):
        if keys == None:
            for key, lineEdit in self.lineEdits.iteritems():
                lineEdit.setEnabled(enabled)
        else:
            for key in keys:
                self.lineEdits[key].setEnabled(enabled)
                


    def setDropdownsEnabled(self, enabled = True, keys = None):
        if keys == None:
            for key, dropdown in self.dropdowns.iteritems():
                dropdown.setEnabled(enabled)
        else:
            for key in keys:
                self.dropdowns[key].setEnabled(enabled)


        
        
            
    def onProjectLineEdited(self, text):
        """ Removes whitespaces from project line and
            enables/disables accordingly.
        """
        if len(text.strip(" ")) > 0:
            ind = self.dropdowns['projects'].findText(text.strip(), 8)
            if ind > -1:
                self.errorLines['projects'].setText("<font color=\"red\">*Project '%s' already exists.</font>"%(text))
                self.createButton.setEnabled(False)
                return
            else:
                invalidMsg = self.checkForInvalidCharacters(text)
                if invalidMsg != None:
                    self.errorLines['projects'].setText('<font color=\"red\">%s</font>'%(invalidMsg))
                    self.createButton.setEnabled(True)
                    return

        self.errorLines['projects'].setText('')
        self.createButton.setEnabled(True)

            

            
    def onSubjectLineEdited(self, text):
        """ Removes whitepsaces from experiment line
            and enables/disables accordingly.
        """
        if len(text.strip(" ")) > 0:
            ind = self.dropdowns['subjects'].findText(text.strip(), 8)
            if ind > -1:
                self.errorLines['subjects'].setText("<font color=\"red\">*Subject '%s' already exists.</font>"%(text))
                self.createButton.setEnabled(False)
                return
            else:
                invalidMsg = self.checkForInvalidCharacters(text)
                if invalidMsg != None:
                    self.errorLines['subjects'].setText('<font color=\"red\">%s</font>'%(invalidMsg))
                    self.createButton.setEnabled(True)
                    return
                    
        self.errorLines['subjects'].setText('')
        self.createButton.setEnabled(True)

                


    def checkForInvalidCharacters(self, text):
        """
           From: http://stackoverflow.com/questions/5698267/efficient-way-to-search-for-invalid-characters-in-python
        """

        invalidChars = " .;:[<>/{}[\]~`]"

        for char in invalidChars:
            if char in text:
                return "The following characters are not allowed: %s"%(invalidChars)

        if ' ' in text:
            return "Spaces are not allowed."
        else:
            return None
