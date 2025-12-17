import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
from collections import deque

# looks for the env file and gets the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# set permissions to default and read what the users type via message_content = True
intents = discord.Intents.default()
intents.message_content = True

# bot is initialized with the prefix // and the set intent permissions
bot = commands.Bot(command_prefix='//', intents=intents)

# A single global queue since we only have one server
song_queue = deque()

yt_dlp_opts = {
    'format': 'bestaudio/best',       
    'noplaylist': True,                                        #setting the options for yt_dlp, set to get best audio quality possible, 
    'quiet': True,                                             #no playlist means only play the top song if playlist is linked, quiet means dont spam the console with text
    'default_search': 'auto',                                  #if url isnt provided, search youtube, and bind it to ipv4
    'source_address': '0.0.0.0'       
}

# FFmpeg Options: Controls how we stream the audio.
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn' # -vn means "No Video", we only want to stream audio
}

ytdl = yt_dlp.YoutubeDL(yt_dlp_opts) #intialize the extractor 

def play_next(ctx):
    if len(song_queue) == 0:
        return

    song_url, title, requester = song_queue.popleft()

    # feed the direct URL into FFmpeg, which converts it to a format Discord understands.
    ctx.voice_client.play(
        discord.FFmpegPCMAudio(song_url, **ffmpeg_options), 
        after=lambda e: play_next(ctx)
    )
    
    coro = ctx.send(f"Now playing: **{title}** (Requested by **{requester}**) 🎵")
    asyncio.run_coroutine_threadsafe(coro, bot.loop)

#triggered when bot connects to discord
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

#command that plays song from yt
@bot.command()
async def play(ctx, *, query): 
    #checks if author of command is in voice or not 
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to play music!")
        return
    
    #sets bots voice channel to users voice channel
    voice_channel = ctx.author.voice.channel
    
    #if the bot is not connected, join the user's channel.
    if ctx.voice_client is None:
        await voice_channel.connect()
    #if the bot is connected but in a different channel, move to the user's.
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)
    
    vc = ctx.voice_client

    await ctx.send(f"Searching for: **{query}**...")

    #to prevent the bot from freezing, we run this in a separate thread/executor.
    #this is a asynchronous process, loop constantly keeps checking for events, run in executor sends a synchronous query in the loop extract_info to a seperate thread
    #this prevents long wait times, as extract_info takes a long time to connect to yt servers and execute, making the bot hang. 
    loop = asyncio.get_event_loop()
    try:
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
    except Exception as e:
        await ctx.send("An error occurred while searching.")
        print(e)
        return
    
    #if 'entries' exists, it means we got a list of results (search query). We take the first one.
    if 'entries' in data:
        data = data['entries'][0]

    song_url = data['url']  # The direct link to the audio stream
    title = data['title']
    requester = ctx.author.name

    if vc.is_playing():
        song_queue.append((song_url, title, requester))
        await ctx.send(f"Added to queue: **{title}** (Position: {len(song_queue)})")
    else:
        # feed the direct URL into FFmpeg, which converts it to a format Discord understands.
        vc.play(
            discord.FFmpegPCMAudio(song_url, **ffmpeg_options), 
            after=lambda e: play_next(ctx)
        )
        await ctx.send(f"Now playing: **{title}** (Requested by **{requester}**)")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped! ⏭️")

@bot.command()
async def q(ctx):
    if len(song_queue) == 0:
        await ctx.send("The queue is empty.")
    else:
        list_str = " **Queue:**\n"
        for i, (url, title, req) in enumerate(song_queue, start=1):
            list_str += f"{i}. {title} (Req: {req})\n"
        await ctx.send(list_str)

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Paused ⏸️")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Resumed ▶️")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        song_queue.clear()
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected 👋")


if TOKEN:
    bot.run(TOKEN)
else:
    print("ERROR: Token not found. Please check your .env file.")