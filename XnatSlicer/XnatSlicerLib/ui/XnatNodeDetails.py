from __main__ import vtk, ctk, qt, slicer

import os

from XnatSettings import *



comment = """
XnatNodeDetails 

TODO : 
"""



class XnatNodeDetails(object):
    """ 
    """

    def __init__(self, MODULE = None):
        """ Init function.
        """
        self.MODULE = MODULE
        self.widget = qt.QTextEdit()
        self.widget.setFont(self.MODULE.GLOBALS.LABEL_FONT)
        self.widget.setFixedHeight(65)
        #
        # NOTE: fixes a scaling error.
        #
        self.scrollBar = self.widget.verticalScrollBar()
        self.scrollBar.setStyleSheet('width: 15px')
        
        #--------------------
        # Placeholder.
        #--------------------



        
    def setText(self, detailsDict):
        """ Sets the text of the widget based on a key-value pair
            styling method.
        """
        #--------------------
        # The argument is a tuple because
        # the callback is called with multiple
        # arguments (see 'runNodeClickedCallbacks' in 
        # XnatUtils).
        #--------------------      
        detailsDict = detailsDict[0]
        detailsText = ''

        
        
        #--------------------
        # Construct the priority keys first.
        #--------------------     
        priorityTags = ['ID', 'id', 'last_accessed_497', 'label', 'name', 'Name', 'type', 'Size', 'series_description']
        modifiedDetails = {}
        for key in detailsDict:
            detailsDict[key] = detailsDict[key].strip(' ')
            if len(detailsDict[key]) > 0:
                if not key in priorityTags:
                    priorityTags.append(key)


                    
        #--------------------
        # Construct the priorty strings.
        #--------------------         
        for key in priorityTags:
            if key in detailsDict:
                detailsText += "\n<b>%s</b>:\n%s\n"%(key, detailsDict[key]) + '<br>'
        self.widget.setText(detailsText)

