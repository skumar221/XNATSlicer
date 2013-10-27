from __main__ import qt

import os
import sys
import shutil



comment = """
VariableItemListWidget is a customized qtWidget.
      
"""



class VariableItemListWidget (qt.QListWidget):
    """ Descriptor above.
    """
    
    def __init__(self):
        """ Init function.
        """
        
        #--------------------
        # Call parent init.
        #--------------------
        super(VariableItemListWidget, self).__init__(self)
        #
        # QT quirk: allows widget to be dynamically updated.
        #
        self.verticalScrollBar().setStyleSheet('width: 15px')



    def addItemsByType(self, textList, itemType = None):
        """
        """


        # See http://harmattan-dev.nokia.com/docs/library/html/qt4/qt.html#ItemDataRole-enum

        
        self.addItems(textList)
        if itemType:
            for i in range(0, self.count):
                if itemType == 'checkbox':
                    z = qt.QSize(20,20)
                    self.item(i).setSizeHint(z)
                    self.item(i).setFlags(4 | 8 | 16 | 32)
                    self.item(i).setCheckState(0)
                    
                elif itemType == 'disabled':
                    self.item(i).setFlags(0)




