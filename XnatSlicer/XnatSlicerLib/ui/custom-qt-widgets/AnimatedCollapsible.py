from __main__ import qt, ctk

import os
import sys
import shutil


from HoverButton import *




comment = """
AnimatedCollapsible is a collapsible widget that animates
itself when the user toggles it.  Much like other QT widgets, 
the user can set a layout where the contents reside to allow
for the animation.  It should be noted that the user should 
provide the further...

TODO:        
"""




class AnimatedCollapsible(ctk.ctkExpandableWidget):
    """ Descriptor above.
    """
    
    def __init__(self, parent, title, maxHeight = 1000, minHeight = 60):
        """ Init function.
        """

        if parent:
            super(AnimatedCollapsible, self).__init__(parent)
        else:
            super(AnimatedCollapsible, self).__init__(self)



        self.sizeGrip = self.children()[0]
        self.sizeGrip.hide()

        
        #--------------------
        # We hide the module first because
        # it creates a flikering on loadup
        #--------------------
        self.hide()


        
        #--------------------
        # Set internal variables.
        #--------------------        
        self.rightArrowChar = u'\u25b8'
        self.downArrowChar = u'\u25be'
        #
        # Size
        #
        self.collapsedHeight = 30
        self.minHeight = minHeight
        self.maxHeight = maxHeight

        
        self.toggleHeight = 16
        self.toggleWidth = 80

        self.setStyleSheet('width: 100%')
        #
        # Animation duration
        #
        self.animDuration = 300


        self.setSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.MinimumExpanding)


        
        #----------------
        # Set the easing curve.  See:
        # http://harmattan-dev.nokia.com/docs/library/html/qt4/qeasingcurve.html
        # for more options.
        #----------------
        self.easingCurve = qt.QEasingCurve(2);


        
        #----------------
        # Set the minimum hieght
        #----------------
        self.setMinimumHeight(self.minHeight)
        

        
        #----------------
        # set  the Title
        #----------------       
        self.title = title


        
        #----------------
        # Make button
        #----------------
        self.button = HoverButton(self)
        self.button.hide()
        self.button.setParent(self)
        self.button.setFixedHeight(self.toggleHeight)
        self.button.setCheckable(True)
        self.button.setObjectName('acButton')
        self.button.setDefaultStyleSheet('#acButton {border: 1px solid transparent; background-color: white; margin-left: 5px; text-align: left; padding-left: 5px;}')
        self.button.setHoverStyleSheet('#acButton {border: 1px solid rgb(200,200,200); background-color: white; border-radius: 2px; margin-left: 5px; text-align: left; padding-left: 5px;}')
        #self.button.setStyleSheet('#acButton:pressed {background-color: gray;}')
        self.setButtonText(True)
     

        
        #----------------
        # Make the internal 'frame' and set the style
        # accordingly.
        #----------------
        self.frame = qt.QFrame(self)
        #
        # To prevent style sheet inheritance
        #
        self.frame.setObjectName('animFrame')
        self.frame.setStyleSheet('#animFrame {margin-top: 9px; border: 2px solid lightgray; padding-top: 5px; padding-left: 2px; padding-right: 2px; padding-bottom: 2px}')

        
        
        
        #----------------
        # Stack the button on top of the frame via a 
        # QStackedLayout
        #----------------
        self.stackedLayout = qt.QStackedLayout()

        self.stackedLayout.addWidget(self.button)
        self.stackedLayout.addWidget(self.frame)
        
        
        #self.stackedLayout.addWidget(self.button)
        #self.stackedLayout.addWidget(self.settingsButton)
        
        #
        # To make sure the button is on top.
        #
        self.stackedLayout.setCurrentIndex(0)
        self.stackedLayout.setStackingMode(1)



        #----------------
        # Set the sayout
        #----------------        
        self.setLayout(self.stackedLayout)


        
        #----------------
        # Init the animation group and callbacks.
        #----------------  
        self.animations = qt.QParallelAnimationGroup()
        self.onAnimate = None
        self.onCollapse = None
        self.onExpand = None
        self.ContentsWidgets = []


        
        #----------------
        # Set the default states after creation.
        #----------------
        #self.button.setChecked(True)
        self.button.connect('toggled(bool)', self.setChecked)
        self.toggled = True



        self.stretchHeight = None






            
        

    def suspendAnimationDuration(self, suspend):
        """ As stated.
        """
        if suspend:
            self.originalAnimDuration = self.animDuration
            self.animDuration = 0    
        else:
            self.animDuration = self.originalAnimDuration


            
        
    def setAnimationDuration(self, duration):
        """ As stated.
        """
        self.animDuration = duration;


        
        
    def setFrameLayout(self, layout):
        """ Adds a layout to the internal frame
            which will be the contents of the widget.
        """
        self.frame.setLayout(layout)


        
        #----------------
        # Temporarily turn off the animation
        # when adding contents.
        #----------------
        self.setChecked(True)
        



    def setButtonText(self, toggled):
        """ Modifies the arrow character of the button
            title to match the 'toggled' state and also
            sets the following text.
        """
        arrowChr = self.downArrowChar if toggled else self.rightArrowChar
        self.button.setText(arrowChr + '  ' + self.title)
        self.button.setFixedHeight(17)
        self.button.setMinimumWidth(10)
        self.button.setMaximumWidth(110)
        #----------------
        # Temporarily turn off the animation
        # when adding contents.
        #----------------  
        #self.button.setFixedWidth(self.button.sizeHint.width())      
        #self.button.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Minimum) 
  

        

    def setWidget(self, widget):
        """
        """
        self.ContentsWidgets = [widget]
        layout = qt.QHBoxLayout()
        layout.addWidget(widget)
        layout.setContentsMargins(0,0,0,0)
        self.frame.setLayout(layout)

        
            
        
    def setOnCollapse(self, callback):
        """ As stated.
        """
        self.onCollapse = callback



        
    def setOnExpand(self, callback):
        """ As stated.
        """
        self.onExpand = callback



        
    def setOnAnimate(self, callback):
        """ As stated.
        """
        self.onAnimate = callback



        
    def addContentsWidgets(self, *args):
        """ Adds contents widgets for tracking, so that
            they can disappear when the collapsible closes.  If any of the 
            arguments are not an array, convert them then add them to 
            self.ContentsWidgets.
        """

        #--------------------
        # Loop through all of the arguments
        #--------------------
        for arg in args:

            
            #
            # Check if the argument is an list, if it isn't
            # then make it one.
            #
            if not isinstance(arg, list):
                arg = [arg]

                
            #
            # Append to self.ContentsWidgets.
            #
            self.ContentsWidgets = self.ContentsWidgets + arg

            


    def removeContentsWidgets(self, *args):
        """ 
        """


        newContentsWidgets = []

        removeWidgets = []

        
        #--------------------
        # Collect all the widgets to be removed
        #--------------------
        for arg in args:

            
            #
            # Check if the argument is an list, if it isn't
            # then make it one.
            #
            if not isinstance(arg, list):
                arg = [arg]

                
            #
            # Append to self.ContentsWidgets.
            #

            removeWidgets = removeWidgets + arg


        
        
        self.ContentsWidgets = list(set(self.ContentsWidgets) - set(removeWidgets))


        
                


    def setSizeGripVisible(self, visible):
        """
        """
        if not visible:
            self.sizeGrip.hide()
        else:
            self.sizeGrip.show()


            

    def hideContentsWidgets(self):
        """ As stated.
        """
        if self.ContentsWidgets:
            for contentsWidget in self.ContentsWidgets:
                contentsWidget.hide()



            
    def showContentsWidgets(self):
        """ As stated.
        """
        if self.ContentsWidgets:
            for contentsWidget in self.ContentsWidgets:
                contentsWidget.show()
        


            
    def onAnimateMain(self, variant):
        """ Function during main animation
            sequence -- runs the 'onAnimate'
            callback.
        """
        if self.onAnimate:
            self.onAnimate()
            self.setFixedHeight(variant.height())
            #size = qt.QSize(variant.width(), variant.height())
            #self.setBaseSize(size)
            #geom = self.geometry
            #self.setGeometry(geom.top(), geom.left(), geom.width(), variant.height())


        
    def onAnimationFinished(self):
        """ Callback function when the animation
            finishes.
        """


        #---------------- 
        # Call the animate function.
        #---------------- 
        self.onAnimateMain(qt.QSize(self.geometry.width(), self.geometry.height()))

        #print "onAnimationFinished", self.toggled
        
        #---------------- 
        # If the widget is toggled...
        #---------------- 
        if self.toggled:

            
            #
            # Set the height
            #
            

            if self.stretchHeight:
                self.setMaximumHeight(self.stretchHeight)
            else:
                self.setMaximumHeight(self.maxHeight)
                
            self.setMinimumHeight(self.minHeight)

            #if self.targetGeometry:
            #    self.setGeometry(self.targetGeometry)
                
            #
            # Show contents
            #
            self.showContentsWidgets()
            #
            # Run callbacks, animate and end.
            #
            if self.onExpand:
                self.onExpand()

                

        #---------------- 
        # Otherwise...
        #---------------- 
        else:
            #print "ON COLLAPSE:", self.onCollapse                
            #
            # Set the height
            #
            self.setFixedHeight(self.collapsedHeight)
            #
            # Run callbacks
            #
            if self.onCollapse:
                self.onCollapse()

    


    def setMaxHeight(self, height):
        """
        """
        self.maxHeight = height
        #self.setMaximumHeight(self.maxHeight)
        #self.setMinimumHeight(self.minHeight)


        

    def setMinHeight(self, height):
        """
        """
        self.minHeight = height
        #self.setMaximumHeight(self.maxHeight)
        #self.setMinimumHeight(self.minHeight)


        

    def setStretchHeight(self, height):
        """
        """
        self.stretchHeight = height
        self.setMaximumHeight(height)
        

        
        
    def setChecked(self, toggled, animDuration = None):
        """ Constructs an executes an animation for the widget
            once the title button is toggled.
        """

        #---------------- 
        # We need to set the button state in case
        # this method is programatically called.
        #----------------         
        self.button.setChecked(toggled)


        
        #---------------- 
        # Track whether collapsible was toggled.
        #---------------- 
        self.toggled = toggled


        
        #---------------- 
        # Define the animation duration.
        #----------------        
        if not animDuration: 
            animDuration = self.animDuration


            
        #---------------- 
        # Clear animation
        #---------------- 
        self.animations.clear()



        #---------------- 
        # For safety...
        #----------------   
        self.setStyleSheet('width: 100%')


        
        #---------------- 
        # Modify button text to match the toggled
        # state (down arrow) 
        #----------------       
        self.setButtonText(toggled)	


            
        #---------------- 
        # Construct top-level animation.
        #----------------	
        
        #
        # Make the animation object
        #
        anim = qt.QPropertyAnimation(self, 'size')
        
        #
        # Set the duration
        #
        anim.setDuration(animDuration)	

        #
        # Set the easing curve
        #
        anim.setEasingCurve(self.easingCurve)

        #
        # Set the start/end values depending on
        # the toggle state.
        #
        if self.toggled:
            

            #
            # Establish the animation sizes
            #	
            startSize = qt.QSize(self.geometry.width(), self.collapsedHeight)
            endSize = qt.QSize(self.geometry.width(), self.maxHeight)  

            self.setMaximumHeight(self.collapsedHeight)
            self.setMinimumHeight(self.collapsedHeight)


        else:

            startHeight = self.geometry.height()
            startSize = qt.QSize(self.geometry.width(), startHeight)
            endSize = qt.QSize(self.geometry.width(), self.collapsedHeight)  
            
            self.setMaximumHeight(startHeight)
            self.setMinimumHeight(startHeight)

   
            self.hideContentsWidgets()
            
            
        anim.setStartValue(startSize)
        anim.setEndValue(endSize)            
       
        #---------------- 
        # Set callback during animation.
        #----------------
        anim.valueChanged.connect(self.onAnimateMain)



        #---------------- 
        # Connect the 'finished()' signal of the animation
        # to the finished callback...
        #----------------
        anim.connect('finished()', self.onAnimationFinished)


        
        #---------------- 
        # Add main animation to queue and  
        # start animation.
        #----------------       
        self.animations.addAnimation(anim)
        self.animations.start()


        
        

