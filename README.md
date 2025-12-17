AlleyBotv3:
AlleyBotv3 is a Python-based Discord bot designed for high-quality music streaming. It features a built-in queue system and utilizes asynchronous multithreading to ensure the bot remains responsive while fetching audio from YouTube.

Features:

Music Playback: Play audio directly from YouTube URLs or via search queries.
Queue System: Supports multiple users adding songs to a queue.
Playback Controls: Includes commands for //play, //skip, //pause, //resume, //stop, and //q (to view the queue).
Non-Blocking Extraction: Uses run_in_executor to prevent the bot from hanging while connecting to YouTube servers.
Smart Reconnection: Configured with FFmpeg options to automatically attempt reconnection if a stream is interrupted.

Requirements:

Python 3.8+
FFmpeg: Must be installed on your system path for audio processing.
Discord Bot Token: Obtained from the Discord Developer Portal.

 Setup & Installation
Clone the repository:

git clone https://github.com/Muzriaz003/AlleyBotv3.git
cd AlleyBotv3

Install dependencies:
pip install discord.py yt_dlp python-dotenv


Environment Variables: Create a .env file in the root directory and add your token:
DISCORD_TOKEN=your_discord_bot_token_here


Run the bot:
python main.py

Commands
//play <query/url> - Joins your voice channel and plays/queues a song.
//skip - Skips the currently playing song.
//pause - Pauses the current track.
//resume - Resumes a paused track.
//q - Displays the current song queue.
//stop - Clears the queue and disconnects the bot.
