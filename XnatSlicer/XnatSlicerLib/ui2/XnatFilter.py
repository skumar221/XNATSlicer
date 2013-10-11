from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import csv
import datetime



comment = """
XnatFilter is currently a placeholder class that is meant
to provide methods for filtering out XnatView items given
certain parameters.  Ideally, most of the filtering would be
conducted by the XnatView's widget (a QT widget).  This class
would be for situations where the widget does not have the
native ability to filter.

TODO: 
"""



class XnatFilter(object):
    """ Descriptor
    """
    
    def __init__(self, browser = None):
        """ Descriptor
        """
        self.browser = browser


        
    def filterHasTag(self, _contents, _outputTag, filterTag):
        """ Cycles through _contents and returns items with
            _outputTag as filtered by filterTag.
        """
        _output = _contents[_outputTag]
        _filterset = _contents[filterTag]
        filteredOutputs = []
        filterTagOutputs = []
        for i in range(0, len(_output)):
            if _filterset[i] and len(_filterset[i]) > 0:
                filteredOutputs.append(_output[i])
                filterTagOutputs.append(_filterset[i])
                
        return filteredOutputs, filterTagOutputs
            

    
    
    def filter(self, contents = None, outputTag = None, filterTags = None):
        """ Descriptor
        """

        def intersect(a, b):
            """ return the intersection of two lists """
            return list(set(a) & set(b))

        outputValues = contents[outputTag]
        for filterTag in filterTags:
            #
            # Filtering here.
            #                
            continue
                    
        return outputValues

