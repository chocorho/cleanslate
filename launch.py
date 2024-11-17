#!/usr/bin/env python3
"""
    Copyright (c) 2024 suwa, chocorho
"""

import datetime
import discord
from discord.ext import commands

import psycopg2

import secret


"""
    A discord bot to be used by Moderators to manage messages in large numbers.
"""


class CleanSlateBot:
    def __init__(self):
        @bot.event
        async def on_ready():
            print(f'We have logged in as {bot.user}')
            await self.load_cogs()

        @bot.event
        async def on_disconnect():
            print("Bot has disconnected.")
  
    def commands(self):
        @bot.command()
        async def ping(message):
            await message.channel.send('Pong!')
    
        @bot.command()
        async def get_channel_id(message):
            i = message.channel.id
            print(f'id is {i}')
            await message.channel.send(f'id is {i}')
    
        @bot.command()
        async def disconnect(message):
            await message.channel.send("Thank you for choosing mayyro-bots!")
            print("Disconnecting...")
            await bot.close()
    
        @bot.command()
        async def dry_run(message, channel_str, target_str, target2_str):
            if (target_str is None or "" == target_str):
                await message.channel.send('target not specified. Try again.')
            else:
                end_date = datetime.datetime(2021, 5, 1)
                num_processed = 0
                num_saved = 0
                selected_channel = message.channel
                for ch in message.guild.channels:
                    if (channel_str == ch.name or int(channel_str) == ch.id):
                        selected_channel = ch
                        # archive 'em here!
                        connexion = psycopg2.connect(host='localhost', database='discord_messages', user=secret.credentials.db_user, password=secret.credentials.db_passwd)
                        async for historical_message in selected_channel.history(limit=None, before=end_date): # TODO: change parameter to go forwards in time?
                            target = int(target_str)
                            target2 = int(target2_str)
                            ts = historical_message.created_at # TODO: get time in addition to date!!!
                            #print(f'now inspecting the next message, from {ts}')
                            num_processed += 1
                            if (target == historical_message.author.id or target2 == historical_message.author.id):
                                # save the message in private database
                                #next_apparent_id = connexion.xid()
                                next_cursor = connexion.cursor()
                                next_sql = 'INSERT INTO channel_name_backup (username, userid, message, timestamp) VALUES (%s, %s, %s, %s);'
                                params = (historical_message.author.name, historical_message.author.id, historical_message.content, ts)
                                next_cursor.execute(next_sql, params)
                                #connexion.tpc_begin(next_apparent_id)
                                #connexion.tpc_prepare()
                                connexion.commit()
                                num_saved += 1
                    
                                ## do the deletion
                                print(f"now deleting the next message, from {message.created_at}")
                                historical_message.delete()
                                time.sleep(1)
                            #else:
                            #  print(f"sorry, kid, the sender IDs do not match. {historical_message.author.id}!={target}")
                        print(f"num_processed={num_processed}, saved={num_saved}.")
                        await message.channel.send(f"processed a total of {num_processed} messages, {num_saved} of which were filtered.")
                        connexion.close()

    async def load_cogs(self):
       await bot.load_extension("cogs.user_commands.reply")
       await bot.load_extension("cogs.privilleged_commands.redact")

    def run(self):
        bot.run(secret.credentials.bottoken)
        

if __name__ == '__main__':
    intents = discord.Intents.all()

    bot = commands.Bot(command_prefix='!', intents=intents)
    CleanSlateBot().run()

