import discord
import os
import pymongo
from discord.ext import commands
from pymongo.errors import OperationFailure
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

mongo_client = pymongo.MongoClient(os.getenv('CLIENT_STRING'))
database = mongo_client['LongLostStakingDatabase']
collection = database['orders']

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

                itemOwner = new_entry["owner"]
                product = new_entry["product"]
                productName = product["productName"]


                stringBuilder = print("Item Owner: ",itemOwner,"\n","Product: ", productName)

                if channel:
                    await channel.send(f'New entry added: {stringBuilder}')

    except OperationFailure as e:
        print(f'MongoDB OperationFailure: {e}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    asyncio.create_task(change_stream_task())

@bot.event
async def on_message(message):
    # Your message handling logic here
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')


if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))


