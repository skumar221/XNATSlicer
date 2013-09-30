from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import csv
import datetime




comment = """
  XnatFilter is the class that handles all of the UI interactions to the XnatCommunicator.

# TODO : 
"""



class XnatFilter(object):
    """ Descriptor
    """
    
    def __init__(self, browser = None):
        """ Descriptor
        """
        self.browser = browser


    @property
    def metadataFilters(self):
        return {'accessed' : 'last_accessed_497',
                }


        
    def filterHasTag(self, _contents, _outputTag, filterTag):
        """
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
            
            
            
            
            
    def filterRecent(self, _filteredValues, _filteredTagValues):
        """
        """
        sortedLists = [list(x) for x in zip(*sorted(zip(_filteredTagValues, _filteredValues), key=lambda pair:pair[0]))]
        return sortedLists[1]

    
    
    def filter(self, contents = None, outputTag = None, filterTags = None):
        """ Descriptor
        """

        def intersect(a, b):
            """ return the intersection of two lists """
            return list(set(a) & set(b))

        outputValues = contents[outputTag]
        for filterTag in filterTags:                
            if filterTag == 'all': break
            elif filterTag == 'accessed' or filterTag == 'recent':
                filteredValues, filteredTagValues = self.filterHasTag(contents, outputTag, self.metadataFilters['accessed'])
                outputValues = intersect(outputValues, filteredValues)
                if filterTag == 'recent':
                    print 'Recent'
                    for i in range(0, len(filteredValues)):
                        print "PRESORTED", filteredValues[i], filteredTagValues[i]
                    recents = self.filterRecent(filteredValues, filteredTagValues)
                    outputValues = intersect(recents, outputValues)
                    print "\n\nSORTED", (recents, outputValues)
                    outputValues.reverse()
                    

                
        return outputValues
            #print projectNames[projContent]#[self.browser.XnatCommunicator.metadataFilters[filterTag]] 
