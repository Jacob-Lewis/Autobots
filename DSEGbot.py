import discord 
import os
from datetime import datetime
from discord.ext import tasks, commands
from server import keep_alive
import drive
from drive import projects, messages, log, Event

#message key
OPT_IN_S = 0
OPT_OUT_S = 1
OPT_IN_F = 2
OPT_OUT_F = 3
MILESTONE = 4

client = commands.Bot('.')
users = []
to_send = ''

@client.event
async def on_ready():
    print('{0.user} reporting for duty'.format(client))
      
@client.event
async def on_message(message):
    if message.author == client.user:
        return

       #opting in, adds user to list of users and adds their id to the file
    if message.content.startswith('$opt in'):
        msg = message.content.split()
        args = len(msg)
        if args != 3:
            await message.author.send("Invalid # of arguments! Format: \"$opt in [project_name]\"")
        else:
            for p in projects:
                if msg[2] == p.title:
                    if message.author.id in p.discord_ids:
                        await message.author.send(messages[OPT_IN_F])

                        now = datetime.now()
                        log.append(Event(datetime.strftime(now, "%m/%d/%Y %H:%M"), 'user failed to opt into ' + p.title, message.author.name))
                        drive.update_log(log)
                    else:
                        p.discord_ids.append(message.author.id)
                        await message.author.send(messages[OPT_IN_S])
                        drive.update_file(p)

                        now = datetime.now()
                        log.append(Event(datetime.strftime(now, "%m/%d/%Y %H:%M"), 'user successfully opted into ' + p.title, message.author.name))
                        drive.update_log(log)
                    return
            await message.author.send("Project name not found.")

    #opting out, removes user from list of users and from file
    if message.content.startswith('$opt out'):
        msg = message.content.split()
        args = len(msg)
        if args != 3:
            await message.author.send("Invalid # of arguments! Format: \"$opt out [project_name]\"")
        else:
            for p in projects:
                if msg[2] == p.title:
                    if message.author.id in p.discord_ids:
                        p.discord_ids.remove(message.author.id)
                        drive.update_file(p)
                        await message.author.send(messages[OPT_OUT_S])

                        now = datetime.now()
                        log.append(Event(datetime.strftime(now, "%m/%d/%Y %H:%M"), 'user successfully opted out of ' + p.title, message.author.name))
                        drive.update_log(log)
                    else:
                        await message.author.send(messages[OPT_OUT_F])

                        now = datetime.now()
                        log.append(Event(datetime.strftime(now, "%m/%d/%Y %H:%M"), 'user failed to opt out of ' + p.title, message.author.name))
                        drive.update_log(log)
                    return
            await message.author.send("Project name not found.")       


#TODO: refresh sheets and create log if it's sunday
#if today is a reminder day, sends reminder message to opted-in users at desired interval
@tasks.loop(hours=24)
async def loop_send():
  global projects
  global messages

  if datetime.today().weekday() == 2:
    drive.refresh()
    projects = drive.get_projects()
    messages = drive.get_messages()

  for i in range(0, len(projects)):

    last_sent = projects[i].last_sent

    if (datetime.now() - datetime.strptime(last_sent, "%m/%d/%Y")).days >= 1:

        #everyday undergo same process in on_ready
        start_date = datetime.strptime(projects[i].start_date, "%m/%d/%Y")

        now = datetime.now()
        days_since_start = (now - start_date).days

        for m in range(0,len(projects[i].m_dates)):
            days_until_m = projects[i].m_dates[m] - days_since_start
            if days_until_m == 1 or days_until_m == 3 or days_until_m == 7:

              for id in projects[i].discord_ids:
                try:
                  user = await client.fetch_user(id)
                  await user.send(messages[MILESTONE] + "\nMilestone: " + projects[i].m_names[m] + "\tProject Day: " + str(projects[i].m_dates[m]))
                except:
                  #log failure to find id
                  log.append(Event(datetime.strftime(now, "%m/%d/%Y %H:%M"), 'bot tried to message nonexistent user', 'N/A'))
                  drive.update_log(log)
            projects[i].last_sent = datetime.strftime(now, "%m/%d/%Y")
            drive.update_file(projects[i])
  
  

#run server, activate loop, run bot
keep_alive()
loop_send.start()
client.run('insert bot token here')
