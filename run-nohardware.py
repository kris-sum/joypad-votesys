from Tkinter import *
from Joypadui import Joypadui
from JoypadioNoHardware import Joypadio


root = Tk()
joyio = Joypadio()

joypad = Joypadui(root,joyio)

joypad.initGui()

# add callbacks for GPIo events
# bouncetime = number of milliseconds before registering another button push
#GPIO.add_event_detect(Joypadio.GPIOteamA, GPIO.RISING, callback=joyio.registerVote, bouncetime=100)
#GPIO.add_event_detect(Joypadio.GPIOteamB, GPIO.RISING, callback=joyio.registerVote, bouncetime=100)


root.mainloop()
