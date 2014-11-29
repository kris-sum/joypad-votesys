from Tkinter import *
import RPi.GPIO as GPIO
from Joypadui import Joypadui
from Joypadio import Joypadio

root = Tk()
joyio = Joypadio()

joypad = Joypadui(root,joyio)
joypad.initGui()

# add callbacks for GPIo events
# bouncetime = number of milliseconds before registering another button push
GPIO.add_event_detect(Joypadio.GPIOteamA, GPIO.RISING, callback=joyio.registerVote, bouncetime=200)
GPIO.add_event_detect(Joypadio.GPIOteamB, GPIO.RISING, callback=joyio.registerVote, bouncetime=200)

root.mainloop()
