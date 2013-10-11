from __main__ import vtk, ctk, qt, slicer

import os
import sys
import shutil
import zipfile



comment = """
XnatDicomLoadWorkflow conducts the necessary steps to delete
a folder or a file from a given XNAT host.  The ability to delete
either depends on the user's priveleges determined both by the 
projects and the XNAT host.


TODO: Consider setting the current item to the deleted 
sibling above or below it.  If no siblings, then go to parent.
"""


    
class XnatDeleteWorkflow(object):
    """ Descriptor above.
    """
    
    def __init__(self, browser):
        """ Init function.
        """

        #--------------------
        # The browser
        #--------------------
        self.browser = browser


        
        #--------------------
        # The Dialog box.  If the user 'OK's the delete
        # it calls on 'XnatDeleteWorkflow.beginWorkflow'
        #--------------------
        self.deleteDialog = qt.QMessageBox()
        self.deleteDialog.setIcon(qt.QMessageBox.Warning)
        self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from Xnat?"%(self.browser.XnatView.viewWidget.currentItem().text(self.browser.XnatView.column_name)))   
        self.deleteDialog.connect('buttonClicked(QAbstractButton*)', self.beginWorkflow)
        self.deleteDialog.addButton(qt.QMessageBox.Ok)
        self.deleteDialog.addButton(qt.QMessageBox.Cancel)  


        
        
    def beginWorkflow(self, button = None):
        """ Main function for the class.
        """

        #--------------------
        # If there's no button argument, then exit out of function
        # by showing the deleteDialog.
        #--------------------
        if not button:
            self.deleteDialog.show()

            
        #--------------------
        # If 'ok' pressed in the deleteDialog...
        #--------------------
        elif button and button.text.lower().find('ok') > -1: 
            
            #
            # Construct the full delete string based on type of tree item deleted
            #
            delStr = self.browser.XnatView.getXnatDir(self.browser.XnatView.getParents(self.browser.XnatView.viewWidget.currentItem()))
            if (('files' in self.browser.XnatView.viewWidget.currentItem().text(self.browser.XnatView.column_category))
                or (self.browser.utils.slicerFolderName in self.browser.XnatView.viewWidget.currentItem().text(self.browser.XnatView.column_category))):
                delStr = delStr
            else:
                delStr = os.path.dirname(delStr)

                
            #
            # Call delete XnatIo's 'delete' function.
            #
            self.browser.XnatIo.delete(delStr)

            
            #
            # Set currItem to parent of deleted item and expand it. 
            #
            # TODO: Consider setting the current item to the deleted 
            # sibling above or below it.  If no siblings, then go to parent.
            #
            self.browser.XnatView.viewWidget.setCurrentItem(self.browser.XnatView.viewWidget.currentItem().parent())
            self.browser.XnatView.onTreeItemExpanded(self.browser.XnatView.viewWidget.currentItem())



        #--------------------
        # Cancel workflow if 'Cancel' button was pressed.
        #--------------------
        elif button and button.text.lower().find('cancel') > -1:
             return
