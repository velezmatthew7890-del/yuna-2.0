import discord
import requests
import os
import json
from discord.ext import commands, tasks
from datetime import datetime, time

# =====================
# ENV
# =====================
TOKEN = os.getenv("TOKEN")

# =====================
# BOT SETUP
# =====================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================
# DATABASE (server -> channel)
# =====================
DB_FILE = "channels.json"

def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

channel_data = load_data()

# =====================
# TEST COMMAND
# =====================
@bot.command()
async def test(ctx):
    await ctx.send("✅ bot is working")

# =====================
# SETUP COMMAND (IMPORTANT)
# =====================
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):

    channel_data[str(ctx.guild.id)] = channel.id
    save_data(channel_data)

    await ctx.send(f"✅ Quote channel set to {channel.mention}")

# =====================
# QUOTE API
# =====================
def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=10)
        data = r.json()[0]
        return data["q"], data["a"]
    except:
        return "Keep going.", "Unknown"

# =====================
# QUOTE COMMAND
# =====================
@bot.command()
async def quote(ctx, mood="random"):

    q, author = get_quote()
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
        description=f'> "{q}"\n\n> — {author}',
        color=color
    )

    await ctx.send(embed=embed)

# =====================
# DAILY SYSTEM (MULTI-SERVER)
# =====================
@tasks.loop(minutes=1)
async def daily_quote():

    now = datetime.utcnow().time()
    target = time(hour=18, minute=0)

    if now.hour != target.hour or now.minute != target.minute:
        return

    quote, author = get_quote()

    for guild_id, channel_id in channel_data.items():

        channel = bot.get_channel(int(channel_id))
        if not channel:
            continue

        embed = discord.Embed(
            title="⌬・Quote of the Day",
            description=f'> "{quote}"\n\n> — {author}',
            color=0x5865F2
        )

        await channel.send(embed=embed)

# =====================
# START
# =====================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    daily_quote.start()

bot.run(TOKEN)
