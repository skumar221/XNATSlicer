from __main__ import vtk, ctk, qt, slicer

import os

from XnatSettings import *



comment = """
XnatNodeDetails inherits QTextEdit and is the display widget
for the details of a selected 'node' within an XnatView.  By 'details'
we mean, it displays all of the relevant metadata pertaining to a given 
XNAT node, whether it's a folder (project, subject, experiment, scan)
or a file.

TODO : 
"""



class XnatNodeDetails(qt.QTextEdit):
    """ Descriptor above.
    """

    def __init__(self, MODULE = None):
        """ Init function.
        """

        #--------------------
        # Call parent init.
        #--------------------
        qt.QFrame.__init__(self)
        self.MODULE = MODULE
        self.setFont(self.MODULE.GLOBALS.LABEL_FONT)


        
        #--------------------
        # NOTE: fixes a scaling error that occurs with the scroll 
        # bar.  Have yet to pinpoint why this happens.
        #--------------------
        self.verticalScrollBar().setStyleSheet('width: 15px')



        
    def setTextValue(self, detailsDict):
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



        #--------------------
        # Call parent 'setText'
        #-------------------- 
        self.setText(detailsText)

