import sys
import pprint
import os
from random import randint
from pygame import mixer

class JoypadAudio:
    
    sound_5secondsleft          = 'resources/5secondsleft.wav'
    sound_vote_open             = 'resources/vote_open.wav'    
    sound_win_team_a            = 'resources/win_team_a.wav'
    sound_win_team_b            = 'resources/win_team_b.wav'
    
    def __init__(self, joypadui):
        self.joypadui = joypadui
        self.joypadui.subscribe(self.eventHandler)
       
    # joypadui events raised go here
    def eventHandler(self, event):
        if (event.action=="countdown"):
            self.onCountdown(event)
        if (event.action=="openVote"):
            self.onOpenVote(event)            
        if (event.action=="announceWinner"):
            self.onAnnounceWinner(event)      
            
    def onCountdown(self, event):
        if (event.time == 5 and (event.status == self.joypadui.STATUS_VOTE_ACTIVE() or event.status == self.joypadui.STATUS_VOTE_PENDING())):
            try:
                sound = mixer.Sound(self.sound_5secondsleft)
                sound.play()
            except:
                print "unable to play sound " + self.sound_5secondsleft;


    def onOpenVote(self, event):
        try:
            sound = mixer.Sound(self.sound_vote_open)
            sound.play()
        except:
            print "unable to play sound " + self.sound_vote_open;
            
            
    def onAnnounceWinner(self, event):
        
        if (event.team == 'a'):
            soundToPlay = self.sound_win_team_a
        else:
            soundToPlay = self.sound_win_team_b
        
        try:
            sound = mixer.Sound(soundToPlay)
            sound.play()
        except:
            print "unable to play sound " + soundToPlay            