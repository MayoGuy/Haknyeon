import disnake as discord
from disnake.ext import commands
from db import Hanknyeon
from views import SelectPages, Menu, ConfirmView


class Folder(commands.Cog):
    def __init__(self, bot:Hanknyeon):
        self.bot = bot


    def convert_name(self, name, r):
        for key in r.keys():
            if key.split(" ")[1] == name:
                return key
    

    @commands.slash_command()
    async def folder(self, inter):
        pass
    

    @folder.sub_command(description="Bind some of your favourite cards into a folder!")
    async def create(self, inter, name, emoji:discord.Emoji=""):
        name = str(emoji) + " " + name
        r = await self.bot.get_inventory(inter.author.id)
        if not r:
           return [id for id in ["Nothing found"]]
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
        v = SelectPages(ids, name)
        v.inter = inter
        await inter.send(embed=discord.Embed(title="Folder Creation Process", description=f"**Folder Name: **{name}\n\n**Selected Cards:**\nNone", color=self.bot.get_color()), view=v)
        await v.wait()
        if v.value:
            await self.bot.folder(inter.author.id, name=name, add=True, ids=v.ids)
        else:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this process!", color=self.bot.get_color()), view=None)


    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.errors.EmojiNotFound):
            await ctx.send("You can only use emojis available in this server!", ephemeral=True)
        else:
            raise error


    @folder.sub_command(description="Shows a folder that you have created")
    async def show(self, inter, name):
        r = await self.bot.folder(inter.author.id, get=True)
        print(r)
        name = self.convert_name(name, r)
        inv = await self.bot.get_inventory(inter.author.id)
        inv_ids = [a[0].split(" ")[0] for a in inv]
        ids1 = r[name]
        ids = []
        for id in ids1:
            if  id in inv_ids:
                ids.append(id)
        embeds = []
        desc = ""
        
        for i in range(0, len(ids), 5):
            emb = discord.Embed(title=f"{name} | Folder", color=self.bot.get_color())
            nl = ids[i:i+5]
            for id in nl:
                for c in inv:
                    if id == c[0].split(" ")[0]:
                        q = c[0].split(" ")[1]
                data = self.bot.data
                card = id
                rari = self.bot.rare[data[card]["rarity"]]
                desc += f"**{data[card]['name']}**\n**🌸 Group**: {data[card]['group']}\n🍃 **Copies**: {q}\n🌼 **Card ID**: {card}\n({rari})\n\n"
            emb.description = desc
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
            desc = ""
            embeds.append(emb)
        v = Menu(embeds)
        v.inter = inter
        await inter.send(embed=embeds[0], view=v)


    @show.autocomplete("name")
    async def name_auto(self, inter, input):
        r = await self.bot.folder(inter.author.id, get=True)
        return [name.split(" ")[1] for name in r.keys() if input in name or input==""][:25]


    @folder.sub_command(description="Lists all folders owned by a user")
    async def list(self, inter):
        r2 = await self.bot.folder(inter.author.id, get=True)
        if not r2:
            return await inter.send("No folder found...", ephemeral=True)
        r1 = [key for key in r2.keys()]
        embeds = []
        for i in range(0, len(r1), 5):
            emb = discord.Embed(title=f"{inter.author.display_name}'s folders:", color=self.bot.get_color())
            nl = r1[i:i+5]
            folders = '\n\n'.join(name + " | " + f"*{len(r2[name])} cards*" for name in nl)
            emb.description=folders
            emb.set_author(name=str(inter.author), icon_url=inter.author.avatar.url)
            embeds.append(emb)
        v = Menu(embeds)
        v.inter = inter
        await inter.send(embed=embeds[0], view=v)


    @folder.sub_command(description="Deletes one of your folders")
    async def delete(self, inter, folder):
        r = await self.bot.folder(inter.author.id, get=True)
        folder = self.convert_name(folder, r)
        v = ConfirmView()
        v.inter = inter
        await inter.send(embed=discord.Embed(description=f"Are you sure you want to delete this folder? ({folder})", color=self.bot.get_color()), view=v)
        await v.wait()
        if not v.value:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this process!", color=self.bot.get_color()), view=None)
        else:
            await self.bot.folder(inter.author.id, name=folder, delete=True)
            await inter.edit_original_message(embed=discord.Embed(description=f"<:HN_Checkmark:1035085306346606602> You successfully deleted the folder! ({folder})", color=self.bot.get_color()), view=None)
    

    @delete.autocomplete("folder")
    async def n_auto(self, inter, input):
        r = await self.bot.folder(inter.author.id, get=True)
        return [name.split(" ")[1] for name in r.keys() if input in name][:25]

    @folder.sub_command(description="Add cards to a folder!")
    async def add_cards(self, inter, folder):
        r = await self.bot.get_inventory(inter.author.id)
        r2 = await self.bot.folder(inter.author.id, get=True)
        folder = self.convert_name(folder, r2)
        if not r:
            return await inter.send("No card found...", ephemeral=True)
        else:
            ids = [str(card[0].split(" ")[0]) for card in r]
        v = SelectPages(ids, folder)
        v.inter = inter
        await inter.send(embed=discord.Embed(title="Select cards from the drop down menu", description=f"**Folder: **{folder}\n\n**Selected Cards:**\nNone", color=self.bot.get_color()), view=v)
        await v.wait()
        if v.value:
            await self.bot.folder(inter.author.id, name=folder, add=True, ids=v.ids)
        else:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this process!", color=self.bot.get_color()), view=None)


    @add_cards.autocomplete("folder")
    async def n_auto2(self, inter, input):
        r = await self.bot.folder(inter.author.id, get=True)
        return [name.split(" ")[1] for name in r.keys() if input in name][:25]
    

    @folder.sub_command(description="Remove cards from a folder!")
    async def remove_cards(self, inter, folder):
        r2 = await self.bot.folder(inter.author.id, get=True)
        folder = self.convert_name(folder, r2)
        ids = r2[folder]
        v = SelectPages(ids, folder)
        v.inter = inter
        await inter.send(embed=discord.Embed(title="Select cards from the drop down menu", description=f"**Folder: **{folder}\n\n**Selected Cards:**\nNone", color=self.bot.get_color()), view=v)
        await v.wait()
        if v.value:
            await self.bot.folder(inter.author.id, name=folder, delete=True, ids=v.ids)
        else:
            await inter.edit_original_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this process!", color=self.bot.get_color()), view=None)


    @remove_cards.autocomplete("folder")
    async def n_auto3(self, inter, input):
        r = await self.bot.folder(inter.author.id, get=True)
        return [name.split(" ")[1] for name in r.keys() if input in name][:25]
        


def setup(bot):
    bot.add_cog(Folder(bot))