import disnake as discord
from db import Hanknyeon


class HelpView(discord.ui.View):
    def __init__(self, bot:Hanknyeon):
        super().__init__(timeout=180)
        self.bot = bot
        self.add_item(discord.ui.Button(label="Support Sever", url="https://discord.gg/haknyeon", style=discord.ButtonStyle.gray))
        self.add_item(discord.ui.Button(label="Patron", url="https://patreon.com/user?u=78851656&utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=creatorshare_creator&utm_content=join_link", style=discord.ButtonStyle.gray))


    @discord.ui.button(label="Cards", style=discord.ButtonStyle.blurple)
    async def cards(self, b, inter):
        cog = self.bot.get_cog("Cards")
        emb = discord.Embed(title="Cards Category", description="All cards related commands are available in this category.", color=self.bot.get_color())
        for com in cog.get_slash_commands():
            if com.children:
                for key, value in com.children.items():
                    emb.add_field(name=com.name+" "+key, value="╰"+value.description, inline=False)
            else:
                emb.add_field(name=com.name, value="╰"+com.description, inline=False)
        await inter.response.edit_message(embed=emb)


    @discord.ui.button(label="Currency", style=discord.ButtonStyle.blurple)
    async def curr(self, b, inter):
        cog = self.bot.get_cog("Currency")
        emb = discord.Embed(title="Currency Category", description="This category contains all Petals related commands.", color=self.bot.get_color())
        for com in cog.get_slash_commands():
            if com.children:
                for key, value in com.children.items():
                    emb.add_field(name=com.name+" "+key, value="╰"+value.description, inline=False)
            else:
                emb.add_field(name=com.name, value="╰"+com.description, inline=False)
        await inter.response.edit_message(embed=emb)


    @discord.ui.button(label="Folder", style=discord.ButtonStyle.blurple)
    async def fol(self, b, inter):
        cog = self.bot.get_cog("Folder")
        emb = discord.Embed(title="Folder Category", description="Sort out your special cards in a certain folder!", color=self.bot.get_color())
        for com in cog.get_slash_commands():
            if com.children:
                for key, value in com.children.items():
                    emb.add_field(name=com.name+" "+key, value="╰"+value.description, inline=False)
            else:
                emb.add_field(name=com.name, value="╰"+com.description, inline=False)
        await inter.response.edit_message(embed=emb)

    
    @discord.ui.button(label="Fun", style=discord.ButtonStyle.blurple)
    async def fun(self, b, inter):
        cog = self.bot.get_cog("Fun")
        emb = discord.Embed(title="Fun Category", description="All fun related commands! These commands have tendency to earn you some petals.", color=self.bot.get_color())
        for com in cog.get_slash_commands():
            if com.children:
                for key, value in com.children.items():
                    emb.add_field(name=com.name+" "+key, value="╰"+value.description, inline=False)
            else:
                emb.add_field(name=com.name, value="╰"+com.description, inline=False)
        await inter.response.edit_message(embed=emb)

    
    @discord.ui.button(label="Utility", style=discord.ButtonStyle.blurple)
    async def utils(self, b, inter):
        cog = self.bot.get_cog("Utility")
        emb = discord.Embed(title="Utility Category", description="Some general commands are found in this category.", color=self.bot.get_color())
        for com in cog.get_slash_commands():
            if com.children:
                for key, value in com.children.items():
                    emb.add_field(name=com.name+" "+key, value="╰"+value.description, inline=False)
            else:
                emb.add_field(name=com.name, value="╰"+com.description, inline=False)
        await inter.response.edit_message(embed=emb)