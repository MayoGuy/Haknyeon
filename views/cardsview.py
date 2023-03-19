import disnake as discord
import time


class CardButton(discord.ui.Button):
    
    def __init__(self, emoji, value, rarity, name, card):
        super().__init__(style=discord.ButtonStyle.gray, emoji=emoji)
        self.value = value
        self.rarity = rarity
        self.claimed = None
        self.name = name
        self.card = card

    async def callback(self, inter):
        self.view: CardsView
        try:
            tm = time.time() - self.view.bot.card_cd[inter.author.id] #type:ignore
            if inter.author.id not in list(self.view.bot.voted.keys()):
                if tm < 300:
                    await inter.send(f"You need to wait {self.view.bot.sort_time(300-tm)} before claiming a card!", ephemeral=True)  #type:ignore
                    return
        except KeyError:
            pass
        if inter.author==self.claimed or (inter.author in self.view.clicked):  #type:ignore
            await inter.response.send_message(
                "You have already picked a card!", ephemeral=True)
        elif not self.claimed or inter.author == self.view.inter.author:
            await inter.response.send_message(
                f"You picked the #{self.value} Card!", ephemeral=True)
            self.view.clicked.append(inter.author)
            if self.claimed in self.view.clicked:
                self.view.clicked.remove(self.claimed)
                self.view.bot.card_cd.pop(self.claimed.id)
                await self.view.bot.remove_cards(self.claimed.id, self.card)
            self.view.bot.card_cd[inter.author.id] = time.time()
            self.claimed = inter.author
            await self.view.bot.insert_card(inter.author.id, self.card)  #type:ignore
        else:
            await inter.response.send_message("Someone has already picked this Card!", ephemeral=True)


class CardsView(discord.ui.View):
    def __init__(self, rarities, names, cards):
        super().__init__(timeout=20)
        self.clicked = []
        for i, j in enumerate(["<:HN_1:1035176844812619856>", "<:HN_2:1035176863598907403>", "<:HN_3:1035176881152081920>"]):
            self.add_item(CardButton(j, i + 1, rarities[i], names[i], cards[i]))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True  # type: ignore
        emb = discord.Embed(
            description=f"{self.inter.author.mention} is dropping a set of 3 cards!",
            color=0xfcb8b8)
        emb.set_footer(text="This drop has expired")
        f = discord.File(self.buff, "image.png")
        emb.set_image(file=f)
        self.buff.close()
        del self.buff
        f.close()
        del f
        await self.inter.edit_original_message(view=self, embed=emb)  # type: ignore
        m = await self.inter.original_message()  # type: ignore
        e = discord.Embed(
            title="Results of the Drop!",
            color=0xfcb8b8
        )
        for item in self.children:
            claimed = item.claimed.mention if item.claimed else "No one."  # type: ignore
            e.add_field(name=f"Card #{item.value}", value=f"<:HN_Butterfly2:1034884649912127619> {item.name}\n{self.bot.rare[item.rarity]}\n\n{claimed}")  # type: ignore
        await m.reply(embed=e)
        del emb