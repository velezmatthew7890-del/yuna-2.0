import discord
import requests
import os
from discord.ext import commands, tasks

# === ENV VARIABLES (Railway) ===
TOKEN = os.getenv("TOKEN")

channel_id = os.getenv("CHANNEL_ID")

if channel_id is None:
    raise Exception("CHANNEL_ID is missing in Railway variables")

CHANNEL_ID = int(channel_id)

# === BOT SETUP ===
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# === GET QUOTE ===
def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    data = response.json()[0]
    return data["q"], data["a"]

# === COMMAND: !quote (with moods) ===
@bot.command()
async def quote(ctx, mood=None):
    quote, author = get_quote()

    if mood == "sad":
        title = "💔 Sad Quote"
        color = 0x2b2d31

    elif mood == "motivational":
        title = "🔥 Motivational Quote"
        color = 0xf1c40f

    elif mood == "dark":
        title = "🖤 Dark Quote"
        color = 0x000000

    else:
        title = "⌬ Random Quote"
        color = 0x5865F2

    embed = discord.Embed(
        title=title,
        description=f'> "{quote}"\n\n> — {author}',
        color=color
    )

    await ctx.send(embed=embed)

# === DAILY QUOTE LOOP ===
@tasks.loop(hours=24)
async def daily_quote():
    channel = bot.get_channel(CHANNEL_ID)

    quote, author = get_quote()

    embed = discord.Embed(
        title="⌬・Quote of the Day",
        description=f'> "{quote}"\n\n> — {author}',
        color=0x5865F2
    )

    await channel.send(embed=embed)

# === START BOT ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_quote.start()

bot.run(TOKEN)
