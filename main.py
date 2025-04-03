import discord
import os
import requests
import json
import random
import datetime
import aladhan
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
import yt_dlp
from keep_alive import keep_alive

# Create an intents object and set the message_content intent to True
intents = discord.Intents.default()
intents.message_content = True
# Create the client with the intents object
client = discord.Client(intents=intents)

bot = commands.Bot(command_prefix="!", intents=intents)

sad_words = [
    "sad", "angry", "unhappy", "heartbroken", "depressed",
    "miserable", "sorry", "bad", "melancholy", "upset", "worried",
    "sorrowful", "disappointed", "mournful", "uneasy", "hopeless",
    "saddened", "troubled", "dejected", "gloomy", "heartsick", "doleful",
    "melancholic", "forlorn", "crestfallen", "depressing", "glum",
    "disconsolate", "inconsolable", "woebegone", "joyless", "despondent",
    "downcast", "wretched", "woeful", "brokenhearted", "distressed",
    "blue", "suicidal", "droopy", "hangdog", "downhearted", "discouraged",
    "heavyhearted", "down", "low-spirited", "heartsore", "heartbroken",
    "down in the mouth", "low", "tearful", "grieving", "despairing",
    "aggrieved", "cast down", "somber", "bleak", "regretful", "sunk",
    "dispirited", "disheartened", "weeping", "morbid", "desolate", "unquiet",
    "anguished", "lugubrious", "plaintive", "sombre", "dolorous", "morose",
    "lachrymose", "rueful", "dark", "grey", "cheerless", "dismal", "agonized",
    "wailing", "sullen", "dreary", "gray", "elegiac", "comfortless", "funereal",
    "drear", "black", "murky", "darkening", "saturnine", "elegiacal",
    "depressing", "pathetic", "heartbreaking", "unfortunate", "mournful",
    "melancholy", "tearful", "saddening", "disturbing", "sorry", "teary",
    "dismal", "dreary", "drear", "lamentable", "distressful", "heartrending",
    "deplorable", "distressing", "woeful", "poignant", "disquieting", "touching",
    "grievous", "moving", "discouraging", "disheartening", "perturbing",
    "discomforting", "affecting", "dispiriting", "discomposing", "انتحر", "زعلان",
    "انا زعلان", "احا", "لا", "انت هنتحر", "كفاية", "بطل خرا", "انت خنزير", "خنزير",
    "😭", "😢", "😔", "😞", "😓", "😩", "😫", "😤", "😡", "🤬"
]

starter_encouragements = [
    "Cheer up!", "Hang in there.", "You are a great person!", "هتنجح المرة الجيه",
    "Don't give up!", "Stay strong!", "انت قدها", "حاول تاني", "انت تقدر", "متستسلمش"
]

voice_clients = {}

yt_dl_options = {'format': 'bestaudio/best'}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {'options': "-vn"}


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = '\"' + json_data[0]['q'] + '\" - ' + json_data[0]['a']
    return quote


def get_prayer_times():
    location = aladhan.City("Cairo", "EG")  # Doha, Qatar
    adhan_client = aladhan.Client(location)
    adhans = adhan_client.get_today_times()
    return adhans


@client.event
async def on_ready():
    print('We logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    #   time = datetime.datetime.now().strftime("%H:%M (%p)")
    #   for adhan in get_prayer_times():
    #       if time == (adhan.readable_timing(show_date=False)):

    if msg.startswith('!inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    if any(word.lower() in msg.lower() for word in sad_words):
        await message.channel.send(random.choice(starter_encouragements))

# Play YouTube Sounds
    if msg.startswith('!play'):
        try:
            voice_client = await message.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as err:
            print(err)

        try:
            url = msg.split()[1]
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            player = discord.FFmpegPCMAudio(song, **ffmpeg_options,
                                            executable="C:\\ffmpeg\\ffmpeg.exe")
            voice_clients[message.guild.id].play(player)
        except Exception as err:
            print(err)

    if msg.startswith('!pause'):
        try:
            voice_clients[message.guild.id].pause()
        except Exception as err:
            print(err)

    if msg.startswith('!resume'):
        try:
            voice_clients[message.guild.id].resume()
        except Exception as err:
            print(err)

    if msg.startswith('!stop'):
        try:
            voice_clients[message.guild.id].stop()
            await voice_clients[message.guild.id].disconnect()
        except Exception as err:
            print(err)


@tasks.loop(minutes=1)  # Check every minute to avoid missing the exact time
async def check_prayer_times():
    time_now = datetime.datetime.now().strftime("%H:%M (%p)")  # Matches the prayer times format
    prayer_times = get_prayer_times()

    for adhan in prayer_times:
        if time_now == (adhan.readable_timing(show_date=False)):
            for guild in bot.guilds:
                general_channel = discord.utils.get(guild.voice_channels, name="General")
                if general_channel:
                    try:
                        voice_client = await general_channel.connect()
                        sound_path = "الأذان المكي.mp3"  # Path to your specified sound

                        if not os.path.exists(sound_path):
                            print("Sound file not found!")
                            return

                        audio_source = discord.FFmpegPCMAudio(sound_path, **ffmpeg_options,
                                                              executable="C:\\ffmpeg\\ffmpeg.exe")
                        voice_client.play(audio_source, after=lambda e: print(f"Finished playing: {e}"))

                        while voice_client.is_playing():
                            await asyncio.sleep(1)  # Wait until playback finishes

                        await voice_client.disconnect()
                    except Exception as err:
                        print(f"Error playing sound: {err}")
                    return

load_dotenv()
TOKEN = os.getenv('TOKEN')
keep_alive()

client.run(TOKEN)
