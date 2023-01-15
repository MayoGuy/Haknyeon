import disnake
from disnake.ext import commands, tasks
from datetime import date
from db import Hanknyeon
import sys
import traceback
import asyncio
from pathlib import Path
import aiohttp
import asyncpg
import random


intents = disnake.Intents.all()
bot = Hanknyeon()

async def run():
    credentials1 = {"user": "user", "password": "pass", "database": "main", "host": "localhost"}
    bot.conn = await asyncpg.create_pool(**credentials1, max_inactive_connection_lifetime=10)
    credentials2 = {"user": "user", "password": "pass", "database": "currency", "host": "localhost"}
    bot.curr = await asyncpg.create_pool(**credentials2, max_inactive_connection_lifetime=3)
    try:
        await bot.start("TOKEN")
    except KeyboardInterrupt:
        await bot.conn.close()
        await bot.curr.close()
        await bot.logout()


@bot.event
async def on_ready():
    print("I'm Alive")
    await bot.get_cards_data()
    bot.chats = await bot.chat(get=True)
    check_limit.start()
    change_status.start()
    print(len(bot.data.keys()))


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CheckFailure):
        if str(error) == "first":
            await bot.create_profile(inter.author.id)
            await inter.send(embed=disnake.Embed(description="This is your first time using me. Your adventure with Haknyeon starts now! Use the command again to continue.", color=0xfcb8b8), ephemeral=True)
        else:
            raise error
    elif isinstance(error, commands.CommandOnCooldown):
        time = error.cooldown.get_retry_after()
        embed = disnake.Embed(title="This command is on cooldown", description=f"Try using this command after {bot.sort_time(int(time))}.", color=disnake.Color.red())
        embed.set_author(name=inter.author.display_name, icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=embed)
    elif isinstance(error, disnake.errors.HTTPException):
        print(str(error))
    else:
        raise error


@bot.event
async def on_message(msg: disnake.Message):
    if not msg.content:
        return
    if msg.channel.id not in bot.chats:
        try:
            await bot.process_commands(msg)
        except:
            pass
        return
    if msg.author == bot.user:
        return
    if msg.reference:
        m = await msg.channel.fetch_message(msg.reference.message_id)
        if m.author.id == 1024387091834077256:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'http://api.brainshop.ai/get?bid=156118&key=135p8CFWdLgfxeBz&uid={msg.author.id}&msg={msg.content}') as r:
                    res = await r.json() 
                    pts = random.randint(1, 150)
                    if pts == 150:
                        await bot.add_coins(msg.author.id, 50)
                        await msg.reply(res['cnt'], mention_author=False)
                        return await msg.channel.send(f"You earned 50 {bot.petal} by just being lucky and talking to me!")
                    else:
                        return await msg.reply(res['cnt'], mention_author=False)
    elif msg.content.startswith("<@1024387091834077256>"):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'http://api.brainshop.ai/get?bid=156118&key=135p8CFWdLgfxeBz&uid={msg.author.id}&msg={msg.content[22:]}') as r:
                res = await r.json() 
                pts = random.randint(1, 150)
                if pts == 150:
                    await bot.add_coins(msg.author.id, 50)
                    await msg.reply(res['cnt'], mention_author=False)
                    return await msg.channel.send(f"You earned 50 {bot.petal} by just being lucky and talking to me!")
                else:
                    return await msg.reply(res['cnt'], mention_author=False)


@tasks.loop(minutes=10)
async def change_status():
    await bot.change_presence(activity=disnake.Game(name=f"THE BOYZ - MAVERICK | {len(bot.guilds)} servers"))


@tasks.loop(seconds=2)
async def check_limit():
    limited_cards = await bot.limited_cards()
    for r in limited_cards:
        card = r[0]
        dated = r[1]
        if str(date.today()) >= dated:
            await bot.delete_card(card, limit=True)
            print("done dana done")

        
for file in Path('cogs').glob('**/*.py'):
    *tree, _ = file.parts
    try:
        f = f"{'.'.join(tree)}.{file.stem}"
        print(f + " has been loaded!")
        bot.load_extension(f)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

        


bot.load_extension("jishaku")

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
