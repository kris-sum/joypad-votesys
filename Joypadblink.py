from blinkstick import blinkstick


class Joypadblink:
    'hardware class for blinkstick support'
    'deprecated - pi isnt fast enough to do this and the UI at the same time'

    attractModeInterval = 100
    attractModeState = 0

    def __init__(self, joypadui):
        joypadui.blinkstick = self
        self.root = joypadui.root

    def attractMode(self):
 
        for b in blinkstick.find_all():
            if (self.attractModeState == 0):
                b.turn_off()
            elif (self.attractModeState == 1):
                b.set_color(0,0,255,0,0)
            elif (self.attractModeState == 2):
                b.turn_off()
            elif (self.attractModeState == 4):
                b.set_color(0,0,0,0,255)
            elif (self.attractModeState == 5):
                b.turn_off()

        self.attractModeState +=1;
        if (self.attractModeState == 6):
            self.attractModeState = 0
           
        self.root.after(100,self.attractMode);


            
        
