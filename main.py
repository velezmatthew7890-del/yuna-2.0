import discord
import requests
import os
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    data = response.json()[0]
    return data["q"], data["a"]

@tasks.loop(hours=24)
async def daily_quote():
    channel = bot.get_channel(CHANNEL_ID)

    quote, author = get_quote()

    embed = discord.Embed(
        title="⌬・Quote of the Day",
        description=f'"{quote}"\n\n— {author}',
        color=0x2b2d31
    )

    await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_quote.start()

bot.run(TOKEN)
