from __main__ import qt

import os
import glob
import sys



comment = """


TODO:
"""




class FingerTabWidget(qt.QWidget):
    """
    """
    
    def __init__(self, parent=None, *args, **kwargs):

        super(FingerTabWidget, self).__init__(self)


        self.mainInnerLayout = qt.QStackedLayout()
        self.mainInnerLayout.setStackingMode(1)
        
        self.mainInnerLayout.setSpacing(0)

        
        self.marginVal = 5
        self.currentIndex = 0


        
        #--------------------
        # Tab column
        #--------------------  
        self.tabColumn = qt.QFrame()
        self.tabWidth = 120
        self.tabColumn.setFixedWidth(self.tabWidth)
        self.tabColumn.setObjectName('tabColumn')
        self.tabColumn.setStyleSheet('#tabColumn {background:#E8E8E8 ; height: 4000px; border-right-width: 1px;  border-right-color: gray; border-right-style: solid; margin-top: 5px; margin-left: 5px; margin-bottom: 5px}')

        
        self._tabLayout = qt.QVBoxLayout()
        self._tabLayout.setContentsMargins(0,0,0,0)
        self._tabLayout.setSpacing(0)
        self._tabLayout.addStretch()

        self.tabColumn.setLayout(self._tabLayout)
        #
        # Add to main layout
        #
        self.mainInnerLayout.addWidget(self.tabColumn)

        


        #--------------------
        # Stacked widgets
        #--------------------  

        self.widgetStack = qt.QWidget()
        
        self._widgetLayout = qt.QStackedLayout()
        
        
        self.widgetStack.setObjectName("widgetStack")
        self.widgetStack.setStyleSheet("#widgetStack{ border: none; background: transparent}")

        self.widgetHBox = qt.QHBoxLayout()
        self.widgetHBox.setContentsMargins(0,self.marginVal,self.marginVal,self.marginVal)
        self.widgetHBox.addSpacing(self.tabWidth -1)
        self.widgetHBox.addLayout(self._widgetLayout)


        self.widgetStack.setLayout(self.widgetHBox)
        #
        # Add to main layout
        #
        self.mainInnerLayout.addWidget(self.widgetStack)


        
        

        self.buttonGroup = qt.QButtonGroup()
        self.buttonGroup.connect('buttonClicked(QAbstractButton*)', self.tabClicked)
        
        self.tabButtons = []
        self.tabWidgets = []


        self.tabObjectName = 'fingerTab'
        self.tabToggledStyle =  '#fingerTab {border: 1px solid gray;    border-right-width: 1px;  border-right-color: white; background-color: white;}'
        self.tabUntoggledStyle ='#fingerTab {border: 1px solid #D0D0D0; border-right-width: 1px;  border-right-color: gray;  background-color: #C0C0C0;}'


        #self.setObjectName("testAm")
        #self.setStyleSheet("#testAm {color: lightgray; background: lightgray}")

        self.tabToggledFont = qt.QFont('Arial', 12, 100, False)
        self.tabUntoggledFont = qt.QFont('Arial', 12, 25, False)


        print '\n\n\n**************%s\n'%(self.mainInnerLayout.count())

        self.mainInnerLayout.setCurrentIndex(1)

        self.mainLayout = qt.QVBoxLayout()
        self.mainLayout.setContentsMargins(5,5,5,5)
        self.mainLayout.addLayout(self.mainInnerLayout)


        
        self.setLayout(self.mainLayout)
        self.mainInnerLayout.setContentsMargins(0,0,0,0)
        #self.mainInnerLayout.setContentsMargins(self.marginVal,self.marginVal,self.marginVal,self.marginVal)


        
    def tabClicked(self, tab):
        """
        """


        if tab.checked:
            tab.setStyleSheet(self.tabToggledStyle)
            tab.setFont(self.tabToggledFont)
        else:
            tab.setStyleSheet(self.tabUntoggledStyle)

        for tabWidget in self.tabButtons:
            if tabWidget != tab:
                tabWidget.setChecked(False)
                tabWidget.setStyleSheet(self.tabUntoggledStyle)
                tabWidget.setFont(self.tabUntoggledFont)


        ind = -1
        for i in range(0, len(self.tabButtons)):
            if self.tabButtons[i] == tab:
                ind = i
                break

        self.currentIndex = ind
        self._widgetLayout.setCurrentIndex(ind)
        



    def setTabFont(self, font):
        """
        """
        for tab in self.tabButtons:
            tab.setFont(font)


    def setCurrentIndex(self, index):
        """ 
        """
        print "\n\nSET CURRENT INDEX %s\n\n"%(index)
        self.currentIndex = index
        self.tabButtons[index].setChecked(True)
        self.tabClicked(self.tabButtons[index])
        #self._widgetLayout.setCurrentIndex(index)

        
        
                
    def makeTabButton(self, tabName):
        """
        """
        a = qt.QPushButton(tabName)
        a.setFixedWidth(self.tabWidth - self.marginVal)
        a.setFixedHeight(25)
        a.setObjectName(self.tabObjectName)
        a.setStyleSheet(self.tabUntoggledStyle)
        a.setCheckable(True)

        return a



    

    def addTab(self, widget, tabName):
        """
        """

        

        tabButton = self.makeTabButton(tabName)
        self._tabLayout.insertWidget(len(self.tabButtons), tabButton)

        self._widgetLayout.addWidget(widget)
        
        self.tabButtons.append(tabButton)
        self.tabWidgets.append(widget)
        
        
        self.buttonGroup.addButton(tabButton)

        
        
        self._tabLayout.setSpacing(0)

        self._widgetLayout.addWidget(widget)
        self.setLayout(None)
        self.setLayout(self.mainInnerLayout)
        self.mainInnerLayout.setCurrentIndex(0)
