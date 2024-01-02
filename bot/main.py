import discord
import os
import pymongo
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

mongo_client = pymongo.MongoClient(os.getenv('CLIENT_STRING'))
database = mongo_client['LongLostStakingDatabase']
collection = database['orders']

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}({bot.user.id})')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@collection.watch()
async def on_collection_change(change):
    if change['operationType'] == 'insert':
        new_entry = change['fullDocument']
        channel_id = '779388088706662463'  # Replace with your channel ID
        channel = bot.get_channel(channel_id)

        if channel:
            await channel.send(f'New entry added: {new_entry}')

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))


