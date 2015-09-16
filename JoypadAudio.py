import sys
import pprint
import os
from random import randint
from pygame import mixer

class JoypadAudio:
    
    def __init__(self, joypadui):
        self.joypadui = joypadui
        self.joypadui.subscribe(self.eventHandler)
       
    # joypadui events raised go here
    def eventHandler(self, event):
        if (event.action=="countdown"):
            self.onCountdown(event)
    
    def onCountdown(self, event):
        # print str(event.time) + " seconds left"