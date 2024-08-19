import discord
import os
import pymongo
from discord.ext import commands
from pymongo.errors import OperationFailure
from openai import OpenAI
import asyncio
import json
import requests
from listings import totalListed

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

mongo_client = pymongo.MongoClient(os.getenv('CLIENT_STRING'))
client = OpenAI(
   api_key=os.getenv('OPENAPI'),
)
steam_key = os.getenv('STEAM_API_KEY')

database = mongo_client['LongLostStakingDatabase']
collection = database['orders']

TARGETUSER = 218623043096805377
CUSTOM_EMOJI_ID = 1237289837569249320
CUSTOM_EMOJI_NAME = 'jesse'



def chunk_string(s, chunk_size):
    return [s[i:i + chunk_size] for i in range(0, len(s), chunk_size)]

async def change_stream_task():
    try:
        # Start the change stream
        change_stream = collection.watch(full_document='updateLookup')

        while True:
            change = change_stream.next()
            if change['operationType'] == 'insert':
                new_entry = change['fullDocument']
                channel_id = 779388088706662463  # Replace with your channel ID
                channel = bot.get_channel(channel_id)

                if channel:
                    await channel.send(f'New entry added: {new_entry}')

    except OperationFailure as e:
        print(f'MongoDB OperationFailure: {e}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    #asyncio.create_task(change_stream_task())

@bot.event
async def on_message(message):

    # Check if the message is sent by the target user
    print("test")
    if message.author.id == TARGETUSER:
        custom_emoji = f'<:{CUSTOM_EMOJI_NAME}:{CUSTOM_EMOJI_ID}>'
            # React to the message with the custom emoji
        await message.add_reaction(custom_emoji)
        

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))


