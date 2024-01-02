import discord
import os
import pymongo
from discord.ext import commands
from pymongo.errors import OperationFailure

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

mongo_client = pymongo.MongoClient(os.getenv('CLIENT_STRING'))
database = mongo_client['LongLostStakingDatabase']
collection = database['orders']

@bot.event
async def on_ready():
    try:
        # Start the change stream
        change_stream = collection.watch(full_document='updateLookup')
        async for change in change_stream:
            if change['operationType'] == 'insert':
                new_entry = change['fullDocument']
                channel_id = 779388088706662463  # Replace with your channel ID
                channel = bot.get_channel(channel_id)

                if channel:
                    await channel.send(f'New entry added: {new_entry}')

    except OperationFailure as e:
        print(f'MongoDB OperationFailure: {e}')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')


if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))


