import discord 
import os
from datetime import datetime
from discord.ext import tasks, commands
from server import keep_alive

client = commands.Bot('.')
users = []
to_send = ''

#global variables for lines that stay the same when writing to new file with updated user.id list
line_two = ''
line_three = ''

@client.event
async def on_ready():

    f = open('testinfo.txt','r')

    #LINE ONE: read users from file into list
    ids = f.readline().split()[1:]
    for id in ids:
        user = await client.fetch_user(id)
        if user is not None:
            users.append(user)
    
    #LINE TWO: read start date, then calculate how many days since project start
    global line_two
    line_two = f.readline()

    start_date_str = line_two.split()[1]
    start_date = datetime.strptime(start_date_str, "%m/%d/%Y")

    now = datetime.now()
    days_since_start = (now - start_date).days

    #LINE THREE: read milestone days, then see if today is a reminder day - reminders are 7, 3, and 1 days before milestone 
    #TO DO: get milestone names and pair them with days (there can be notifications for different milestones on the same day)
    global line_three
    line_three = f.readline() 

    milestones = line_three.split()[1:]
    for m in milestones:
        global to_send
        days_until_m = int(m) - days_since_start
        if days_until_m == 1:
            to_send = to_send + 'Milestone approaching in 1 day.'
        if days_until_m == 3:
            to_send = to_send + 'Milestone approaching in 3 days. '
        if days_until_m == 7:
            to_send = to_send + 'Milestone approaching in 7 days. '

    f.close()

    print('{0.user} reporting for duty'.format(client))
      
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    #opting in, adds user to list of users and adds their id to the file
    if message.content == '$opt in':
        if message.author in users:
            await message.author.send("You have already opted in!")
        else:
            users.append(message.author)
            await message.author.send('You have opted into project milestone reminders! You will be notified 7, 3, and 1 day(s) before every milestone.')
            update_file()

    #opting out, removes user from list of users and from file
    if message.content == '$opt out':
        if message.author in users:
            users.remove(message.author)
            await message.author.send('You have opted out of project milestone reminders. Use \'$opt in\' to opt back in.')
            update_file()
        else:
            await message.author.send('There is nothing for you to opt out of!')


#if today is a reminder day, sends reminder message to opted-in users at desired interval
@tasks.loop(hours=24)
async def loop_send():

    #everyday undergo same process in on_ready
    f = open('testinfo.txt','r')

    #LINE ONE: read users from file into list
    ids = f.readline().split()[1:]
    for id in ids:
        user = await client.fetch_user(id)
        if user is not None:
            users.append(user)
    
    #LINE TWO: read start date, then calculate how many days since project start
    global line_two
    line_two = f.readline()

    start_date_str = line_two.split()[1]
    start_date = datetime.strptime(start_date_str, "%m/%d/%Y")

    now = datetime.now()
    days_since_start = (now - start_date).days

    #LINE THREE: read milestone days, then see if today is a reminder day - reminders are 7, 3, and 1 days before milestone 
    #TO DO: get milestone names and pair them with days (there can be notifications for different milestones on the same day)
    global line_three
    line_three = f.readline() 

    milestones = line_three.split()[1:]
    global to_send
    for m in milestones:
        days_until_m = int(m) - days_since_start
        if days_until_m == 1:
            to_send = to_send + 'Milestone approaching in 1 day.'
        if days_until_m == 3:
            to_send = to_send + 'Milestone approaching in 3 days. '
        if days_until_m == 7:
            to_send = to_send + 'Milestone approaching in 7 days. '

    f.close()

    if to_send != '':
        for u in users:
            await u.send(to_send)

    to_send = ''

#can't edit files, so this behavior is emulated by making a temp file and keeping every line the same except
#for the new user id list, then setting the old file to the new one
def update_file():
    f = open("temp.txt", "w")

    #updated line one
    f.write("Users: ")
    for u in users:
        f.write(str(u.id))
        f.write(' ')
    f.write("\n")

    #lines two and three unchanged
    f.write(line_two)
    f.write(line_three)

    f.close()
    os.rename('temp.txt', 'testinfo.txt')
        
#run server, activate loop, run bot
keep_alive()
loop_send.start()
client.run('ODU2OTA4MTMzMjc1NjY0Mzk0.YNH34w.rGxJRL8EvYcz8kIJg2KxGO0MdX0')
