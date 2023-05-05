import disnake as discord
from disnake.ext import commands
from db import Hanknyeon
import random
from datetime import datetime, timedelta
from views import ConfirmView
import traceback


class Powerups(commands.Cog):
    def __init__(self, bot:Hanknyeon) -> None:
        self.bot = bot


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

    
    @commands.slash_command()
    async def powerups(self, inter):
        pass


    @powerups.sub_command(description="Shows powerups in your inventory", guild_ids=[1024399481782927511, 1024402764601765978])
    async def show(self, inter):
        r = await self.bot.get_boosters(inter.author.id)
        d = {"np":"Normal Package", "mp":"Mega Package", "sb":"Small Boost", "nb":"Normal Boost", "mb":"Mega Boost"}
        if not r:
            emb = discord.Embed(description="Nothing found...", color=self.bot.get_color())
            return await inter.send(embed=emb)
        else:
            boosts = []
            for l in r:
                if l["user_id"] == inter.author.id and l['quantity'] > 0:
                    boosts.append(l)
            desc = ""
            i = 1
            for b in boosts:
                desc += f"**{i}. {d[b['item']]}**\n🍃 Quantity: {b['quantity']}\n\n"
                i += 1
            emb = discord.Embed(title="Your boosts inventory...", description=desc, color=self.bot.get_color())
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
            await inter.send(embed=emb)


    @powerups.sub_command(description="Use a powerup you own", guild_ids=[1024399481782927511, 1024402764601765978])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def use(self, inter, item:str=commands.Param(choices=["Normal Package", "Mega Package", "Small Boost", "Normal Boost", "Mega Boost"])):
        r = await self.bot.get_boosters(inter.author.id)
        d = {"Normal Package":"np", "Mega Package":"mp", "Small Boost":"sb", "Normal Boost":"nb", "Mega Boost":"mb"}
        avail = False
        for l in r:
            if l['item'] == d[item]:
                avail = l
        if not avail:
            return await inter.send(f"You don't own any {item}s!", ephemeral=True)
        if avail['quantity'] <= 0:
            return await inter.send(f"You don't own any {item}s!", ephemeral=True)
        if item in ("Small Boost", "Normal Boost", "Mega Boost") and inter.author.id in list(self.bot.curr_boosts.keys()):
            return await inter.send("You already have a boost running! See `/powerups current` for more info.", ephemeral=True)
        else:
            await inter.response.defer()
            boost = None
            match item:
                case "Normal Package":
                    droppable = []
                    for dr in self.bot.data.keys():
                        if dr not in self.bot.deleted:
                            droppable.append(dr)
                    cards = []
                    for i in range(3):
                        c_lis = []
                        for ca in droppable:
                            if self.bot.data[ca]["rarity"]==5:
                                ri = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
                                if ri == 3:
                                    c_lis.append(ca)
                            else:
                                c_lis.append(ca)
                        c = random.choice(c_lis)
                        cards.append(c)
                        await self.bot.insert_card(inter.author.id, c)
                    q, w, e = cards
                    buff = await self.bot.loop.run_in_executor(None, self.bot.create, q + ".png", w + ".png", e + ".png")
                    emb = discord.Embed(title="You opened a Normal Package and got:", color=self.bot.get_color())
                    f = discord.File(buff, "image.png")
                    emb.set_image(file=f)
                    await self.bot.edit_booster(inter.author.id, "np", remove=True)
                    return await inter.edit_original_message(embed=emb)
                case "Mega Package":
                    droppable = []
                    for dr in self.bot.data.keys():
                        if dr not in self.bot.deleted:
                            droppable.append(dr)
                    ids = []
                    for i in range(4):
                        c = random.choice([k for k in droppable if self.bot.data[k]['rarity']!=5 and "Special" not in self.bot.data[k]["group"]])
                        ids.append(c)
                        await self.bot.insert_card(inter.author.id, c)
                    r5 = [k for k in droppable if self.bot.data[k]['rarity']==5 and "Special" not in self.bot.data[k]["group"]]
                    c5 = random.choice(r5)
                    await self.bot.insert_card(inter.author.id, c5)
                    ids.append(c5)
                    buff = await self.bot.loop.run_in_executor(None, self.bot.create_b, ids[0]+".png", ids[1]+".png", ids[2]+".png", ids[3]+".png", ids[4]+".png")
                    emb = discord.Embed(title="You opened a Mega Package and got:", color=self.bot.get_color())
                    f = discord.File(buff, "image.png")
                    emb.set_image(file=f)
                    await self.bot.edit_booster(inter.author.id, "mp", remove=True)
                    return await inter.edit_original_message(embed=emb)
                case "Small Boost":
                    emb = discord.Embed(title="You used a Small Boost!", description=f"You now have a 30% chance of dropping rare cards for 1 hour!\n**Remaining Small Boosts: **{avail['quantity']-1}", color=self.bot.get_color())
                    await inter.send(embed=emb)
                    await self.bot.add_boosts(inter.author.id, "sb")
                    await self.bot.edit_booster(inter.author.id, "sb", remove=True)
                case "Normal Boost":
                    emb = discord.Embed(title="You used a Normal Boost!", description=f"You now have a 50% chance of dropping rare cards for 1 hour!\n**Remaining Normal Boosts: **{avail['quantity']-1}", color=self.bot.get_color())
                    await inter.send(embed=emb)
                    await self.bot.add_boosts(inter.author.id, "nb")
                    await self.bot.edit_booster(inter.author.id, "nb", remove=True)
                case "Mega Boost":
                    emb = discord.Embed(title="You used a Mega Boost!", description=f"You now have a 70% chance of dropping rare cards for 1 hour!\n**Remaining Mega Boosts: **{avail['quantity']-1}", color=self.bot.get_color())
                    await inter.send(embed=emb)
                    await self.bot.add_boosts(inter.author.id, "mb")
                    await self.bot.edit_booster(inter.author.id, "mb", remove=True)
            
                
    
    @powerups.sub_command(name="buy", description="Buy a powerup.", guild_ids=[1024399481782927511, 1024402764601765978])
    async def _buy(self, inter:discord.ApplicationCommandInteraction, item:str=commands.Param(choices={"Normal Package":"np", "Mega Package":"mp", "Small Boost":"sb", "Normal Boost":"nb", "Mega Boost":"mb"})):
        b = await self.bot.get_boosters(inter.author.id)
        dap = {"np":1, "mp":7, "sb":1, "nb":7, "mb":14}
        d = {"np":"Normal Package", "mp":"Mega Package", "sb":"Small Boost", "nb":"Normal Boost", "mb":"Mega Boost"}
        rl = None
        for l in b:
            if l['item'] == item:
                rl = l
        if rl:
            if rl["bought"]:
                if datetime.now() < l["bought"] + timedelta(days=dap[l["item"]]):
                    remain = l["bought"] + timedelta(days=dap[l["item"]]) - datetime.now()
                    remain_sec = remain.total_seconds()
                    return await inter.send(f"You need to wait {self.bot.sort_time(int(remain_sec))} before buying a {d[item]}!", ephemeral=True)
        await inter.response.defer()
        dp = {"np":7000, "mp":20000, "sb":7000, "nb":13000, "mb":20000}
        r = await self.bot.get_profile(inter.author.id)
        if r['coins'] < dp[item]:
                return await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_X:1035085573104345098> You need atleast {dp[item]} {self.bot.petal} to buy a {d[item]}!", color=self.bot.get_color()), view=None, attachments=[])
        emb = discord.Embed(description=f"Are you sure you want to buy a {d[item]} for {format(dp[item], ',')} {self.bot.petal}", color=self.bot.get_color())
        v = ConfirmView()
        v.inter = inter
        await inter.edit_original_message(embed=emb, view=v)
        await v.wait()
        if v.value == False:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this transaction!", color=self.bot.get_color()), view=None, attachments=[])
        elif v.value == True:
            await self.bot.remove_coins(inter.author.id, dp[item])
            await self.bot.edit_booster(inter.author.id, item)
            if rl:
                qu = rl['quantity']
            else:
                qu = 1
            await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_Checkmark:1035085306346606602> You successfully bought a {d[item]}. You now have {qu} {d[item]}(s)", color=self.bot.get_color()), view=None, attachments=[])


    @powerups.sub_command(description="Shows your current active boosts")
    async def current(self, inter):
        v = None    
        for key, value in self.bot.curr_boosts.items():
            if key == inter.author.id:
                v = value
        if v:
            d = {"np":"Normal Package", "mp":"Mega Package", "sb":"Small Boost", "nb":"Normal Boost", "mb":"Mega Boost"}
            ti = v["start"] + timedelta(hours=1) - datetime.now()
            emb = discord.Embed(title="Current Power Up:", description=f"**{d[v['item']]}**\nTime remaining: {self.bot.sort_time(int(ti.total_seconds()))}", color=self.bot.get_color())
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            await inter.send(embed=emb)
        else:
            emb = discord.Embed(description="You dont have any active boosts...", color=self.bot.get_color())
            await inter.send(embed=emb)


    @powerups.sub_command(name="shop", description="A marketplace for items to boost up your claiming Experience")
    async def _powerups(self, inter):
        emb = discord.Embed(title="Powerups Marketplace", description=f"<a:HN_Boun:1035119052919685210> **__Here are the listed prices of the powerups:__**. <a:HN_Boun:1035119052919685210>\n\n**1. Normal Pack**\nGives 3 random cards! Can only be bought once per day.\n**Price: **7,000 {self.bot.petal}\n\n**2. Mega Pack**\nGives 5 random cards with a guaranteed 5 rarity card. Can only be bought once per week.\n**Price: **20,000 {self.bot.petal}\n\n**3. Small Boost**\nBoosts your chances of dropping rare cards by 30% for 1 hour. Can only be bought once per day.\n**Price: **7,000 {self.bot.petal}\n\n**4. Normal Boost**\nBoosts your chances of dropping rare cards by 50% for 1 hour. Can only be bought once per week.\n**Price: **13,000 {self.bot.petal}\n\n**4. Mega Boost**\nBoosts your chances of dropping rare cards by 70% for 1 hour. Can only be bought once per two weeks.\n**Price: **20,000 {self.bot.petal}\n\n", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)


def setup(bot:Hanknyeon):
    bot.add_cog(Powerups(bot))