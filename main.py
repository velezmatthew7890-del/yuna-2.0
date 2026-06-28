import discord
import requests
import os
import random
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

# === QUOTE API ===
def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=10)
        data = r.json()[0]
        return data["q"], data["a"]
    except:
        return "Keep going.", "Unknown"

# === MOOD STYLES ===
def style(mood):
    styles = {
        "sad": ("💔 Sad Quote", 0x2b2d31),
        "motivational": ("🔥 Motivational Quote", 0xf1c40f),
        "dark": ("🖤 Dark Quote", 0x000000),
        "random": ("⌬ Quote", 0x5865F2)
    }
    return styles.get(mood, styles["random"])

# === COMMAND ===
@bot.command()
async def quote(ctx, mood="random"):
    quote, author = get_quote()

    title, color = style(mood)

    embed = discord.Embed(
        title=title,
        description=f'> "{quote}"\n\n> — {author}',
        color=color
    )

    message = await ctx.send(embed=embed)

    await message.add_reaction("👍")
    await message.add_reaction("❤️")
    await message.add_reaction("🔥")

# === DAILY QUOTE ===
@tasks.loop(minutes=1)
async def daily_quote():
    now = datetime.utcnow().time()

    # 6 PM UTC daily
    target = time(hour=18, minute=0)

    if now.hour == target.hour and now.minute == target.minute:
        channel = bot.get_channel(CHANNEL_ID)
        if channel is None:
            return

        quote, author = get_quote()

        embed = discord.Embed(
            title="⌬・Quote of the Day",
            description=f'> "{quote}"\n\n> — {author}',
            color=0x5865F2
        )

        message = await channel.send(embed=embed)

        await message.add_reaction("👍")
        await message.add_reaction("❤️")
        await message.add_reaction("🔥")

# === START BOT ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_quote.start()

bot.run(TOKEN)

