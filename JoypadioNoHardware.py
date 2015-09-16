import os
import time
#import RPi.GPIO as GPIO

class JoypadioEvent(object):
    pass

class Joypadio:
    'hardware I/O class for joypad voting system'

    #choose your GPIO pins here
    GPIOteamA = 16
    GPIOteamB = 20
    
    def __init__(self):
       
        self.scoreA = 0
        self.scoreB = 0
        self.callbacks = []
                   
    #Record a vote agains the given object
    def registerVote(self,channel):
        if (channel == self.GPIOteamA):
            self.scoreA = self.scoreA +1;
            self.fire(action='vote', team='a');
        elif (channel == self.GPIOteamB):
            self.scoreB = self.scoreB + 1;
            self.fire(action='vote', team='b');
        else:
            print("unknown channel input detected on GPIO pin:" + channel)
    
    def resetScores(self):
        self.scoreA = 0
        self.scoreB = 0
        
    #callback handling
    def subscribe(self, callback):
        self.callbacks.append(callback)
    def fire(self, **attrs):
        e = JoypadioEvent()
        e.source = self;
        for k, v in attrs.iteritems():
            setattr(e,k,v)
        for fn in self.callbacks:
            fn(e)

