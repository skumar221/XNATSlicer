import os
from __main__ import vtk, ctk, qt, slicer




comment = """
XnatGlobals contains static properites relevant o 
interacting with XNAT.

TODO : 
"""



class XnatGlobals(object):
    
    def __init__(self, parent=None):   
        pass

    
    
    @property
    def LIB_URI(self):
        return os.path.dirname(os.path.dirname(os.path.abspath( __file__ )))



    
    @property
    def ROOT_URI(self):
        return os.path.dirname(self.LIB_URI)

    

    
    @property
    def CACHE_URI(self):
        return os.path.join(self.ROOT_URI, 'Cache')



    
    @property
    def RESOURCES_URI(self):
        return os.path.join(self.ROOT_URI, 'Resources')


    
    
    @property
    def LOCAL_URIS(self):
        return {
            "home" : self.ROOT_URI,
            "settings": os.path.join(self.ROOT_URI, "Settings"),
            "projects" : os.path.join(self.CACHE_URI, "projects"),
            "downloads" : os.path.join(self.CACHE_URI, "downloads"),
            "uploads" : os.path.join(self.CACHE_URI, "uploads"), 
            "icons" : os.path.join(self.RESOURCES_URI, "Icons"),                       
        }



    
    @property
    def DICOM_EXTENSIONS(self):
        return [".dcm", ".ima", ".dicom"]


    

    @property
    def ALL_LOADABLE_EXTENSIONS(self):
        return self.DICOM_EXTENSIONS + [".nii", 
                                       ".nrrd", 
                                       ".img", 
                                       ".ima",
                                       ".IMA",
                                       ".nhdr", 
                                       ".dc", 
                                       ".raw.gz", 
                                       ".gz", 
                                       ".vtk"]


    @property
    def DECOMPRESSIBLE_EXTENSIONS(self):
        return  [".gz", ".zip", ".tar"]


    
    @property
    def MRML_EXTENSIONS(self):
        return [".mrml"]




    @property
    def BUTTON_SIZE_MED(self):
        return qt.QSize(45, 45)



    
    @property
    def BUTTON_SIZE_SMALL(self):
        return qt.QSize(28, 28)


    @property
    def LABEL_FONT(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE, 10, False)


    
    @property
    def LABEL_FONT_LARGE(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE + 2, 10, False)


    
    @property
    def LABEL_FONT_BOLD(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE, 100, False)


    
    
    @property
    def LABEL_FONT_ITALIC(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE, 10, True)


    
    @property
    def LABEL_FONT_ITALIC_LARGE(self):
        return qt.QFont(self.FONT_NAME, self.FONT_SIZE + 2, 10, True)

    

    @property
    def FONT_NAME(self):
        return "Arial"

    
    
    @property
    def FONT_SIZE(self):
        return 10
