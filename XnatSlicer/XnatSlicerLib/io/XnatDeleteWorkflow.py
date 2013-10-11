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
    
    def __init__(self, MODULE):
        """ Init function.
        """

        #--------------------
        # The MODULE
        #--------------------
        self.MODULE = MODULE


        
        #--------------------
        # The Dialog box.  If the user 'OK's the delete
        # it calls on 'XnatDeleteWorkflow.beginWorkflow'
        #--------------------
        self.deleteDialog = qt.QMessageBox()
        self.deleteDialog.setIcon(qt.QMessageBox.Warning)
        self.deleteDialog.setText("Are you sure you want to delete the file: '%s' from Xnat?"%(self.MODULE.XnatView.viewWidget.currentItem().text(self.MODULE.XnatView.column_name)))   
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
            delStr = self.MODULE.XnatView.getXnatDir(self.MODULE.XnatView.getParents(self.MODULE.XnatView.viewWidget.currentItem()))
            if (('files' in self.MODULE.XnatView.viewWidget.currentItem().text(self.MODULE.XnatView.column_category))
                or (self.MODULE.utils.slicerFolderName in self.MODULE.XnatView.viewWidget.currentItem().text(self.MODULE.XnatView.column_category))):
                delStr = delStr
            else:
                delStr = os.path.dirname(delStr)

                
            #
            # Call delete XnatIo's 'delete' function.
            #
            self.MODULE.XnatIo.delete(delStr)

            
            #
            # Set currItem to parent of deleted item and expand it. 
            #
            # TODO: Consider setting the current item to the deleted 
            # sibling above or below it.  If no siblings, then go to parent.
            #
            self.MODULE.XnatView.viewWidget.setCurrentItem(self.MODULE.XnatView.viewWidget.currentItem().parent())
            self.MODULE.XnatView.onTreeItemExpanded(self.MODULE.XnatView.viewWidget.currentItem())



        #--------------------
        # Cancel workflow if 'Cancel' button was pressed.
        #--------------------
        elif button and button.text.lower().find('cancel') > -1:
             return
