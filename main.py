import discord
from discord.ext import commands, tasks
import os
import requests
import json
import random
from datetime import datetime, time

# === ENV ===
TOKEN = os.getenv("TOKEN")

channel_id = os.getenv("CHANNEL_ID")
if channel_id is None:
    raise Exception("CHANNEL_ID is missing in Railway variables")

CHANNEL_ID = int(channel_id)

# === INTENTS ===
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === SIMPLE PERSISTENT STORAGE (no repeat quotes) ===
FILE = "used_quotes.json"

def load_used():
    try:
        with open(FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_used(data):
    with open(FILE, "w") as f:
        json.dump(list(data), f)

used_quotes = load_used()

# === QUOTE API ===
def get_quote():
    r = requests.get("https://zenquotes.io/api/random")
    data = r.json()[0]
    return data["q"], data["a"]

# === STYLES ===
def style(mood):
    styles = {
        "sad": ("💔 Sad Quote", 0x2b2d31),
        "motivational": ("🔥 Motivational Quote", 0xf1c40f),
        "dark": ("🖤 Dark Quote", 0x000000),
        "random": ("⌬ Quote", 0x5865F2)
    }
    return styles.get(mood, styles["random"])

# === SLASH COMMAND ===
@bot.tree.command(name="quote", description="Get a quote")
async def quote(interaction: discord.Interaction, mood: str = "random"):

    quote, author = get_quote()

    # avoid repeats (persistent)
    while quote in used_quotes:
        quote, author = get_quote()

    used_quotes.add(quote)
    save_used(used_quotes)

    title, color = style(mood)

    embed = discord.Embed(
        title=title,
        description=f'> "{quote}"\n\n> — {author}',
        color=color
    )

    await interaction.response.send_message(embed=embed)

# === DAILY SYSTEM (stable timing) ===
@tasks.loop(minutes=1)
async def daily_quote():
    now = datetime.utcnow().time()
    target = time(hour=18, minute=0)  # 6 PM UTC

    if now.hour == target.hour and now.minute == target.minute:
        channel = bot.get_channel(CHANNEL_ID)

        quote, author = get_quote()

        embed = discord.Embed(
            title="⌬・Quote of the Day",
            description=f'> "{quote}"\n\n> — {author}',
            color=0x5865F2
        )

        await channel.send(embed=embed)

# === SYNC SLASH COMMANDS ===
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    daily_quote.start()

bot.run(TOKEN)

