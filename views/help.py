import disnake as discord
from db import Hanknyeon


class HelpView(discord.ui.View):
    def __init__(self, bot: Hanknyeon):
        super().__init__(timeout=180)
        self.bot = bot
        self.add_item(discord.ui.Button(label="Support Sever",
                      url="https://discord.gg/haknyeon", style=discord.ButtonStyle.gray))
        self.add_item(discord.ui.Button(
            label="Patron", url="https://patreon.com/user?u=78851656&utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=creatorshare_creator&utm_content=join_link", style=discord.ButtonStyle.gray))
        self.d = {"Cards":["🎴", "All cards related commands are available in this category."], "Currency":["💰", "This category contains all Petals related commands."], "Folder":["📁", "Sort out your special cards in a certain folder!"], "Fun":["🎮", "All fun related commands! These commands have tendency to earn you some petals."], "Utility":["⚙️", "Some general commands are found in this category."], "Powerups":["🚀","Boost your card collection with awesome powerups!."]}
        for key, value in self.d.items():
            self.catsel.add_option(label=key, emoji=value[0], description=value[1])
 

    @discord.ui.select(placeholder="Select a category", options=[])
    async def catsel(self, s, inter):
        c = s.values[0]
        cog = self.bot.get_cog(c)
        emb = discord.Embed(title=f"{c} Category",
                            description=self.d[c][1], color=self.bot.get_color())
        for com in cog.get_slash_commands():
            if com.children:
                for key, value in com.children.items():
                    emb.add_field(name=com.name+" "+key,
                                  value="╰"+value.description, inline=False)
            else:
                emb.add_field(name=com.name, value="╰" +
                              com.description, inline=False)
        await inter.response.edit_message(embed=emb)
