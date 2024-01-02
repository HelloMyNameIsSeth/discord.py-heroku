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
    print(f'Logged in as {bot.user.name}')
    try:
        # Start the change stream
        change_stream = collection.watch(full_document='updateLookup')

        while True:
            change = change_stream.next()
            if change['operationType'] == 'insert':
                new_entry = change['fullDocument']
                channel_id = 325858295527243776
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


