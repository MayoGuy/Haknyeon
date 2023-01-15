from disnake.ext import commands
import disnake as discord
from datetime import datetime
from db import Hanknyeon
import time
from views.binder import SelectPages
from views import ConfirmView, HelpView
from PIL import Image
from io import BytesIO


class Utility(commands.Cog):
    def __init__(self, bot:Hanknyeon):
        self.bot = bot


    async def cog_slash_command_check(self, inter: discord.ApplicationCommandInteraction):
        r = await self.bot.get_profile(inter.author.id)
        if not r:
            raise commands.CheckFailure("first")
        else:
            return True


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
            emb.set_image(file=discord.File("pics/" + r["fav_card"]+ ".png", "image.png"))
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
            return [id for id in ids] 
            

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
    async def setup(self, inter: discord.ApplicationCommandInteraction):
        await inter.response.defer()
        r = await self.bot.get_inventory(inter.author.id)
        bids = await self.bot.binder(inter.author.id, get=True)
        if not bids:
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
                    await self.bot.binder(inter.author.id, n=True)
            else:
                return await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_X:1035085573104345098> You need at least **5000** {self.bot.petal} to buy a binder!", color=self.bot.get_color()))
        ids = [str(card[0].split(" ")[0]) for card in r]
        v = SelectPages(ids)
        v.inter = inter
        await inter.edit_original_message(embed=discord.Embed(title="Binder Creation", description=f"**Selected Cards:**", color=self.bot.get_color()), view=v)
        await v.wait()
        if v.value:
            await self.bot.binder(inter.author.id, v.selected_ids)


    @binder.sub_command(description="Shows your binder")
    async def show(self, inter: discord.ApplicationCommandInteraction):
        await inter.response.defer()
        bids = await self.bot.binder(inter.author.id, get=True)
        if not bids:
            return await inter.send("You don't have a binder!", ephemeral=True)
        if bids[1] == "n":
            return await inter.send("You haven't set up your binder yet! use `/binder create` to set it up.", ephemeral=True)
        ids = bids[1].split(" ")
        inv = await self.bot.get_inventory(inter.author.id)
        invl = [a[0].split(" ")[0] for a in inv]
        if any(l not in invl for l in ids):
            await inter.send("One of the cards in your binder is not available in your inventory. Please recreate the binder to continue!", ephemeral=True)
            return
        r = await self.bot.loop.run_in_executor(None, self.create, ids[0]+".png", ids[1]+".png", ids[2]+".png", ids[3]+".png", ids[4]+".png")
        file = discord.File(r, "image.png")
        emb = discord.Embed(color=self.bot.get_color())
        emb.set_author(name=f"{inter.author}'s custom binder", icon_url=inter.author.avatar.url)
        emb.set_image(file=file)
        await inter.edit_original_message(embed=emb)

    
    def create(self, q, w, e, r, t):
        i1 = Image.open(f"pics/{q}").convert("RGBA")
        i2 = Image.open(f"pics/{w}").convert("RGBA")
        i3 = Image.open(f"pics/{e}").convert("RGBA")
        i4 = Image.open(f"pics/{r}").convert("RGBA")
        i5 = Image.open(f"pics/{t}").convert("RGBA")
        img = Image.new("RGBA", (2460, 2210), (0, 0, 0, 0))
        img.paste(i1, (0, 0), i1)
        img.paste(i2, (820, 0), i2)
        img.paste(i3, (1640, 0), i3)
        img.paste(i4, (410, 1110), i4)
        img.paste(i5, (1230, 1110), i5)
        i1.close()
        i2.close()
        i3.close()
        i4.close()
        i5.close()
        del i1
        del i2
        del i3
        del i4
        del i5
        buff = BytesIO()
        img.save(buff, "png")
        buff.seek(0)
        return buff


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
        emb = discord.Embed(title="Haknyeon Help", description="**Haknyeon** is a __K-pop__ card collecting game bot 𓆩♡𓆪 __dedicated__ to THE BOYZ's **Juhaknyeon**.\n\n**Click on any button below to get help for respective category**", color=self.bot.get_color())
        await inter.send(embed=emb, view=v)


def setup(bot):
    bot.add_cog(Utility(bot))