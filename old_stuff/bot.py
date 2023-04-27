import discord
from discord.ext import commands
import asyncio
# get env
from dotenv import load_dotenv
import os
load_dotenv()
from elevenlabs import generate
from pydub import AudioSegment
import io

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

def convert_to_pcm(audio_bytes):
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    pcm_audio = audio.export(format="wav", codec="pcm_s16le", parameters=["-ac", "2", "-ar", "48000"])
    return pcm_audio

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel!")
        return
    channel = ctx.author.voice.channel

    voice_client = await channel.connect()

    text = "Hello, I am your voice bot!"
    audio = generate(text)
    pcm_audio = convert_to_pcm(audio)

    buffer = io.BytesIO(pcm_audio.read())
    buffer.seek(0)

    voice_client.play(discord.PCMAudio(buffer))
    await asyncio.sleep(5)
    await voice_client.disconnect()

@bot.event
async def on_ready():
    print(f"{bot.user.name} is connected to Discord!")

bot.run(TOKEN)