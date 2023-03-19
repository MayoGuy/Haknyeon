from disnake.ext import commands
import disnake as discord
from datetime import datetime
from db import Hanknyeon
import time
from views.binder import SelectPages
from views import ConfirmView, HelpView
import traceback


class Utility(commands.Cog):
    def __init__(self, bot:Hanknyeon):
        self.bot = bot


    async def cog_slash_command_check(self, inter: discord.ApplicationCommandInteraction):
        r = await self.bot.get_profile(inter.author.id)
        if not r:
            raise commands.CheckFailure("first")
        else:
            return True


    async def cog_command_error(self, inter: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            time = error.cooldown.get_retry_after()
            embed = discord.Embed(title="This command is on cooldown", description=f"Try using this command after {self.bot.sort_time(int(time))}.", color=discord.Color.red())
            embed.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            await inter.send(embed=embed)
        else:
            etype = type(error)
            trace = error.__traceback__
            lines = traceback.format_exception(etype, error, trace)
            traceback_text = ''.join(lines)
            ch = self.bot.get_channel(1085272060986654831)
            await ch.send(f"```py\n{traceback_text}\n```")
            wee_embed = discord.Embed(title="We ran into an unexpected error...", description="If this problem persists, report this on our [support server](https://discord.gg/haknyeon/)", color=self.bot.get_color())
            try:
                await inter.reponse.send_message(embed=wee_embed)
            except:
                await inter.followup.send(embed=wee_embed)



    @commands.slash_command(description="Shows profile")
    async def profile(self, inter, user:discord.User=None):  #type:ignore
        use = user if user else inter.author
        r = await self.bot.get_profile(use.id)
        if not r:
            if not use:
                return await inter.send("You are using the bot for the first time! Try the command again to continue...", ephemeral=True)
            else:
                return await inter.send(f"{use.mention} does not have any profile yet!", ephemeral=True)
        emb=discord.Embed(title=f"{use.display_name}'s Profile...", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        emb.set_author(name=use.name, icon_url=use.avatar.url)  #type:ignore
        emb.add_field(name="Started Playing", value=discord.utils.format_dt(datetime.fromtimestamp(r["startdate"])))
        emb.add_field(name="Petals", value=format(r["coins"], ",")  + " " + self.bot.petal)
        emb.add_field(name="Daily Streak", value=str(r["daily_streak"]+1)+" days")
        c = await self.bot.get_inventory(use.id)
        emb.add_field(name="Total Cards", value=len(c))
        if r["fav_card"] != " " and r["fav_card"] in list(self.bot.data.keys()):
            emb.add_field(name="Favourite Card", value="\u200b", inline=False)
            emb.set_image(url=f"https://haknyeon.info/topsecret/card?id={r['fav_card'].replace('#', 'h')}")
        else:
            emb.add_field(name="Favourite Card", value="No favourite card has been set.", inline=False)
        await inter.send(embed=emb)


    @commands.slash_command()
    async def favourite(self, inter):
        pass


    @favourite.sub_command(description="Sets a favourite card in your profile")
    async def set(self, inter, card_id:str):
        await self.bot.insert_fav(inter.author.id, card_id)
        emb = discord.Embed(description=f"<:HN_Butterfly:1034882795547394179> Your favourite card has been successfully set! (ID: {card_id})", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @set.autocomplete("card_id")
    async def getidfav(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id, limit=input.upper())
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids][:25]
            

    @commands.slash_command(description="Shows bot's latency")
    async def ping(self, inter):
        start = time.perf_counter()
        await inter.send("Ping...")
        end = time.perf_counter()
        duration = (end - start) * 1000
        await inter.edit_original_message(content='Pong! {:.2f}ms'.format(duration))


    @commands.slash_command()
    async def binder(self, inter):
        pass

        
    @binder.sub_command(description="Combine your 5 favourite cards into a binder!")
    async def new(self, inter, name:str):
        await inter.response.defer()
        r = await self.bot.get_inventory(inter.author.id)
        p = await self.bot.get_profile(inter.author.id)
        if p["coins"] > 5000:
            emb = discord.Embed(description=f"Are you sure you want to buy a binder for **5000** {self.bot.petal}?", color=self.bot.get_color())
            v = ConfirmView()
            v.inter = inter
            await inter.edit_original_message(embed=emb, view=v)
            await v.wait()
            if v.value == False:
                return await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this transaction!", color=self.bot.get_color()), view=None, attachments=[])
            else:
                await self.bot.remove_coins(inter.author.id, 5000)
                await self.bot.binder(inter.author.id, n=True, name=name)
        else:
            return await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_X:1035085573104345098> You need at least **5000** {self.bot.petal} to buy a binder!", color=self.bot.get_color()))
        ids = [str(card[0].split(" ")[0]) for card in r]
        v = SelectPages(ids)
        v.inter = inter
        emb = discord.Embed(title="Binder Creation", description=f"**Selected Cards:**", color=self.bot.get_color())
        emb.set_footer(text="Use the buttons below to go through other cards. 25 at a time.")
        await inter.edit_original_message(embed=emb, view=v)
        await v.wait()
        if v.value:
            await self.bot.binder(inter.author.id, v.selected_ids, name=name)

    
    @binder.sub_command(description="Edit cards in one your binders!")
    async def edit(self, inter, binder, name:str=None):
        await inter.response.defer()
        if not name:
            name = binder
        bid = await self.bot.binder(inter.author.id, get=True)
        for b in bid:
            if b["name"] == binder:
                bids=b
        if bids["card"]=="n":
            idst = " "
            idt = []
        else:
            idst = bids["card"].split(" ")
            idst = "\n".join(id for id in idst)
            idt = bids["card"].split(" ")
        r = await self.bot.get_inventory(inter.author.id)
        ids = [str(card[0].split(" ")[0]) for card in r]
        v = SelectPages(ids, edit=True)
        v.inter = inter
        v.selected_ids = idt
        emb = discord.Embed(title="Binder Creation", description=f"**Selected Cards:**\n\n{idst}", color=self.bot.get_color())
        emb.set_footer(text="Use the buttons below to go through other cards. 25 at a time.")
        await inter.edit_original_message(embed=emb, view=v)
        await v.wait()
        if v.value:
            conn = await self.bot.curr.acquire()
            async with conn.transaction():
                await self.bot.curr.execute("UPDATE binder SET card=$1, name=$2 WHERE user_id=$3 AND name=$4", " ".join(v.selected_ids), name, inter.author.id, binder)
            await self.bot.curr.release(conn)


    @binder.sub_command(description="Shows your binder")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def show(self, inter: discord.ApplicationCommandInteraction, binder:str):
        if binder=="You don't have any binder!":
            return await inter.send("You don't have any binder!", ephemeral=True)
        await inter.response.defer()
        bid = await self.bot.binder(inter.author.id, get=True)
        for b in bid:
            if b["name"] == binder:
                bids=b
        if bids[1] == "n":
            return await inter.send("You haven't set up this binder yet! use `/binder create` to set it up.", ephemeral=True)
        ids = bids[1].split(" ")
        inv = await self.bot.get_inventory(inter.author.id)
        invl = [a[0].split(" ")[0] for a in inv]
        if any(l not in invl for l in ids):
            await inter.send("One of the cards in your binder is not available in your inventory. Please recreate the binder to continue!", ephemeral=True)
            return
        r = await self.bot.loop.run_in_executor(None, self.bot.create_b, ids[0]+".png", ids[1]+".png", ids[2]+".png", ids[3]+".png", ids[4]+".png")
        file = discord.File(r, "image.png")
        emb = discord.Embed(color=self.bot.get_color())
        emb.set_author(name=f"{inter.author}'s custom binder", icon_url=inter.author.avatar.url)
        emb.set_image(file=file)
        await inter.edit_original_message(embed=emb)
        del emb
        file.close()
        r.close()
        del r


    @show.autocomplete("binder")
    async def show_auto(self, inter, input):
        bids = await self.bot.binder(inter.author.id, get=True)
        if not bids:
            return ["You don't have any binder!"]
        names = []
        for b in bids:
            names.append(b["name"])
        return [n for n in names if input.lower() in n.lower()]
    

    @edit.autocomplete("binder")
    async def edit_auto(self, inter, input):
        bids = await self.bot.binder(inter.author.id, get=True)
        if not bids:
            return ["You don't have any binder!"]
        names = []
        for b in bids:
            names.append(b["name"])
        return [n for n in names if input.lower() in n.lower()]


    @commands.slash_command(description="Chat with haknyeon in a channel of your choice!", dm_permission=False)
    @commands.default_member_permissions(manage_guild=True, administrator=True)
    async def set_chat_channel(self, inter, channel:discord.TextChannel):
        emb = discord.Embed(title="Success!", description=f"Haknyeon chat channel has been successfully set to {channel.mention}!", timestamp=datetime.utcnow(), color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)
        await self.bot.chat(channel)


    @commands.slash_command(description="A guide to Haknyeon!")
    async def help(self, inter):
        v = HelpView(self.bot)
        emb = discord.Embed(title="Haknyeon Help", description="**Haknyeon** is a __K-pop__ card collecting game bot 𓆩♡𓆪 __dedicated__ to THE BOYZ's **Juhaknyeon**.\n\n**Select an option from dropdown menu to get help for respective category**", color=self.bot.get_color())
        await inter.send(embed=emb, view=v)


    @commands.slash_command(description="Vote for Haknyeon to get awesome prices!")
    async def vote(self, inter):
        r = await self.bot.curr.fetchrow("SELECT datee, claim FROM votes WHERE user_id=$1", inter.author.id)
        if not r:
            emb = discord.Embed(title="You have not voted for Haknyeon Yet!", description=f"Press the button to vote for Haknyeon. Use `/vote` once you have voted!\n\nBy voting, you get:\n- 200 {self.bot.petal}\n- 5 minutes `/drop` cooldown for 40 minutes.\n- No claim cooldown for 40 minutes.", color=self.bot.get_color())
            b = discord.ui.Button(label="Vote on Top.gg", url="https://top.gg/bot/1024387091834077256/vote")
            v = discord.ui.View()
            v.add_item(b)
            return await inter.send(embed=emb, view=v)
        else:
            if r[1]:
                await self.bot.vote(inter.author.id, claim=False)
                self.bot.voted[inter.author.id] = datetime.utcnow().timestamp()
                await self.bot.add_coins(inter.author.id, 200)
                emb = discord.Embed(title="Thanks for voting Haknyeon!", description=f"You have been given the following perks:\n\n- 200 {self.bot.petal}\n- 5 minutes `/drop` cooldown for 40 minutes.\n- No claim cooldown for 40 minutes.", color=self.bot.get_color())
                return await inter.send(embed=emb)
            else:    
                if int(datetime.utcnow().timestamp()) - r[0] > 43200:
                    emb = discord.Embed(title="You have a vote available!", description="Press the button to vote for Haknyeon. Use `/vote` once you have voted!", color=self.bot.get_color())
                    b = discord.ui.Button(label="Vote on Top.gg", url="https://top.gg/bot/1024387091834077256/vote")
                    v = discord.ui.View()
                    v.add_item(b)
                    return await inter.send(embed=emb, view=v)
                else:
                    print(43200-int(datetime.utcnow().timestamp())-r[0])
                    emb = discord.Embed(title="You can't vote for Haknyeon right now!", description=f"Come back again in {self.bot.sort_time(43200-(int(datetime.utcnow().timestamp())-r[0]))}", color=self.bot.get_color())
                    return await inter.send(embed=emb)


def setup(bot):
    bot.add_cog(Utility(bot))