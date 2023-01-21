from disnake.ext import commands
import disnake as discord
from db import Hanknyeon
from views import DeleteView

class _staff(commands.Cog):
    def __init__(self, bot: Hanknyeon) -> None:
        self.bot = bot


    @commands.slash_command(
    description="Adds a card to database. Staff only command", guild_ids=[1024399481782927511, 1024402764601765978])
    async def add_card(self, inter, name: str, rarity: commands.Range[1, 5], group: str, id,
                        pic: discord.Attachment, limited_days:int=None): #type:ignore
        if not inter.guild.get_role(1024579633699627028) in inter.author.roles and inter.author.id != 756018524413100114:
            return await inter.send("You don't have permissions to use this command!")
        await inter.response.defer()
        await inter.edit_original_message(
            f"Successfully added the card with ID: {id}!")
        await pic.save(f"./pics/{id}.png") #type:ignore
        await pic.save(f"/var/www/html/hanknyeon/pics/{id}.png")
        self.bot.data[id] = {"name": name, "rarity": rarity, "group": group}
        await self.bot.add_card_data(name, group, rarity, id, limit=limited_days)

    
    @commands.slash_command(description="Makes a card not accessible. Staff only command", guild_ids=[1024399481782927511, 1024402764601765978])
    async def delete_card(self, inter, id: str):
        if not inter.guild.get_role(1024579633699627028) in inter.author.roles and inter.author.id != 756018524413100114:
            return await inter.send("You don't have permissions to use this command!")
        await inter.send("Succesfully deleted")
        await self.bot.delete_card(id, from_existance=False)


    @commands.slash_command(description="Takes a card from a user. Staff only command", guild_ids=[1024399481782927511, 1024402764601765978])
    async def take_card(self, inter, user: discord.User):
        r = await self.bot.get_inventory(user.id)
        view = DeleteView(user.id, r)
        view.bot = self.bot #type:ignore
        view.inter = inter  #type:ignore
        await inter.send(view=view)

    
    @commands.slash_command(description="Gives a card to anyone. Staff only command", guild_ids=[1024399481782927511, 1024402764601765978])
    async def give_card(self, inter, user: discord.User, card_id:str):
        if not inter.guild.get_role(1024979194800779324) in inter.author.roles:
            return await inter.send("You don't have permissions to use this command!")
        if card_id == "Nothing found":
            await inter.send("You don't have any card in your inventory.", ephemeral=True)
            return
        await self.bot.insert_card(user.id, card_id)
        await inter.send(f"You successfully gave a card ({self.bot.data[card_id]['name']}) to {user.mention}!")
    

    @give_card.autocomplete("card_id")
    async def getallids(self, inter, user_input):
        return [id for id in list(self.bot.data.keys()) if user_input.lower() in id.lower()][:25]


    @commands.slash_command(description="Removes a card from database. Staff only command", guild_ids=[1024399481782927511, 1024402764601765978])
    async def remove_card(self, inter, card_id):
        if not inter.guild.get_role(1024579633699627028) in inter.author.roles and inter.author.id != 756018524413100114:
            return await inter.send("You don't have permissions to use this command!")
        await inter.send("Succesfully deleted")
        await self.bot.delete_card(card_id, from_existance=True)


    @remove_card.autocomplete("card_id")
    async def remgetallids(self, inter, user_input):
        return [id for id in self.bot.data.keys() if user_input.lower() in id.lower()][:25]


def setup(bot: Hanknyeon):
    bot.add_cog(_staff(bot))