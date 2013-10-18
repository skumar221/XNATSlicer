from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil



comment = """
XnatSearchBar constructs the UI components for the search
bar. It should be noted that the XnatSearchBar class does
not contain the methods for conducting a search on an XNAT 
host, rather it allows the user to connect the 'returnPressed'
signal of the searchLine to a search method of their choice.

TODO:        
"""



class XnatSearchBar(object):
    """ Descriptor above.
    """
    
    def __init__(self, MODULE):
        """ Init function.
        """

        self.MODULE = MODULE
        self.prevText = None
        self.defaultSearchText = 'Search projects, subjects and experiments...'


        
        #--------------------------------
        # The search box (qt.QLineEdit)
        #--------------------------------
        self.searchLine = qt.QLineEdit()
 

        
        #--------------------------------
        # The search button
        #--------------------------------
        self.button = qt.QPushButton('')
        self.button.setIcon(qt.QIcon(os.path.join(self.MODULE.GLOBALS.LOCAL_URIS['icons'], 'x.png')) )
        size = qt.QSize(26,26)
        self.button.setFixedSize(size)
        self.button.connect('clicked()', self.onClearButtonClicked)
      

        
        #--------------------------------
        # Search Layout
        #--------------------------------
        self.searchLayout = qt.QHBoxLayout()        
        self.searchLayout.addWidget(self.searchLine)
        self.searchLayout.addWidget(self.button)



        #--------------------------------
        # The Search Widget
        #--------------------------------       
        self.searchWidget = qt.QFrame()
        self.searchWidget.setLayout(self.searchLayout)


        
        #--------------------------------
        # AESTHETICS
        #--------------------------------  
        #
        # Widget aesthetics
        #
        self.searchWidget.setStyleSheet('border: 1px solid rgb(160,160,160); border-radius: 3px;')
        self.searchWidget.setFixedHeight(22)
        #
        # Search box aesthetics
        #
        self.searchLine.setStyleSheet("border: none")
        #
        # Button aesthetics
        #
        self.button.setStyleSheet("border: none")
        self.button.setFixedHeight(20)
        #
        # Layout aesthetics
        #
        self.searchLayout.setContentsMargins(0,0,0,0)

        

        #--------------------------------
        # Apply the default text and style
        #--------------------------------
        self.onClearButtonClicked()
        self.applyTextStyle('empty')

        

    def applyTextStyle(self, mode):
        """ Applies a stylistic change to text depending on the
            'mode' argument specified.  Empty searchLines are 
            italicized.
        """
        if mode == 'empty':
            self.searchLine.setFont(self.MODULE.GLOBALS.LABEL_FONT_ITALIC) 
            palette = qt.QPalette();
            color = qt.QColor(150,150,150)
            palette.setColor(6, color);
            self.searchLine.setPalette(palette);
        
        elif mode == 'not empty':
            self.searchLine.setFont(self.MODULE.GLOBALS.LABEL_FONT) 
            palette = qt.QPalette();
            color = qt.QColor(0,0,0)
            palette.setColor(6, color);
            self.searchLine.setPalette(palette);


            
        
    def onSearchBoxCursorPositionChanged(self, oldPos, newPos):
        """ Signal method for when the user interacts with the 
            searchLine.  We reapply the default text if the user
            clears the search line or deletes all the way to the 
            0 cursor position.
        """

        #--------------------------------
        # When the user clears the searchLine (there's no text), apply
        # the same functionality as the clear button.
        #--------------------------------
        if len(self.searchLine.text) == 0 and newPos == 0 and self.prevText != None:
            self.onClearButtonClicked()
            return


        
        #--------------------------------
        # Clear the default string in the searchLine
        # once the user clicks on the line
        #--------------------------------
        if self.defaultSearchText in str(self.searchLine.text) and self.prevText == None: 
            self.applyTextStyle('not empty')
            self.searchLine.setText('')


            
        #--------------------------------
        # Store the previous text.
        #--------------------------------
        self.prevText = self.searchLine.text
            

            

    def onClearButtonClicked(self):
        """ Callback function for when the clear button is clicked.
            Applies the default text in the searchLine and awaits the
            user to click ont the searchLine so it can clear it by linking
            the 'cursorPositionChanged' signal to 'onSearchBoxCursorPositionChanged'
            function.
        """
        self.searchLine.disconnect('cursorPositionChanged(int, int)', self.onSearchBoxCursorPositionChanged)
        self.applyTextStyle('empty')
        self.searchLine.setText(self.defaultSearchText)
        self.prevText = None
        self.searchLine.setCursorPosition(1000)
        self.searchLine.connect('cursorPositionChanged(int, int)', self.onSearchBoxCursorPositionChanged)


        

    def getText(self):
        """ As stated.  Generic method for classes that access
            the XnatSearchBar without going into the depth of 
            the widget
        """
        return self.searchLine.text.strip()



    
    def getButton(self):
        """ Returns the button of the XnatSearchBar, which
            is the 'clear' button.
        """
        return self.button


    

    def getSearchLine(self):
        """ As stated.
        """
        return self.searchLine


    

    def connect(self, function):
        """ For external classes to link the 'returnPressed' signal
            to a given function.  In this case, it's a search method
            provided by the XnatView class (and subclasses) and
            the XnatIo class.
        """
        self.searchLine.connect("returnPressed()", function)
    
