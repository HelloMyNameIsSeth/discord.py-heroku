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


async def send_messages(channel, messages):
    for message in messages:
        await channel.send(message)

@bot.event
async def on_message(message):
    
    if message.content.lower().startswith('/game'):
        msg = message.content[5:]

        current_channel = message.channel
        # To bug if input has no space
        if msg.startswith(' '):
            msg = msg[1:]
        
        #with open('data.json', 'r') as file:
        #    parsed_data = json.load(file)

        steamlink = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={msg}&count=5&maxlength=5000&feeds=steam_community_announcements&format=json"
        
        response = requests.get(steamlink)
        if response.status_code == 200:
            data = response.json()
            news_items = data.get('appnews', {}).get('newsitems', [])
            news_strings = []
            
            for news_item in news_items:
                news_string = f"Title: {news_item.get('title')}\nContents: {news_item.get('contents')}\n\n"
                news_strings.append(news_string)
        
        else:
            print(f"Error: {response.status_code}")
            await message.channel.send("Error with the steam database: "+response.status_code)


        result_string = ''.join(news_strings)

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Based on the title and content in"+result_string+" with a focus on the words 'updates' or 'patches' can you generate a summary in dotpoints of all the changes that have happened. If there are no updates please summarize what information that is avaliable and specify that there are no updates"}
            ]
            )
        completion_content = completion.choices[0].message.content
        print(completion_content)
        message_chunks = chunk_string(completion_content, 1900)
        for x in message_chunks:
            print(x)
        await send_messages(current_channel, message_chunks)

        
@bot.event
async def on_message(message):
    if message.content.lower().startswith('/listed'):
            listed = totalListed()
            string = ""
            for x in listed:
                address = x["address"]
                rate = x["rate"]
                string = string + "\n" + "Address: " + address + "Rate: " + rate
                
            embed = discord.Embed(
            title="Title of the Embed",
            description="Description of the Embed",
            color=discord.Color.blue()
            )
            embed.add_field(name="Field Name", value="test", inline=False)
            embed.set_footer(text="Footer text")
            
            
            await message.channel.send(embed=embed)

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))


