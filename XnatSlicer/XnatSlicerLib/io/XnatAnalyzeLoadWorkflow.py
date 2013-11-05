from XnatLoadWorkflow import *



comment = """
XnatAnalyzeLoadWorkflow contains the specific load method for single-file
(non-Slicer scene) downloads from an XNAT host into Slicer.

TODO:
"""



class XnatAnalyzeLoadWorkflow(XnatLoadWorkflow):
        



    def initLoad(self, args):
        """ As stated.
        """
        self.load(args)

        
        
    def load(self, args):
        """ Downloads a file from an XNAT host, then attempts to load it
            via the Slicer API's 'loadNodeFromFile' method, which returns
            True or False if the load was successful.
        """

        #--------------------    
        # Call parent 'load' method.
        #-------------------- 
        super(XnatAnalyzeLoadWorkflow, self).load(args)


        
        #-------------------- 
        # Get the file from XNAT host.
        #-------------------- 

        #print "ANALYZE", self.xnatSrc, self.localDst

        downloadFiles = {'hdr': {'src': None, 'dst': None} , 'img': {'src': None, 'dst': None}}


        for key in downloadFiles:
            if self.xnatSrc.lower().endswith(key):
                downloadFiles[key]['src'] = self.xnatSrc
                downloadFiles[key]['dst'] = self.localDst
            else:
                if key == 'img':
                    replacer = 'hdr'
                else:
                    replacer = 'img'
                downloadFiles[key]['src'] = self.xnatSrc.replace(replacer, key)
                downloadFiles[key]['dst'] = self.localDst.replace(replacer, key)                

 

        for key in downloadFiles:
            self.MODULE.XnatIo.getFile({downloadFiles[key]['src']: downloadFiles[key]['dst']})



        #-------------------- 
        # Attempt to open file
        #-------------------- 
        a = slicer.app.coreIOManager()

        #
        # Prioritize loading of header file first.
        #
        if downloadFiles['hdr']['dst'] != None:
            t = a.fileType(downloadFiles['hdr']['dst'])
            fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(downloadFiles['hdr']['dst'], t)

        #
        # If there's no header file, the open the .img.
        #
        else:
            t = a.fileType(downloadFiles['img']['dst'])
            fileSuccessfullyLoaded = slicer.util.loadNodeFromFile(downloadFiles['img']['dst'], t)

            

        #-------------------- 
        # If the load was successful, update the
        # session args...
        #-------------------- 
        if fileSuccessfullyLoaded: 
            sessionArgs = XnatSessionArgs(MODULE = self.MODULE, srcPath = self.xnatSrc)
            sessionArgs['sessionType'] = "scene download"
            self.MODULE.XnatView.startNewSession(sessionArgs)
            print ("'%s' successfully loaded."%(os.path.basename(self.localDst))) 



        #-------------------- 
        # Otherwise kick back error.
        #-------------------- 
        else: 
            errStr = "Could not load '%s'!"%(os.path.basename(self.localDst))
            print (errStr)
            qt.QMessageBox.warning( None, "Load Failed", errStr) 


            
        #-------------------- 
        # Return the load success
        #-------------------- 
        return fileSuccessfullyLoaded
