from lib import Leap
import sys 
import learn
from features import getVariance, fingerVariance
from time import time

class GestureListener(Leap.Listener): 
    """
        Selectively analyzes the frame stream to detect gestures that have
        been taught to a learn.GestureLearner (or other) classifier.
    """

    def __init__(self, callback, controller): 
        super(GestureListener, self).__init__()
        self.callback = callback 
        self.controller = controller
        
    def onInit(self, controller): 
        """
            Initialize the instance variables.
        """
        # Set up the classifier and populate it with
        # learned gestures.
        self.learner = learn.GestureLearner()
        self.learner.load_data()
        self.learner.learn()
        
        # Max window size should be set programmatically, but this works
        # for now.
        self.window = []
        self.max_window_size = 500
        
        # Running total of all the frames seen.
        self.total_frames = 0

        # The frequency, in number of frames, at which to check for gestures
        # Should probably not be hard coded
        self.freq = 60
        
        # A threshold amount of random noise that determines whether or
        # not to check the window for gestures.
        self.empty_threshold = 300
        
        # How long to lock gesture recognition for after lock().
        self.delay = 0
        self.last_update = time()


    def onFrame(self, controller):
        """
            Update self.window to reflect the new frame, then 
            either check for a gesture or do nothing. If a gesture is found,
            self.callback is called. 
        """
        if self.locked():
            self.window = []
            return
        self.total_frames += 1
        self.window.append(controller.frame())
        if len(self.window) > self.max_window_size:
            self.window.pop(0)
        
        if self.total_frames % self.freq == 0 and not self.emptyFrames(self.window):
            prediction = self.learner.predict(self.window)
            self.callback(self.controller, prediction)
            self.window = []

    # 
    def emptyFrames(self, frames):
        """
            A hack to stop the classifier from running on a window
            full of random noise.
        """
        variance = fingerVariance(frames)
        maxvar = max(variance)
        return maxvar < self.empty_threshold

    def locked(self):
        """
            Return True if the classifier should be run on the 
            current window.
        """
        return time() - self.last_update < self.delay

    def lock(self, delay=2):
        """
            Lock gesture recognition for the specified number of
            seconds.
        """
        self.last_update = time()
        self.delay = delay

