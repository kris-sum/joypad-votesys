joypad-votesys
==============

Joypad (http://www.joypadbar.co.uk) voting system.

This is python code for running a voting booth, which is powered by a Raspberry Pi and using its GPIO functions.

Execute with : 
```
sudo python run.py
```

Pre-configure your voting by editing the resources directory, files should be like this:

| file | description |
|------|-------------|
| 1a.txt | Text file containing the first vote heading for the left column (column A) |
| 1b.txt | Text file containing the first vote heading for the rightt column (column B) |
| 1a.gif or 1a.jpg | The first vote image file for the left column |
| 1b.gif or 1b.jpg | the first vote image file for the right column | 
| 2a.txt | second vote text ... |
| 2b.txt | second vote text ... |
| 2a.gif | second vote image ... |
| 2b.gif | second vote image ... |

Certain code settings can be modified inside Joypadui.py:

| setting name | description |
| -------------|-------------|
| timerSeconds | How long people get to vote (in seconds) | 
| timeOnVoteResults | How long should the system stay on the vote results screen for before moving on to the next vote |

Contact Joypad Management for more information.
Code written by Kris of Switch Systems Ltd.
