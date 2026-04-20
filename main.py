import os
import threading
from flask import Flask
import discord
from discord.ext import commands

app = Flask(__name__)

@app.get("/")
def home():
    return "Bot actif"

def run_flask():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask, daemon=True).start()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("Missing DISCORD_TOKEN")

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook():
    print("🚀 setup_hook…")

    await bot.load_extension("cogs.alerts")
    await bot.load_extension("cogs.reactions")

    print("✔ Cogs chargés")


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")


bot.run(TOKEN)