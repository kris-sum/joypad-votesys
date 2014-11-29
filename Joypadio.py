import os
import time
import RPi.GPIO as GPIO


class Joypadio:
    'hardware I/O class for joypad voting system'

    #choose your GPIO pins here
    GPIOteamA = 16
    GPIOteamB = 20
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False) 
        GPIO.cleanup()

        GPIO.setup(self.GPIOteamA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.GPIOteamB, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.scoreA = 0
        self.scoreB = 0
                   
    #Record a vote agains the given object
    def registerVote(self,channel):
        if (channel == self.GPIOteamA):
            self.scoreA = self.scoreA +1;
        elif (channel == self.GPIOteamB):
            self.scoreB = self.scoreB + 1;
        else:
            print("unknown channel input detected on GPIO pin:" + channel)

    def resetScores(self):
        self.scoreA = 0
        self.scoreB = 0


"""
In your code, implement the following

   GPIO.add_event_detect(Joypadio.GPIOteamA, GPIO.RISING, callback=JoypadioObject.registerVote, bouncetime=200)
   GPIO.add_event_detect(Joypadio.GPIOteamB, GPIO.RISING, callback=JoypadioObject.registerVote, bouncetime=200)
"""
