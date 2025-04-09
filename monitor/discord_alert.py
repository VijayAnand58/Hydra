import discord
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

async def send_discord_message(msg):
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"[EXTERNAL] {msg}")
    else:
        print("Channel not found!")

def get_bot():
    return client

def get_send_function():
    return send_discord_message

def get_token():
    return TOKEN
