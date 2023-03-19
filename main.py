import disnake
from disnake.ext import commands, tasks
from datetime import date
from db import Hanknyeon
import sys
import traceback
import asyncio
from pathlib import Path
import aiohttp
import logging
import asyncpg
import random
import psutil
import topgg
from logging.handlers import RotatingFileHandler


my_handler = RotatingFileHandler('disnake.log', mode='a', maxBytes=10*1024*1024, backupCount=2, encoding=None, delay=0)
logger = logging.getLogger('disnake')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='disnake.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
logger.addHandler(my_handler)

TOKEN = ""
TOKEN_BOT = ""

bot = Hanknyeon()
topgg_webhook = topgg.WebhookManager(bot).dbl_webhook("/topgg", "D51yE_39@E")
bot.topggpy = topgg.DBLClient(bot, TOKEN, autopost=True, post_shard_count=True)


@bot.event
async def on_autopost_success():
    print(
        f"Posted server count ({bot.topggpy.guild_count}), shard count ({bot.shard_count})"
    )


async def run():
    await bot.get_cards_data()
    await bot.get_votees()
    await bot.get_boosts()
    bot.chats = await bot.chat(get=True)
    try:
        await bot.start(TOKEN_BOT)
    except KeyboardInterrupt:
        await bot.conn.close()
        await bot.curr.close()
        await bot.logout()


@bot.event
async def on_ready():
    print("I'm Alive")
    await topgg_webhook.run(5000)
    print(len(bot.data.keys()))


@bot.event
async def on_dbl_vote(data: topgg.types.BotVoteData):
    print(f"Received a vote:\n{data}")
    await bot.vote(data.user)


@bot.event
async def on_slash_command(inter):
    ch = bot.get_channel(1064903053100208158)
    await ch.send(f"**/{inter.application_command.name}** - {psutil.virtual_memory()[2]}% - {psutil.virtual_memory()[3]/1000000000} GB")


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
        etype = type(error)
        trace = error.__traceback__
        lines = traceback.format_exception(etype, error, trace)
        traceback_text = ''.join(lines)
        ch = bot.get_channel(1085272060986654831)
        await ch.send(f"```py\n{traceback_text}\n```")
        wee_embed = disnake.Embed(title="We ran into an unexpected error...", description="If this problem persists, report this on our [support server](https://discord.gg/haknyeon/)", color=bot.get_color())
        try:
            await inter.response.send_message(embed=wee_embed, ephemeral=True)
        except:
            await inter.followup.send(embed=wee_embed, ephemeral=True)




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
async def check_limit():
    limited_cards = await bot.limited_cards()
    for r in limited_cards:
        card = r[0]
        dated = r[1]
        if str(date.today()) >= dated:
            await bot.delete_card(card, limit=True)
            print("done dana done")


@tasks.loop(minutes=10)
async def insert_guilds():
    conn = await bot.curr.acquire()
    async with conn.transaction():
        await conn.execute("UPDATE guilds SET n_g=$1 WHERE gss='gs'", len(bot.guilds))
    await bot.curr.release(conn)


@check_limit.before_loop
async def before_check():
    await bot.wait_until_ready()


@insert_guilds.before_loop
async def before_guilds():
    await bot.wait_until_ready()

        
for file in Path('cogs').glob('**/*.py'):
    *tree, _ = file.parts
    try:
        f = f"{'.'.join(tree)}.{file.stem}"
        print(f + " has been loaded!")
        bot.load_extension(f)
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


bot.load_extension("jishaku")


insert_guilds.start()
check_limit.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
