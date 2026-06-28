import discord
import requests
import os
from discord.ext import commands, tasks
from datetime import datetime, time

# === ENV VARIABLES ===
TOKEN = os.getenv("TOKEN")

channel_id = os.getenv("CHANNEL_ID")
if not channel_id:
    raise Exception("CHANNEL_ID is missing in Railway variables")

CHANNEL_ID = int(channel_id)

# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === GET QUOTE ===
def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=10)
        data = r.json()[0]
        return data["q"], data["a"]
    except:
        return "Keep going.", "Unknown"

# === !quote COMMAND (FIXED MOODS) ===
@bot.command()
async def quote(ctx, mood="random"):

    quote, author = get_quote()
    mood = mood.lower()

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
        title = "⌬ Quote"
        color = 0x5865F2

    embed = discord.Embed(
        title=title,
        description=f'> "{quote}"\n\n> — {author}',
        color=color
    )

    await ctx.send(embed=embed)

# === DAILY QUOTE ===
@tasks.loop(minutes=1)
async def daily_quote():
    now = datetime.utcnow().time()
    target = time(hour=18, minute=0)  # 6PM UTC

    if now.hour == target.hour and now.minute == target.minute:
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            return

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

