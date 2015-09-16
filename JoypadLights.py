import	sys
import	pprint
import	os
import time
import	gertbot2 as gb

class JoypadLights:
	
	def	__init__(self, joypadui):
		self.joypadui = joypadui
		self.joypadui.subscribe(self.eventHandler)
		
		self.gb_board	=	3
		gb.open_uart(0)
		print("Found gertbot board version:	%d"	% gb.get_version(self.gb_board))
		

		# set brushed mode
		gb.set_mode(self.gb_board,0,1)
		gb.set_mode(self.gb_board,1,1)
		
		#setup the on/off ramps
		gb.set_brush_ramps(self.gb_board, 0,2,5,1)
		gb.set_brush_ramps(self.gb_board, 1,2,5,1)

		# light init
		self.lights('a','off')
		self.lights('b','off')
		#light check
		print "Light Check initialising ..."
		time.sleep(1)
		print "RED (a) ON"
                self.lights('a','on')
                time.sleep(1)
                print "RED (a) OFF"
                self.lights('a','off')
                time.sleep(1)
                print "BLUE (b) ON"
                self.lights('b','on')
                time.sleep(1)
                print "BLUE (b) OFF"
                self.lights('b','off')
                print "Light check finished"
		
	# joypadui events raised go here
	def	eventHandler(self,	event):
		if (event.action=="loadVote"):
			self.onLoadVote(event)		
		if (event.action=="openVote"):
			self.onOpenVote(event)				
		#if	(event.action=="countdown"):
		#	self.onCountdown(event)
			
		if (event.action=="announceWinner"):
			self.onAnnounceWinner(event)		
		
	def	onLoadVote(self, event):
		self.lights('a','off')
		self.lights('b','off')
		
	def	onOpenVote(self, event):
		self.lights('a','on')
		self.lights('b','on')
	
	def	onAnnounceWinner(self, event):
		if (event.team == 'a'):
			self.lights('a','on')
			self.lights('b','off')
		else:
			self.lights('a','off')
			self.lights('b','on')
		
	
	# turn the lights on/off for a team
	def	lights(self, team, state):
		
		if (team =='a'):
			channel	= 0
		else:
			channel	= 1
		
		if (state=='on'):
			direction =	1
		else:	
			direction =	0
		
		gb.move_brushed(self.gb_board, channel, direction)
		
