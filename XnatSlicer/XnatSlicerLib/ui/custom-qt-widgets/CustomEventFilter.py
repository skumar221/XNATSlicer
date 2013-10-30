from __main__ import qt



comment = """
CustomEventFilter



See: http://qt-project.org/doc/qt-5.0/qtcore/qevent.html
for list of events.


TODO:
"""



                
class CustomEventFilter(qt.QObject):
    def __init__(self):
        """
        """
        super(CustomEventFilter, self).__init__(self)

        self.trackedEvents = [i for i in range(0, 300)]

        self.callbacks = {}
        for event in self.trackedEvents:
            self.callbacks[event] = []



            
    def addEventCallback(self, event, callback):
        """
        """

        self.callbacks[event].append(callback)


        
        
    def eventFilter(self, widget, event):
        """
        """

        try:
            for callback in self.callbacks[event.type()]:
                callback(widget)

        except Exception, e:
            #print "NO EVENT FOR: ", event.type()
            #print str(e)
            pass

            
        return False
