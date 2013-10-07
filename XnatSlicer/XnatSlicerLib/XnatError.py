from __main__ import vtk, ctk, qt, slicer



comment = """
XnatError is 

TODO: 
"""



class XnatError(object):
    """ Descriptor
    """
    
    def __init__(self, host, username, errorString):
        """ Descriptor
        """

        self.host = host
        self.username = username


        
        #----------------------
        # CASE 1: Invalid username/password.
        #----------------------
        if 'Login attempt fail' in errorString:
            #self.errorMsg  = "Login to '%s' failed! Invalid username/password."%(self.host)
            self.errorMsg  = "Invalid username/password."
