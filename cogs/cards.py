from disnake.ext import commands
import disnake as discord
from db import Hanknyeon
from views import CardsView, Menu
import random
from PIL import Image
import time
from io import BytesIO
import os
from datetime import datetime


class Cards(commands.Cog):
    def __init__(self, bot: Hanknyeon) -> None:
        super().__init__()
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
            raise error


    @commands.slash_command(description="Drops card")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def drop(self, inter: discord.ApplicationCommandInteraction):
        data = self.bot.data
        await inter.response.defer()
        piclis = []
        for _ids in self.bot.data.keys():
            if _ids not in self.bot.deleted:
                piclis.append(_ids)
        r1 = [id for id in piclis if data[id]["rarity"]==1]
        r2 = [id for id in piclis if data[id]["rarity"]==2]
        r3 = [id for id in piclis if data[id]["rarity"]==3]
        r4 = [id for id in piclis if data[id]["rarity"]==4]
        r5 = [id for id in piclis if data[id]["rarity"]==5]
        while True:
            q, w, e = random.sample(r1+r2+r3+r4+r5, 3)
            if q != w and w != e and e != q:
                break
        buff = await self.bot.loop.run_in_executor(None, self.create, q + ".png", w + ".png", e + ".png")
        q, w, e = q, w, e
        emb = discord.Embed(
            description=f"{inter.author.mention} is dropping a set of 3 cards!",
            color=self.bot.get_color())
        file = discord.File(buff, filename="image.png")
        emb.set_image(file=file)
        rarities = []
        names = []
        for i in (q, w, e):
            rarities.append(data[i]["rarity"])
            names.append(f"{data[i]['group']} {data[i]['name']}")
        view = CardsView(rarities, names, (q, w, e))
        view.inter = inter #type:ignore
        view.bot = self.bot #type:ignore
        view.emb = emb
        view.buff = await self.bot.loop.run_in_executor(None, self.create, q + ".png", w + ".png", e + ".png")
        await inter.edit_original_message(
            embed=emb,
            view=view,
        )
        file.close()
        buff.close()
        del buff
        del emb


    def create(self, q, w, e):
        img = img = Image.new("RGBA", (2460, 1100), (0, 0, 0, 0))
        x = 0
        for i in (q, w, e):
            with Image.open(f"pics/{i}") as im:
                im = im.convert("RGBA")
                img.paste(im, (x, 0), im)
                x += 820
        buff = BytesIO()
        img.save(buff, "png")
        buff.seek(0)
        img.close()
        del img
        return buff


    @commands.slash_command(description="Shows Inventory")
    async def inventory(self, inter, user: discord.User = None, group=None): #type:ignore
        data = self.bot.data
        user = user if user else inter.author
        r = await self.bot.get_inventory(user.id)
        cards = []
        if group:
            for c in r:
                if data[c[0].split(" ")[0]]["group"] == group:
                    cards.append(c)
        else:
            cards = r
        if not cards:
            await inter.send(embed=discord.Embed(description="Nothing found...", color=self.bot.get_color()))
            return
        if len(cards) <= 5:
            emb = discord.Embed(title=f"{user.display_name}'s Inventory...",
                                color=self.bot.get_color())
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            num = 1
            desc = ""
            checked = []
            for card in cards:
                if not card[0] in checked:
                    lq = card[0]
                    sp = card[0].split(" ")
                    card = sp[0]
                    if len(sp) == 2:
                        q = sp[1]
                    else:
                        q = 1
                    checked.append(card[0])
                    try:
                        rari = self.bot.rare[data[card]["rarity"]]
                    except:
                        continue
                    desc += f"**{num}. {data[card]['name']}**\n**🌸 Group**: {data[card]['group']}\n🍃 **Copies**: {q}\n🌼 **Card ID**: {card}\n({rari})\n\n"
                    num += 1
            emb.description = desc
            emb.set_footer(text="Page 1 of 1")
            await inter.response.send_message(embed=emb)
        elif len(cards) > 5:
            await inter.response.defer()
            embeds = []
            num = 1
            total, left_over = divmod(len(cards), 5)
            pages = total + 1 if left_over else total
            desc = ""
            mnum = 0
            for page in range(pages):
                for card in cards:
                    lq = card[0]
                    sp = card[0].split(" ")
                    card = sp[0]
                    if len(sp) == 2:
                        q = sp[1]
                    else:
                        q = 1
                    try:
                        rari = self.bot.rare[data[card]["rarity"]]
                    except:
                        continue
                    emb = discord.Embed(
                        title=f"{user.display_name}'s Inventory...", color=self.bot.get_color())
                    emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
                    rari = self.bot.rare[data[card]["rarity"]]
                    desc += f"**{num}. {data[card]['name']}**\n**🌸 Group**: {data[card]['group']}\n🍃 **Copies**: {q}\n🌼 **Card ID**: {card}\n({rari})\n\n"
                    num += 1
                    mnum += 1
                    if num - 1 == len(cards):
                        emb.description = desc
                        embeds.append(emb)
                        mnum = -1000000000000000
                    if mnum == 5:
                        mnum = 0
                        emb.description = desc
                        desc = ""
                        embeds.append(emb)
            view = Menu(embeds)
            view.inter = inter #type:ignore
            await inter.edit_original_message(embed=embeds[0], view=view)


    @inventory.autocomplete("group")
    async def inv_group_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]


    @commands.slash_command()
    async def show(self, inter):
        pass


    @show.sub_command(description="Shows information about a card")
    async def card(self, inter, id: str):
        if id == "Nothing found":
            await inter.response.send_message("You don't have any card in your inventory.")
            return
        data = self.bot.data
        card = id
        rari = self.bot.rare[data[card]["rarity"]]
        emb = discord.Embed(
            title=f"{data[card]['name']}",
            description=
            f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n🍃 **Owner**: {inter.author.mention}\n({rari})",
            color=self.bot.get_color())
        emb.set_image(file=discord.File(f"./pics/{id}.png", "image.png"))
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)


    @show.sub_command(description="Shows all cards in the database")
    async def all(self, inter):
        ids = self.bot.data.keys()
        data = self.bot.data
        embs = []
        files = []
        for card in ids:
            rari = self.bot.rare[data[card]["rarity"]]
            emb = discord.Embed(
                title=f"{data[card]['name']}",
                description=
                    f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n({rari})",
                color=self.bot.get_color())
            emb.set_image(file=discord.File(f"./pics/{card}.png", "image.png"))
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            embs.append(emb)
            files.append(card)
        v = Menu(embs, files=files)
        del embs
        del files
        v.inter = inter #type:ignore
        await inter.send(embed=embs[0], view=v)

    @card.autocomplete("id")
    async def getids(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id, limit=input.upper())
        if not r:
            return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower() or input==""][:24]
    

    @commands.slash_command(description="Gift a card to your friend")
    async def gift_card(self, inter, user: discord.User, card_id:str):
        if card_id == "Nothing found":
            await inter.send("You don't have any card in your inventory.", ephemeral=True)
            return
        r = await self.bot.get_inventory(inter.author.id)
        copies = 0
        for card in r:
            if card[0].split(" ")[0] == card_id:
                copies = card[0].split(" ")[1]
                break
        if not copies:
            return await inter.send("You don't have that card in your inventory!", ephemeral=True)
        emb = discord.Embed(description=f"You've given {user.mention} a gift! <:HN_Gift:1034881304052899850>\n\n<:HN_Butterfly2:1034884649912127619> Given 1x {self.bot.data[card_id]['group']} **{self.bot.data[card_id]['name']}** | **{card_id}**\n{self.bot.rare[self.bot.data[card_id]['rarity']]}\n<:HN_Butterfly:1034882795547394179> **Copies left: **{copies-1}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)
        await self.bot.remove_cards(inter.author.id, card_id)
        await self.bot.insert_card(user.id, card_id)


    @gift_card.autocomplete("card_id")
    async def getid(self, inter, input: str):
        r = await self.bot.get_inventory(inter.author.id, limit=input.upper())
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
            return [id for id in ids if input.lower() in id.lower() or input==""][:24]  
    

    @commands.slash_command(description="Search a card with its name and group!")
    async def search(self, inter, group:str, rarity:commands.Range[1, 5]=0):  #type: ignore
        ids = [id for id in self.bot.data.keys()]
        embeds = []
        files = []
        for id in ids:
            if self.bot.data[id]["group"] == group:
              if rarity == self.bot.data[id]["rarity"] or rarity==0:
                data = self.bot.data
                card = id
                rari = self.bot.rare[data[card]["rarity"]]
                emb = discord.Embed(
                    title=f"{data[id]['name']}",
                    description=
                    f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n({rari})",
                    color=self.bot.get_color())
                emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
                file=discord.File(f"pics/{id}.png", "image.png")
                emb.set_image(url="attachment://image.png")
                files.append(id)
                embeds.append(emb)
        if len(embeds) == 0:
            return await inter.send("Nothing found...")
        m_v = Menu(embeds, files=files)
        m_v.inter = inter  #type:ignore
        await inter.send(embed=embeds[0], view=m_v, file=discord.File(f"pics/{files[0]}.png"))


    @search.autocomplete("group")
    async def group_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]


    @commands.slash_command(description="Shows your current cooldowns")
    async def cooldowns(self, inter):
        command1: commands.InvokableApplicationCommand = self.bot.get_slash_command("drop") #type:ignore
        command2 = self.bot.get_slash_command("task")
        commandli = [command1, command2]
        cds = []
        for command in commandli:
            fake_msg = discord.Object(id=inter.author.id)
            fake_msg.author = inter.author #type:ignore
            cd_mapping = command._buckets
            cd = cd_mapping.get_bucket(fake_msg) #type:ignore
            dr_cd = cd.get_retry_after()
            drop_cd = self.bot.sort_time(int(dr_cd)) if dr_cd else "0 seconds"
            cds.append(drop_cd)
        drop_cd = cds[0]
        task_cd = cds[1]
        try:
            car_cd = time.time() - self.bot.card_cd[inter.author.id]
            card_cd = self.bot.sort_time(int(300-car_cd)) if 300 > car_cd > 0 else "0 seconds"
        except KeyError:
            card_cd = "0 seconds"
        r = await self.bot.daily(inter.author.id, get=True)
        dai_cd = datetime.now().timestamp() - r[0]  #type:ignore
        daily_cd = self.bot.sort_time(int(86400-dai_cd)) if 86400 > dai_cd > 0 else "0 seconds"
        emb = discord.Embed(title="COOLDOWNS", description=f"<:HN_DropCD:1033796159149453312> **Drop: **{drop_cd}\n<:HN_ClaimCD:1033796187985281034> **Claim: **{card_cd}\n<:HN_DailyCD:1033796206155022336> **Daily: **{daily_cd}\n<:HN_DropCD:1033796159149453312> **Task: **{task_cd}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @commands.slash_command(description="Shows your progress in collecting a certain group!")
    async def progress(self, inter, group):
        inv = await self.bot.get_inventory(inter.author.id)
        g_cards = []
        tg_cards = []
        for c in inv:
            if self.bot.data[c[0].split(" ")[0]]["group"] == group:
                g_cards.append(c[0].split(" ")[0])
        for key, value in self.bot.data.items():
            if value["group"] == group:
                tg_cards.append(key)
        progress = {
            0:  "‿︵ʚ˚̣̣̣ɞ ══════════ ʚ˚̣̣̣ɞ‿︵",
            1: "‿︵ʚ˚̣̣̣ɞ ▰═════════ ʚ˚̣̣̣ɞ‿︵",
            2: "‿︵ʚ˚̣̣̣ɞ ▰▰════════ ʚ˚̣̣̣ɞ‿︵",
            3: "‿︵ʚ˚̣̣̣ɞ ▰▰▰═══════ ʚ˚̣̣̣ɞ‿︵", 
            4: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰══════ ʚ˚̣̣̣ɞ‿︵",
            5: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰▰═════ ʚ˚̣̣̣ɞ‿︵",
            6: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰▰▰════ ʚ˚̣̣̣ɞ‿︵",
            7: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰▰▰▰═══ ʚ˚̣̣̣ɞ‿︵",
            8: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰▰▰▰▰══ ʚ˚̣̣̣ɞ‿︵",
            9: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰▰▰▰▰▰═ ʚ˚̣̣̣ɞ‿︵",
            10: "‿︵ʚ˚̣̣̣ɞ ▰▰▰▰▰▰▰▰▰▰ ʚ˚̣̣̣ɞ‿︵"
        }
        perc = (len(g_cards)/len(tg_cards)) * 100
        pr = int(round(perc, 2))
        if pr in list(range(0, 10)):
            per = 0
        elif pr in list(range(11, 20)):
            per = 1
        elif pr in list(range(21, 30)):
            per = 2
        elif pr in list(range(31, 40)):
            per = 3
        elif pr in list(range(41, 50)):
            per = 4
        elif pr in list(range(51, 60)):
            per = 5
        elif pr in list(range(61, 70)):
            per = 6
        elif pr in list(range(71, 80)):
            per = 7
        elif pr in list(range(81, 90)):
            per = 8
        elif pr in list(range(91, 100)):
            per = 9
        elif pr == 100:
            per = 10
        tick_cross = []
        embs = []
        for cd in tg_cards:
            if cd in g_cards:
                tick_cross.append(f"**{cd}** <:HN_Checkmark:1035085306346606602>\n")
            else:
                tick_cross.append(f"**{cd}** <:HN_X:1035085573104345098>\n")
        for id in range(0, len(tick_cross), 25):
            nl = tick_cross[id:id+10]
            tc = "> " +'\n> '.join(nl)
            emb = discord.Embed(title=f"{group} Progress", description=f"{len(g_cards)}/{len(tg_cards)} Cards\n{progress[per]}\n\n{tc}", color=self.bot.get_color())
            embs.append(emb)
            v = Menu(embs)
            v.inter = inter
        await inter.send(embed=embs[0], view=v)


    @progress.autocomplete("group")
    async def gro_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]


def setup(bot: Hanknyeon):
    bot.add_cog(Cards(bot))