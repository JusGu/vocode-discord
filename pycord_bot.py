import discord
from dotenv import load_dotenv
import os
from pydub import AudioSegment
from elevenlabs import generate
import io
load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')
bot = discord.Bot()
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

@bot.event
async def on_ready():
    print(f"{bot.user.name} is connected to Discord!")

connections = {}

async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()  # Disconnect from the voice channel.
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)  # Send a message with the accumulated files.

@bot.command()
async def record(ctx):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    connections.update({ctx.guild.id: vc})  # Updating the cache with the guild and channel.

    vc.start_recording(
        discord.sinks.WaveSink(),  # The sink type to use.
        once_done,  # What to do once done.
        ctx.channel  # The channel to disconnect from.
    )
    await ctx.respond("Started recording!")

@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        await ctx.delete()  # And delete.
    else:
        await ctx.respond("I am currently not recording here.")  # Respond with this if we aren't recording.

bot.run(TOKEN)