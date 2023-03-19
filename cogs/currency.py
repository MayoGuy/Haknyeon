from disnake.ext import commands, tasks
import disnake as discord
from db import Hanknyeon
from datetime import datetime, timedelta
import random
from views import Menu, ConfirmView
import traceback


class Currency(commands.Cog):
    def __init__(self, bot: Hanknyeon) -> None:
        super().__init__()
        self.bot = bot
        self.check_boosts.start()
        self.prices = {
            1:3000, 2:4500, 3:6000, 4:8500, 5:10000
        }

    
    async def cog_slash_command_check(self, inter: discord.ApplicationCommandInteraction) -> bool:
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


    @commands.slash_command(description="Claim your daily petals!")
    async def daily(self, inter: discord.ApplicationCommandInteraction):
        await inter.response.defer()
        r1 = await self.bot.get_profile(inter.author.id)
        r = [r1["daily_dt"], r1["daily_streak"], r1["coins"]] #type:ignore
        today = datetime.now().timestamp()
        if today - r[0] > 86400:
            if today - r[0] > 172800:
                streak = 1
            else:
                streak = r[1] + 1
            add = ""
            if streak:
                if not streak%20:
                    add = f"\n\nYou got a Mega Package! Use `/powerups use` to open it. \nNext Normal Package at {streak+10} days streak"
                    await self.bot.add_boosts(inter.author.id, "mp")
                elif not streak%10:
                    add = f"\n\nYou got a Normal Package! Use `/powerups use` to open it. \nNext Mega Package at {streak+10} days streak"
                    await self.bot.add_boosts(inter.author.id, "mp")
            cs = await self.bot.daily(inter.author.id, set=True, streak=streak-1)
            emb = discord.Embed(title="Daily Petals Claimed!", description=f"**<:HN_Gift:1034881304052899850> Petals Claimed: **{cs} {self.bot.petal}\n**<:HN_Butterfly2:1034884649912127619> Total Petals: **{format(r[2] + cs, ',')} {self.bot.petal}\n**<:HN_Butterfly:1034882795547394179> Daily Streak: **{streak}{add}\n\nCome back tomorrow to claim more petals!", color=self.bot.get_color())
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            await inter.edit_original_message(embed=emb)
        else:
            await inter.edit_original_message(f"You need to wait {self.bot.sort_time(86400-(today-r[0]))} before claiming your daily petals!")


    @commands.slash_command(description="Shows the amount of petals a user owns.")
    async def balance(self, inter, user:discord.Member=None):  #type:ignore
        user = user if user else inter.author
        r = await self.bot.get_profile(user.id)
        c = await self.bot.get_inventory(user.id)
        coins = format(r["coins"], ",")  #type:ignore
        emb = discord.Embed(title=f"{user.display_name}'s balance", description=f"**<:HN_Butterfly2:1034884649912127619> Petals: **{coins} {self.bot.petal}\n**<:HN_Butterfly:1034882795547394179>Cards: **{len(c)}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @commands.slash_command()
    async def shop(self, inter):
        pass


    @shop.sub_command(name="cards", description="Hanknyeon's card marketplace!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def card_(self, inter, group=None, rarity:commands.Range[1, 5]=None): #type:ignore
        ids = []
        if group:
            for id in self.bot.data.keys():
                if self.bot.data[id]["group"] == group:
                    ids.append(id)
        if not group:
            for id in self.bot.data.keys():
                ids.append(id)
        if rarity:
            _ids = []
            for id in ids:
                if self.bot.data[id]["rarity"] == rarity:
                    _ids.append(id)
            ids = _ids
        embeds = []
        desc = "<a:HN_Boun:1035119052919685210> **__Here are the listed prices of the cards:__**. <a:HN_Boun:1035119052919685210>\n\n"
        for i in range(0, len(ids), 5):
            emb = discord.Embed(title="The Haknyeon Cards Market", color=self.bot.get_color())
            nl = ids[i:i+5]
            for id in nl:
                data = self.bot.data[id] #type:ignore
                price = format(self.prices[data['rarity']], ',') if not "Special" in data["group"] else "Not Available"
                if "Limited" in data["group"]:
                    price = "Not Available"
                elif data["rarity"] == 5:
                    price = "Not Available"
                desc += f"{data['group']} **{data['name']}**\n**Card ID: **{id}\n**Rarity: **{self.bot.rare[data['rarity']]}\n**Price: **{price}\n\n" #type:ignore
            emb.description = desc
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            desc = "<a:HN_Boun:1035119052919685210> **__Here are the listed prices of the cards:__** <a:HN_Boun:1035119052919685210>.\n\n"
            embeds.append(emb)
        view = Menu(embeds)
        view.inter = inter  #type:ignore
        await inter.send(embed=embeds[0], view=view)


    @shop.sub_command(description="Cards buying and selling prices", guild_ids=[1024399481782927511, 1024402764601765978])
    async def prices(self, inter):
        buyprices = "\n".join(f"{self.bot.rare[i+1]}: {format(str(self.prices[i+1]), ',')}" for i in range(5))
        sellprices = "\n".join(f"{self.bot.rare[i+1]}: {format(str(self.prices[i+1])[:-1], ',')}" for i in range(5))
        emb = discord.Embed(title="Marketplace buying and selling prices", description=f"**__Buying Prices__**:\n{buyprices}\n\n**__Selling Prices__**:\n{sellprices}", color=self.bot.get_color())
        await inter.send(emb)


    @shop.sub_command(name="powerups", description="A marketplace for items to boost up your claiming Experience")
    async def _powerups(self, inter):
        emb = discord.Embed(title="Powerups Marketplace", description=f"<a:HN_Boun:1035119052919685210> **__Here are the listed prices of the powerups:__**. <a:HN_Boun:1035119052919685210>\n\n**1. Normal Pack**\nGives 3 random cards! Can only be bought once per day.\n**Price: **7,000 {self.bot.petal}\n\n**2. Mega Pack**\nGives 5 random cards with a guaranteed 5 rarity card. Can only be bought once per week.\n**Price: **20,000 {self.bot.petal}\n\n**3. Small Boost**\nBoosts your chances of dropping rare cards by 30% for 1 hour. Can only be bought once per day.\n**Price: **7,000 {self.bot.petal}\n\n**4. Normal Boost**\nBoosts your chances of dropping rare cards by 50% for 1 hour. Can only be bought once per week.\n**Price: **13,000 {self.bot.petal}\n\n**4. Mega Boost**\nBoosts your chances of dropping rare cards by 70% for 1 hour. Can only be bought once per two weeks.\n**Price: **20,000 {self.bot.petal}\n\n", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)  


    @card_.autocomplete("group")
    async def shopgroup(self, inter, input):
        groups = []
        for id in self.bot.data.keys():
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [gr for gr in groups if input.lower() in gr.lower() or input==""][:24]


    @commands.slash_command(description="Buy a card with your petals!")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def buy(self, inter, card_id):
        id = card_id
        v = ConfirmView()
        v.inter = inter #type:ignore
        dt = self.bot.data[id]
        if "Special" in dt["group"] or "Limited" in dt["group"]:
            return await inter.send("You cannot buy this card!", ephemeral=True)
        elif dt["rarity"] == 5:
            return await inter.send("You cannot buy cards of rarity 5!", ephemeral=True)
        price = self.prices[dt['rarity']]
        emb = discord.Embed(title="Are you sure you want to buy this card?", description=f"{dt['group']} **{dt['name']}**\n**Card ID: **{id}\n{self.bot.rare[dt['rarity']]}\n**Price: **{format(price, ',')}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        emb.set_image(url=f"https://haknyeon.info/topsecret/card?id={id.replace('#', 'h')}")
        await inter.send(embed=emb, view=v)
        await v.wait()
        if v.value == False:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this transaction!", color=self.bot.get_color()), view=None, attachments=[])
        elif v.value == True:
            prf = await self.bot.get_profile(inter.author.id)
            coins = prf["coins"]  #type:ignore
            if coins < price:
                return await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You don't have enough coins to buy this card!", color=self.bot.get_color()), view=None, attachments=[])
            await self.bot.remove_coins(inter.author.id, price)
            await self.bot.insert_card(inter.author.id, id)
            await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_Checkmark:1035085306346606602> You successfully bought the card! (ID: {id})", color=self.bot.get_color()), view=None, attachments=[])


    @buy.autocomplete("card_id")
    async def buyid(self, inter, input):
        return [id for id in self.bot.data.keys() if (input.lower() in id.lower() or input=="") and "Special" not in self.bot.data[id]["group"]][:24]


    @commands.slash_command(description="Sell your cards for some petals!")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def sell(self, inter, card_id):
        id = card_id
        v = ConfirmView()
        v.inter = inter  #type:ignore
        dt = self.bot.data[id]
        price = int(str(self.prices[dt['rarity']])[:-1])
        emb = discord.Embed(title="Are you sure you want to sell this card?", description=f"{dt['group']} **{dt['name']}**\n**Card ID: **{id}\n{self.bot.rare[dt['rarity']]}\n**Selling Price: **{format(price, ',')}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        emb.set_image(url=f"https://haknyeon.info/topsecret/card?id={id.replace('#', 'h')}")
        await inter.send(embed=emb, view=v)
        await v.wait()
        if v.value == False:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this transaction!", color=self.bot.get_color()), view=None, attachments=[])
        elif v.value == True:
            await self.bot.add_coins(inter.author.id, price)
            await self.bot.remove_cards(inter.author.id, id)
            await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_Checkmark:1035085306346606602> You successfully sold the card! (ID: {id})", color=self.bot.get_color()), view=None, attachments=[])


    @sell.autocomplete("card_id")
    async def getidfav(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id, limit=input.upper())
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower() or input==""][:24] 


    @commands.slash_command(description="Do a task every 2 hours to earn some petals!")
    @commands.cooldown(1, 7200, commands.BucketType.user)
    async def task(self, inter: discord.ApplicationCommandInteraction):
        pro = await self.bot.get_profile(inter.author.id)
        fav_card = pro["fav_card"]
        if fav_card == " ":
            return await inter.send("You need to set a favourite card to do your tasks with!", ephemeral=True)
        prompts = {
            125: f"{self.bot.petal} You went to water your flowers in your garden and gained +125 petals!",
            250: f"{self.bot.petal} You and **{fav_card}** went to the forest to help collect some mushrooms! Mom gave you 250+ petals for your help.",
            375: f"{self.bot.petal} You sold some flower on the market and received +375 petals!",
            500: f"{self.bot.petal} **{fav_card}** befriended a group of butterflies and was gifted +500 petals by them!\nHow nice~",
            750: f"{self.bot.petal} You and **{fav_card}** participated in a flower contest and won +750 petals!"
        }
        coins = random.choice(list(prompts.keys()))
        emb = discord.Embed(description=prompts[coins], color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)
        await self.bot.add_coins(inter.author.id, coins)


    @commands.slash_command()
    async def gift(self, inter):
        pass


    @gift.sub_command(description="Gift a card to your friend.")
    async def card(self, inter, user: discord.User, card_id:str):
        if card_id == "Nothing found":
            await inter.send("You don't have any card in your inventory.", ephemeral=True)
            return
        r = await self.bot.get_inventory(inter.author.id)
        copies = 0
        for card in r:
            if card[0].split(" ")[0] == card_id:
                copies = int(card[0].split(" ")[1])
                break
        if not copies:
            return await inter.send("You don't have that card in your inventory!", ephemeral=True)
        emb = discord.Embed(description=f"You've given {user.mention} a gift! <:HN_Gift:1034881304052899850>\n\n<:HN_Butterfly2:1034884649912127619> Given 1x {self.bot.data[card_id]['group']} **{self.bot.data[card_id]['name']}** | **{card_id}**\n{self.bot.rare[self.bot.data[card_id]['rarity']]}\n<:HN_Butterfly:1034882795547394179> **Copies left: **{copies-1}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)
        await self.bot.remove_cards(inter.author.id, card_id)
        await self.bot.insert_card(user.id, card_id)


    @gift.sub_command(description="Gift petals to your friend!")
    async def petals(self, inter, user:discord.User, amount:int):
        r = await self.bot.get_profile(inter.author.id)
        r2 = await self.bot.get_profile(user.id)
        if int(r["coins"]) < amount:
            return await inter.send(f"The gifting amount exceeds your current balance! ({format(r['coins'], ',')})")
        emb = discord.Embed(description=f"You've given {user.mention} {format(amount, ',')} {self.bot.petal}! <:HN_Gift:1034881304052899850>\n\n<:HN_Butterfly2:1034884649912127619> Current Balance: {format(int(r['coins']) - amount, ',')} {self.bot.petal}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)
        await self.bot.add_coins(user.id, amount)
        await self.bot.remove_coins(inter.author.id, amount)


    @card.autocomplete("card_id")
    async def getid(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id, limit=input.upper())
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower() or input==""][:24] 


    @tasks.loop(seconds=30)
    async def check_boosts(self):
        k = []
        for key, value in self.bot.curr_boosts.items():
            if value["start"] + timedelta(hours=1) < datetime.now():
                k.append(key)
                await self.bot.add_boosts(key, value["item"], remove=True)
        if k:
            for i in k:
                self.bot.curr_boosts.pop(i)


def setup(bot):
    bot.add_cog(Currency(bot))