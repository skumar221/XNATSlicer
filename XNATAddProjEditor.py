from __main__ import vtk, ctk, qt, slicer
import datetime, time

import os
import sys
import shutil
import csv
import urllib2

from XNATUtils import *

#===============================================================================
# XNATAddProjEditor is used for creating new projects/folders within a given
# XNAT host.  It manages talking to a given XNATCommunicator and its associated
# string inputs. 
#===============================================================================

class XNATAddProjEditor(object):
    def __init__(self, viewer = None, browser = None, XNATCommunicator = None):
        self.browser = browser
        self.viewer = viewer
        self.XNATCommunicator = XNATCommunicator
        self.projLabel = qt.QLabel("Project")
        self.projDD = qt.QComboBox()
        self.projDD.addItems(self.XNATCommunicator.getFolderContents('/projects'))
        self.projDD.connect("currentIndexChanged(const QString&)", self.populateSubjectDD)
        self.projLE = qt.QLineEdit()
        self.projLE.connect("textEdited(const QString&)", self.projLineEdited)
        self.projError = qt.QLabel()
        self.projError.setTextFormat(1)
        self.subjLabel = qt.QLabel("Subject")
        self.subjDD = qt.QComboBox()
        self.subjLE = qt.QLineEdit()
        self.subjLE.connect("textEdited(const QString&)", self.subjLineEdited)
        self.subjError = qt.QLabel()
        self.subjError.setTextFormat(1)
        self.exptLabel = qt.QLabel("Experiment")
        self.exptLE = qt.QLineEdit()
        self.exptError = qt.QLabel()
        self.exptError.setTextFormat(1)
        p = None
        s = None
        proj = ""
        if (self.viewer.viewWidget.currentItem() != None):
            p = self.viewer.getParentItemByCategory(self.viewer.viewWidget.currentItem(), "projects")
            s = self.viewer.getParentItemByCategory(self.viewer.viewWidget.currentItem(), "subjects")
            proj = p.text(self.viewer.column_name)
            self.projDD.setCurrentIndex(self.projDD.findText(proj))
        else:
            proj = self.projDD.currentText       
        self.populateSubjectDD(proj)        
        if s:
            self.subjDD.setCurrentIndex(self.subjDD.findText(s.text(self.viewer.column_name)))

    def populateSubjectDD(self, proj):
        subjs_raw = self.XNATCommunicator.getFolderContents('/projects/' + proj + '/subjects')
        subjs_name = []
        for r in subjs_raw:
            subjs_name.append(self.XNATCommunicator.getItemValue('/projects/' + proj + '/subjects/' + str(urllib2.quote(r)), 'label'))
        self.subjDD.clear()
        self.subjDD.addItems(subjs_name)
       
    def show(self):
        l = qt.QGridLayout()
        self.addProjWindow = qt.QWidget()
        self.addProjWindow.setFixedWidth(700)
        mainWindow = slicer.util.mainWindow()
        screenMainPos = mainWindow.pos
        x = screenMainPos.x() + mainWindow.width/2 - self.addProjWindow.width/2
        y = screenMainPos.y() + mainWindow.height/2 - self.addProjWindow.height/2
        existingCol = qt.QLabel("Existing")
        newCol = qt.QLabel("New")
        l.addWidget(existingCol, 0, 1)
        l.addWidget(newCol, 0, 2)
        l.addWidget(self.projLabel, 1, 0)
        l.addWidget(self.projDD, 1, 1)
        l.addWidget(self.projLE, 1, 2)
        l.addWidget(self.projError, 2, 2)
        l.addWidget(self.subjLabel, 3, 0)
        l.addWidget(self.subjDD, 3, 1)
        l.addWidget(self.subjLE, 3, 2)
        l.addWidget(self.subjError, 4, 2)
        l.addWidget(self.exptLabel, 5, 0)
        l.addWidget(self.exptLE, 5, 2)
        l.addWidget(self.exptError, 6, 2)
        #=======================================================================
        # BUTTONS
        #=======================================================================
        createButton = qt.QPushButton()
        createButton.setText("Create")
        cancelButton = qt.QPushButton()
        cancelButton.setText("Cancel")
        buttonRow = qt.QDialogButtonBox()
        buttonRow.addButton(createButton, 0)
        buttonRow.addButton(cancelButton, 2)
        buttonRow.connect('clicked(QAbstractButton*)', self.createButtonClicked)
        l.addWidget(buttonRow, 7, 2)
        self.addProjWindow.setLayout(l)
        self.addProjWindow.move(qt.QPoint(x,y))
        self.addProjWindow.setWindowTitle("Add Folder to XNAT")
        self.addProjWindow.show()
    
    def createButtonClicked(self,button):
        #=======================================================================
        # If OK button clicked..,.
        #=======================================================================
        if 'create' in button.text.lower():
            self.exptError.setText("")
            self.subjError.setText("")
            self.projError.setText("")
            pathStr = "/projects/"
            #===================================================================
            # STEP 1: Sum up the xnat text boxes according to XNAT file organizational rules
            #===================================================================
            if len(self.projLE.text)>0:
                pathStr += self.projLE.text
                if len(self.subjLE.text)>0:
                    pathStr += "/subjects/" + self.subjLE.text
                    if len(self.exptLE.text)>0:
                        pathStr += "/experiments/" + self.exptLE.text
            else:
                pathStr += self.projDD.currentText
                if len(self.subjLE.text)>0:
                    pathStr += "/subjects/" + self.subjLE.text
                    if len(self.exptLE.text)>0:
                        pathStr += "/experiments/" + self.exptLE.text
                else:
                    pathStr += "/subjects/" + self.subjDD.currentText
                    if len(self.exptLE.text)>0:
                        pathStr += "/experiments/" + self.exptLE.text
            #===================================================================
            # STEP 2: After summing up the text to XNAT folders, see if they exist already
            #===================================================================
            if (self.XNATCommunicator.fileExists(pathStr)):
                print ("%s ALREADY EXISTS!"%(pathStr))
                projStr = pathStr.split("/subjects")[0]
                subjStr = None
                exptStr = None
                if "/subjects" in pathStr:
                    subjStr = pathStr.split("/experiments")[0]
                if "/experiments" in pathStr:
                    exptStr =  pathStr
                if (exptStr and self.XNATCommunicator.fileExists(exptStr)):
                    self.exptError.setText("<font color=\"red\">*Experiment already exists.</font>")
                elif (subjStr and self.XNATCommunicator.fileExists(subjStr)):
                    self.subjError.setText("<font color=\"red\">*Subject already exists.</font>")
                elif (projStr and self.XNATCommunicator.fileExists(projStr)):
                    self.projError.setText("<font color=\"red\">*Project already exists.</font>")
            #===================================================================
            # STEP 3: Doesn't exist? Then make the folders.
            #===================================================================
            else:
                self.XNATCommunicator.makeDir(pathStr)
                slicer.app.processEvents()
                self.viewer.selectItem_byPath(pathStr)
                print ("CREATING %s "%(pathStr))
                self.addProjWindow.close()
        elif 'cancel' in button.text.lower():
            self.addProjWindow.close()
    
    def projLineEdited(self, str):
        if (len(str.strip(" ")) > 0):
            self.projDD.setEnabled(False)
            self.subjDD.setEnabled(False)
        else:
            self.projDD.setEnabled(True)
            
    def subjLineEdited(self, str):
        if (len(str.strip(" ")) > 0):
            self.subjDD.setEnabled(False)
        else:
            self.subjDD.setEnabled(True)