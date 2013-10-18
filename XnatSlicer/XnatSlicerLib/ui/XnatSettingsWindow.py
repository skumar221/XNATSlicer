from __main__ import vtk, qt, ctk, slicer

import os
import glob
import sys



comment = """
XnatSettingsWindow is the window for user-inputted XNAT settings, 
such as the Host Manager, Tree View Settings, etc.

TODO:
"""



class XnatSettingsWindow:
    """ Popup window for managing user-inputted XnatSettings, 
        such as host names and default users.
    """
    
    def __init__(self, MODULE):  
        """ Descriptor
        """      
        self.MODULE = MODULE
        self.settingsDict = {}


        #--------------------
        # Make window.
        #--------------------
        self.window = qt.QWidget()
        self.window.setFixedWidth(700)
        self.window.setFixedHeight(600)
        self.window.setWindowModality(2)
        self.window.hide()

        

        #--------------------
        # Make master layout.
        #--------------------
        self.masterLayout = qt.QGridLayout()
        self.window.setLayout(self.masterLayout)
        

        
        #--------------------
        # Make SettingsLister
        #--------------------
        self.settingsLister = SettingsLister(self.MODULE, self.showSettingWidget)
        self.masterLayout.addWidget(self.settingsLister, 0, 0)


        
        #--------------------
        # Make settings area layout (where the settings widgets reside).
        #--------------------
        self.settingsAreaLayout = qt.QStackedLayout()
        self.masterLayout.addLayout(self.settingsAreaLayout, 0, 1)


        
        #--------------------
        # Add buttons.
        #--------------------
        self.doneButton = qt.QPushButton("Done")
        self.doneButton.connect('clicked()', self.doneClicked)
        self.masterLayout.addWidget(self.doneButton, 1, 1)



        
        
    def showWindow(self, settingName = None, position = True):
        """ Creates a new window, adjusts aesthetics, then shows.
        """ 

        currSetting = None

        
        #--------------------
        # Loop through settingsLister to find 
        # the setting.
        #--------------------
        settingNames =  self.settingsLister.getSettingsAsList()
        for name in settingNames:
            if settingName.lower() in name.lower():
                currSetting = name



        #--------------------
        # Select the setting in the
        # 'settingsLister' text.
        #--------------------
        self.settingsLister.selectSetting(currSetting)


        
        #--------------------
        # Show the window.
        #--------------------
        self.window.show()

        

        #--------------------
        # Reposition window if argument is true.
        #--------------------
        if position:
            self.window.show()
            mainWindow = slicer.util.mainWindow()
            screenMainPos = mainWindow.pos
            x = screenMainPos.x() + mainWindow.width/2 - self.window.width/2
            y = screenMainPos.y() + mainWindow.height/2 - self.window.height/2
            self.window.move(qt.QPoint(x,y))
        
        self.window.raise_()
        



    def showSettingWidget(self, settingName):
        """ Changes the settingsAreaLayout index (a QStackedLayout)
            to the relevant settings widget based on the 'settingsName'
            argument.
        """
        self.settingsAreaLayout.setCurrentIndex(self.settingsDict[settingName])
        

            

        
    def doneClicked(self):
        """ Hide window if done was clicked.
        """
        self.MODULE.XnatLoginMenu.loadDefaultHost()
        self.window.hide()




    def addSetting(self, settingsName, widget = None):
        """ Inserts a setting into the settings window.
        """
        self.settingsLister.addSetting(settingsName)
        self.settingsAreaLayout.addWidget(widget)
        self.settingsDict[settingsName] = self.settingsAreaLayout.count() - 1



        
        
        
class SettingsLister(qt.QTextEdit):
    """ Inherits qt.QTextEdit to list the settings categories in the 
        SettingsWindow
    """


    
    def __init__(self, parent = None, selectCallback = None): 
        """ Init function.
        """
        qt.QTextEdit.__init__(self, parent)
        
        self.currText = None        
        self.setReadOnly(True)
        self.setFixedWidth(130)
        self.setLineWrapMode(False)
        self.setHorizontalScrollBarPolicy(1)
        self.selectCallback = selectCallback





    def onTextSelected(self):
        """ Runs the appropriate callbacks
            when text is selected.
            
        """
        cursor = self.textCursor()


        
        #--------------------
        # Set currText
        #--------------------
        if cursor.selectedText():
            self.currText = cursor.selectedText()



        #--------------------
        # Apply callbacks.
        #--------------------
        if self.selectCallback:
            self.selectCallback(self.currText)
            


        
    def mouseReleaseEvent(self, event):
        """ After the user clicks on a given line.
        """
        
        #--------------------
        # Define a cursor and select the line
        # that the cursor clicked on.
        #--------------------
        cursor = qt.QTextCursor(self.textCursor())
        cursor.select(qt.QTextCursor.LineUnderCursor)


        
        #--------------------
        # Select the text.
        #--------------------
        self.setTextCursor(cursor)



        #--------------------
        # Run event method.
        #--------------------
        self.onTextSelected()



            
    def selectSetting(self, settingName):
        """ Highlights a settingsName within the 
            text of the object.
        """
        
        #--------------------
        # Get the text of the widget
        # then find the index of the 'settingName'
        #--------------------
        text = self.toPlainText()
        settingNameIndex = text.find(settingName)



        #--------------------
        # Make a cursor, then manually highlight
        # the text based on the index name and text length.
        #--------------------
        cursor = qt.QTextCursor(self.textCursor())
        cursor.setPosition(settingNameIndex, 0);
        cursor.setPosition(settingNameIndex + len(settingName), 1)
        self.setTextCursor(cursor)

        

        #--------------------
        # Run event method.
        #--------------------
        self.onTextSelected()


            

        

        

    def getSettingsAsList(self):
        """ Returns a list of the settings as strings.
            Needs to break apart the linebreaks and clean
            the list before returning.
        """
        textList = self.toPlainText().split('\n')

        returnList = []
        for text in textList:
            if len(text) > 0:
                returnList.append(text)

        return returnList

    
        

    def addSetting(self, settingsName):
        """ Applies aesthetic scheme will adding name and Url.
        """
        #
        # Need to create a newline every time
        # we insert a settingsName into the settingsLister.
        #
        if len(self.toPlainText()) > 0:
            settingsName = '\n\n' + settingsName

            
        self.insertPlainText(settingsName) 


        
        
    def selectedText(self):
        """ Returns selected text.
        """ 
        return self.currText


