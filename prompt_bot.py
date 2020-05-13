import datetime
import random
import discord.ext
from discord.ext import tasks, commands
from discord.ext.commands import Bot
import asyncio


on=0
prompt_range = 140
BOT_PREFIX = ("pt!","PT!","Pt!")
TOKEN = "XXXSECRETXXX"  #Bot token form Discord Developers - replace with your own
client = Bot(command_prefix=BOT_PREFIX) #creating client form Bot class

def gen_prompt(): #generates random number withing prompt_range and searches for it in "prompts.txt" file
    prompt_num = random.randint(1, prompt_range)
    prompt_search = "[" + str(prompt_num) + "]"
    with open("prompts.txt", "r") as fi:
        id1 = []
        for ln in fi:
            if ln.startswith(prompt_search):
                id1.append(ln[2:])
    id1 = str(id1)
    prompt = id1[4:-4]
    prompt=prompt.replace("]","")
    return prompt

@tasks.loop(count=1)  #background task counting sessions time
async def session_on():
    await client.wait_until_ready()
    global counter
    counter = 60*5*60 #set to 5 hours (command for changing session's length in furder development)
    while counter > 0:
        counter -= 1
        await asyncio.sleep(1)
    await channel.send(":x: :x: :x: The session ended!  :x: :x: :x:\n The prompt was: __**" +current_prompt + "**__\nYou can read all the works above!")

@client.event #called once on inicialization
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="your ideas!"))
    print("Logged in as " + client.user.name)


@client.command(name='give_prompt',
                description="Gives random prompt from list",
                aliases=['giveprompt', 'new_prompt', 'newprompt', 'np'],
                )
@commands.has_permissions(kick_members=True) #only members with permission to kick others from server can use this command
async def give_prompt(ctx):
    try :
        #if not session_on.loop.is_closed():
            global channel #channel set once giveprompt command issued. Bot will use this channel to communicate
            channel1 = ctx.channel.id
            str(channel1)
            channel = client.get_channel(channel1)
            session_on.start()
            #await ctx.send('{0.author.mention} requested a new prompt!'.format(ctx))
            global current_prompt #making current_prompt global var to access it in other commands
            current_prompt= gen_prompt() #calling gen_prompt to get new prompt
            str(current_prompt)
            await channel.send('{0.author.mention} started new session!\nThe new prompt is: __**'.format(ctx) + current_prompt + "**__\nYou have 5 hours to complete the prompt and upload it here.")
            return current_prompt

    except RuntimeError:
        await channel.send("Prompt already genetrated") #if session already in progress (background task running)

@client.command(name='prompt',
                description="Lists current prompt.",
                aliases=['currentprompt', 'p'],
                )
async def show_prompt(ctx):
    session = session_on.get_task()
    if session==None or session.done(): #if session never called before or task ended once already
        await ctx.send("No session in progress")
    else:
        await ctx.send("Current prompt is: __**" + current_prompt + "**__")


@client.command(name='time',
                description="Shows how much time left for session",
                aliases=['showtime', 't'],
                )
async def show_time(ctx):
    session = session_on.get_task()
    if session == None or session.done():
        await ctx.send("No session in progress")
    else:
        seconds=counter #calling global var from session_on()
        a = datetime.timedelta(0, seconds)
        await ctx.send("You have this many seconds: " + str(a))

@client.command(name='halt',
                description="Shows how much time left for session",
                aliases=['stopsession', 'stop'],
                )
@commands.has_permissions(kick_members=True) #only members with permission to kick others from server can use this command
async def stop_session(ctx):
    session = session_on.get_task()
    if session == None or session.done():
        await ctx.send("No session in progress")
    else:
        session_on.cancel() #terminates background task on wish
        await ctx.send('{0.author.mention} stopped the session!'.format(ctx))
        print('loop ended by stop')
        pass


@stop_session.error #error handling for stop_session()
async def stop_session_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("{0.author.mention}, You don't have permission to use this command!".format(ctx))


@give_prompt.error #error handling for give_prompt()
async def stop_session_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("{0.author.mention}, You don't have permission to use this command!".format(ctx))

"""@client.event
async def on_disconnect():
    session = session_on.get_task()
    if session == None or session.done():
        await channel.send(":x: Prompt_Bot is fainting from exhaustion. :x:")
    else:
        await channel.send(":x: Prompt_Bot is fainting from exhaustion. Session forcefully ended :x:")""" #writes message on bot disconnecting from Discord != script terminating -> useless spam

client.run(TOKEN) #run client (connect to discord developer Bot)
session = session_on.get_task()



