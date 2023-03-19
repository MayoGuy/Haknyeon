from disnake.ext import commands, tasks
import disnake as discord
from db import Hanknyeon
from views import CardsView, Menu
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import traceback


class Cards(commands.Cog):
    def __init__(self, bot: Hanknyeon) -> None:
        self.bot = bot
        self.get_votees.start()
        
    
    async def cog_slash_command_check(self, inter: discord.ApplicationCommandInteraction) -> bool:
        r = await self.bot.get_profile(inter.author.id)
        if not r:
            raise commands.CheckFailure("first")
        else:
            return True


    @tasks.loop(seconds=30)
    async def get_votees(self):
        for key, value in self.bot.voted.copy().items():
            if datetime.utcnow().timestamp() - value > 2400:
                del self.bot.voted[key]


    @get_votees.before_loop
    async def before_vote(self):
        await self.bot.wait_until_ready()


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
    

    def drop_cool(msg:discord.Interaction):
        try:
            if msg.author.id == 756018524413100114:
                return None
            elif msg.author.id in list(msg.bot.voted.keys()):
                return commands.Cooldown(1, 300)
        except Exception as e:
            print(e)
        print(msg.author.id)
        return commands.Cooldown(1, 600)


    @commands.slash_command(description="Drops a set of 3 cards")
    @commands.dynamic_cooldown(drop_cool, commands.BucketType.user)
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
        if inter.author.id in list(self.bot.curr_boosts.keys()):
            match self.bot.curr_boosts[inter.author.id]["item"]:
                case 'sb':
                    loy = random.choice([1, 2, 4, 0])
                    if loy == 0:
                        r5 = [id for id in piclis if data[id]["rarity"]==5]
                    else:
                        r5 = []
                    tot = (r1 + r2 + r3*3 + r4*2 + r5)
                case 'nb':
                    loy = 0
                    if loy == 0:
                        r5 = [id for id in piclis if data[id]["rarity"]==5]
                    else:
                        r5 = []
                    tot = (r2 + r3*2 + r4*3 + r5*2)
                case 'mb':
                    loy = []
                    r5 = [id for id in piclis if data[id]["rarity"]==5]
                    tot = (r3*2 + r4*4 + r5*3)
        else:
            loy = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
            if loy == 0:
                r5 = [id for id in piclis if data[id]["rarity"]==5]
            else:
                r5 = []
            tot = (r1 + r2 + r3 + r4 + r5)
        while True:
            q, w, e = random.sample(tot, 3)
            if q != w and w != e and e != q:
                break
        buff = await self.bot.loop.run_in_executor(None, self.bot.create, q + ".png", w + ".png", e + ".png")
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
        view.buff = await self.bot.loop.run_in_executor(None, self.bot.create, q + ".png", w + ".png", e + ".png")
        await inter.edit_original_message(
            embed=emb,
            view=view,
        )
        file.close()
        buff.close()
        del buff
        del emb

    
    def sort_idol(self, id):
        return self.bot.data[id[0].split(" ")[0]]["name"].split(" (")[0]
    

    def sort_gorup(self, id):
        return self.bot.data[id[0].split(" ")[0]]["group"]
    

    def sort_rarity(self, id):
        return self.bot.data[id[0].split(" ")[0]]["group"]
    
    def sort_era(self, id):
        try:
            return self.bot.data[id[0].split(" ")[0]]["name"].split(" (")[1][:-1]
        except:
            pass


    @commands.slash_command(description="Shows Inventory")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def inventory(self, inter, user: discord.User = None, sort_by:str=commands.Param("Idol", choices=["Idol", "Group", "Rarity", "Era"]), group:str=None, rarity:commands.Range[1, 5]=None, idol:str=None, era:str=None): #type:ignore
        await inter.response.defer()
        data = self.bot.data
        user = user if user else inter.author
        r = await self.bot.get_inventory(user.id)
        cards = [l for l in r if l[0].split(" ")[0] in list(data.keys())]
        foldered = []
        r2 = await self.bot.folder(user.id, get=True)
        if r2:
            for k, v in r2.items():
                foldered += v
            print(len(cards))
            print(len(foldered))
            cards = [c for c in cards if c[0].split(" ")[0] not in foldered]
            print(len(cards))
        if group:
            cards = [c for c in cards if data[c[0].split(" ")[0]]["group"] == group]
        if rarity:
            cards = [c for c in cards if data[c[0].split(" ")[0]]["rarity"] == rarity]
        if idol:
            cards = [c for c in cards if idol in data[c[0].split(" ")[0]]["name"]]
        if era:
            cards = [c for c in cards if era in data[c[0].split(" ")[0]]["name"]]
        if not cards:
            await inter.send(embed=discord.Embed(description="Nothing found...", color=self.bot.get_color()))
            return
        match sort_by:
            case "Idol":
                cards.sort(key=self.sort_idol)
            case "Group":
                cards.sort(key=self.sort_gorup)
            case "Rarity":
                cards.sort(key=self.sort_rarity)
            case "Era":
                cards.sort(key=self.sort_era)
        num = 1
        embs = []
        for i in range(0, len(cards), 5):
            nl = cards[i:i+5]
            emb = discord.Embed(title=f"{user.display_name}'s Inventory...",
                                color=self.bot.get_color())
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            emb.set_footer(text="Cards in your folders won't be shown in your inventory")
            desc = ""
            for c in nl:
                card = c[0].split(" ")[0]
                q = c[0].split(" ")[1]
                try:
                    rari = self.bot.rare[data[card]["rarity"]]
                except:
                    continue
                desc += f"**{num}. {data[card]['name']}**\n**🌸 Group**: {data[card]['group']}\n🍃 **Copies**: {q}\n🌼 **Card ID**: {card}\n({rari})\n\n"
                num += 1
            emb.description = desc
            embs.append(emb)
        view = Menu(embs)
        view.inter = inter
        await inter.edit_original_message(embed=embs[0], view=view)


    @inventory.autocomplete("group")
    async def inv_group_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]


    @inventory.autocomplete("idol")
    async def inv_idol_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["name"].split(" (")[0] in groups:
                groups.append(self.bot.data[id]["name"].split(" (")[0])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]
    

    @inventory.autocomplete("era")
    async def inv_era_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            try:
                if not self.bot.data[id]["name"].split(" (")[1][:-1] in groups:
                    groups.append(self.bot.data[id]["name"].split(" (")[1][:-1])
            except:
                pass
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
        emb.set_image(url=f"https://haknyeon.info/topsecret/card?id={card.replace('#', 'h')}")
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
        await inter.send(embed=emb)


    @show.sub_command(description="Shows all cards in the database")
    @commands.cooldown(1, 30, commands.BucketType.user)
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
            emb.set_image(url=f"https://haknyeon.info/topsecret/card?id={card.replace('#', 'h')}")
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            embs.append(emb)
            files.append(card)
        v = Menu(embs)
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
    

    def se_sort_idol(self, id):
        return self.bot.data[id]["name"].split(" (")[0]
    

    def se_sort_gorup(self, id):
        return self.bot.data[id]["group"]
    

    def se_sort_rarity(self, id):
        return self.bot.data[id]["group"]
    
    def se_sort_era(self, id):
        try:
            return self.bot.data[id]["name"].split(" (")[1][:-1]
        except:
            return self.bot.data[id]["name"]


    @commands.slash_command(description="Search a card with its name and group!")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def search(self, inter, sort_by:str=commands.Param("Idol", choices=["Idol", "Group", "Rarity", "Era"]), group:str=None, rarity:commands.Range[1, 5]=0, idol:str=None, era:str=None):  #type: ignore
        ids = [id for id in self.bot.data.keys()]
        data = self.bot.data
        embeds = []
        if group:
            ids = [c for c in ids if data[c]["group"] == group]
        if rarity:
            ids = [c for c in ids if data[c]["rarity"] == rarity]
        if idol:
            ids = [c for c in ids if idol in data[c]["name"]]
        if era:
            ids = [c for c in ids if era in data[c]["name"]]
        if not ids:
            await inter.send(embed=discord.Embed(description="Nothing found...", color=self.bot.get_color()))
            return
        match sort_by:
            case "Idol":
                ids.sort(key=self.se_sort_idol)
            case "Group":
                ids.sort(key=self.se_sort_gorup)
            case "Rarity":
                ids.sort(key=self.se_sort_rarity)
            case "Era":
                ids.sort(key=self.se_sort_era)
        for id in ids:
            card = id
            rari = self.bot.rare[data[card]["rarity"]]
            emb = discord.Embed(
                title=f"{data[id]['name']}",
                description=
                f"🌸 **Group**: {data[card]['group']}\n🌼 **Card ID**: {card}\n({rari})",
                color=self.bot.get_color())
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
            emb.set_image(url=f"https://haknyeon.info/topsecret/card?id={card.replace('#', 'h')}")
            embeds.append(emb)
        if len(embeds) == 0:
            return await inter.send("Nothing found...")
        m_v = Menu(embeds)
        m_v.inter = inter  #type:ignore
        await inter.send(embed=embeds[0], view=m_v)


    @search.autocomplete("group")
    async def group_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]


    @search.autocomplete("idol")
    async def se_idol_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["name"].split(" (")[0] in groups:
                groups.append(self.bot.data[id]["name"].split(" (")[0])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]
    

    @search.autocomplete("era")
    async def se_era_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            try:
                if not self.bot.data[id]["name"].split(" (")[1][:-1] in groups:
                    groups.append(self.bot.data[id]["name"].split(" (")[1][:-1])
            except:
                pass
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
            drop_cd = self.bot.sort_time(int(dr_cd)) if dr_cd else "Available!"
            cds.append(drop_cd)
        drop_cd = cds[0]
        task_cd = cds[1]
        try:
            car_cd = time.time() - self.bot.card_cd[inter.author.id]
            card_cd = self.bot.sort_time(int(300-car_cd)) if 300 > car_cd > 0 else "Available!"
        except KeyError:
            card_cd = "Available!"
        if inter.author.id in list(self.bot.voted.keys()):
            card_cd = "Available!"
        r = await self.bot.daily(inter.author.id, get=True)
        dai_cd = datetime.now().timestamp() - r[0]  #type:ignore
        daily_cd = self.bot.sort_time(int(86400-dai_cd)) if 86400 > dai_cd > 0 else "Available!"
        v = await self.bot.curr.fetchrow("SELECT datee, claim FROM votes WHERE user_id=$1", inter.author.id)
        if not v:
            vote = "Available!"
        elif v[1]:
            vote = "Available!"
        else:
            vote_cd = datetime.now().timestamp() - v[0]
            vote = self.bot.sort_time(int(43200-vote_cd)) if 43200 > vote_cd > 0 else "Available!"
        emb = discord.Embed(title="Current Cooldowns", description=f"<:HN_DropCD:1033796159149453312> **Drop: **{drop_cd}\n<:HN_ClaimCD:1033796187985281034> **Claim: **{card_cd}\n\n<:HN_DailyCD:1033796206155022336> **Daily: **{daily_cd}\n<:HN_DropCD:1033796159149453312> **Task: **{task_cd}\n**Vote: **{vote}", color=self.bot.get_color())
        emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url) #type:ignore
        await inter.send(embed=emb)


    @commands.slash_command(description="Shows your progress in collecting a certain group!")
    @commands.cooldown(1, 60, commands.BucketType.user)
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
        elif pr in list(range(10, 20)):
            per = 1
        elif pr in list(range(20, 30)):
            per = 2
        elif pr in list(range(30, 40)):
            per = 3
        elif pr in list(range(40, 50)):
            per = 4
        elif pr in list(range(50, 60)):
            per = 5
        elif pr in list(range(60, 70)):
            per = 6
        elif pr in list(range(70, 80)):
            per = 7
        elif pr in list(range(80, 90)):
            per = 8
        elif pr in list(range(90, 100)):
            per = 9
        elif pr == 100:
            per = 10
        embs = []
        await inter.response.defer()
        r = await self.bot.loop.run_in_executor(None, self.create_progress, g_cards, tg_cards)
        embs = []
        for f in r:
            emb = discord.Embed(title=f"{group} Progress", description=f"{len(g_cards)}/{len(tg_cards)} Cards\n{progress[per]}", color=self.bot.get_color())
            embs.append(emb)
        v = Menu(embs, files=r)
        v.inter = inter
        embs[0].set_image(file=discord.File(r[0], "image.png"))
        await inter.edit_original_message(embed=embs[0], view=v)
        return


    @progress.autocomplete("group")
    async def gro_auto(self, inter, input):
        ids = [id for id in self.bot.data.keys()]
        groups = []
        for id in ids:
            if not self.bot.data[id]["group"] in groups:
                groups.append(self.bot.data[id]["group"])
        return [group for group in groups if input.lower() in group.lower() or input==""][:24]


    def create_progress(self, inventory, group):
        imgs = []
        if "SLCY#577" in group:
            print("yes")
        for g in group:
            img = Image.new("RGBA", (273, 400), (0, 0, 0, 0))
            im = Image.open(f"pics/{g}.png").resize((273, 367))
            if g in inventory:
                img.paste(im, (0, 0), im.convert("RGBA"))
                color = "pink"
            else:  
                color = "gray"
                img.paste(im.convert("LA"), (0, 0), im.convert("LA"))  
            draw = ImageDraw.Draw(img, "RGBA")
            font = ImageFont.truetype('Cookies.ttf', 24)
            _, _, w, h = draw.textbbox((0, 0), g, font=font)
            draw.text(((273-w)/2, 367), g, font=font, fill=color)
            del im
            del draw
            del font
            imgs.append(img)
            del img
        files = []
        for i in range(0, len(imgs), 12):
            bimg = Image.new("RGBA", (820+273, 1200), (0, 0, 0, 0))
            x = 0
            y = 0
            nl = imgs[i:i+12]
            for im in nl:
                bimg.paste(im, (x, y), im.convert("RGBA"))
                if x == 819:
                    x = 0
                    y += 400
                else:
                    x += 273
            buff = BytesIO()
            bimg.save(buff, "png")
            buff.seek(0)
            del bimg
            files.append(buff)
        del imgs
        return files


def setup(bot: Hanknyeon):
    bot.add_cog(Cards(bot))