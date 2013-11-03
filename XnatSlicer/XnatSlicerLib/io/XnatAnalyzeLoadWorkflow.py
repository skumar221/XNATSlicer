import imp, os, inspect, sys, slicer

from XnatLoadWorkflow import *



comment = """
XnatAnalyzeLoadWorkflow 
TODO:
"""


class XnatAnalyzeLoadWorkflow(XnatLoadWorkflow):
    """ XnatAnalyzeLoadWorkflow conducts the necessary steps
        to load DICOM files into Slicer.
    """

                
    def load(self): 
        """ 
        """
        print "LOAD"
