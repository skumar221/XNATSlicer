from __main__ import qt

import os
import sys
import shutil




comment = """
HoverButton is a customized qtWidget.
      
"""




class HoverButton (qt.QPushButton):
    """ Descriptor above.
    """
    
    def __init__(self, parent = None):
        """ Init function.
        """

        if parent:
            super(HoverButton, self).__init__(parent)
        else:    
            super(HoverButton, self).__init__(self)


        self.installEventFilter(self)
        self.defaultStyleSheet = None
        self.hoverStyleSheet = None
        



    def setDefaultStyleSheet(self, styleSheet):
        """
        """
        self.defaultStyleSheet = styleSheet
        self.setStyleSheet(styleSheet)
        

        
    def setHoverStyleSheet(self, styleSheet):
        """
        """
        self.hoverStyleSheet = styleSheet

        

        
    def eventFilter(self, widget, event):
        """
        """
        if event.type() == qt.QEvent.Enter:
            self.onHoverEnter()

        elif event.type() == qt.QEvent.Leave:
            #elif event.type() == qt.QEvent.HoverLeave:
            self.onHoverLeave()


                

    def onHoverEnter(self):
        """
        """
        #print "\t\ton hover enter"
        self.setStyleSheet(self.hoverStyleSheet)
        

        
    def onHoverLeave(self):
        """
        """
        #print "\t\ton hover out"
        self.setStyleSheet(self.defaultStyleSheet)


        
        


