# Autobots

This project is a working prototype for an accountability coach/project coordinator bot. Its primary function
is to message project members with reminders on upcoming milestones. It does this by reading in an input file 
containing the Discord user ids of project members, the project start date, and the project milestone days. The
format for the input file is straightforward and can be seen in testinfo.txt. If the number of days since the 
project start date is approaching a milestone day (7, 3, and 1 day(s) before), the bot will directly message
the project members on Discord with a reminder. Project members can opt in and out of reminders by sending
'$opt in' and '$opt out' into the Discord channel or the bot's direct messages.

In its current state the bot sends reminders when it starts up and every 24 hours after that. This can easily be customized by 
changing the parameters of the loop on line 82.

