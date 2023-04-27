import discord
from discord.ext import commands
from vocode.streaming.output_device.base_output_device import BaseOutputDevice

TOKEN = "YOUR_BOT_TOKEN"
bot = commands.Bot(command_prefix="!")

class DiscordOutputDevice(BaseOutputDevice):
    def __init__(self, voice_client: discord.voice_client, sampling_rate, audio_encoding):
        super().__init__(sampling_rate, audio_encoding)
        self.voice_client = voice_client

    async def send_async(self, chunk):
        self.voice_client.send_audio_packet(chunk, encode=False)
