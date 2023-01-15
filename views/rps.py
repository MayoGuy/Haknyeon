import disnake as discord
import random


class RPSButton(discord.ui.Button):
    def __init__(self, thing):
        self.ch = thing
        self.color = {"Rock":discord.ButtonStyle.blurple, "Paper":discord.ButtonStyle.green, "Scissors":discord.ButtonStyle.red}
        self.emoj = {"Rock":"✊", "Paper":"🖐️", "Scissors":"✌️"}
        super().__init__(label=thing, style=self.color[thing], emoji=self.emoj[thing])


    async def callback(self, inter):
        comp_ch = random.choice(["Rock", "Paper", "Scissors"])
        title = ""
        if self.ch == comp_ch:
            title = "It's a Tie!"
        elif (self.ch=='Paper' and comp_ch=='Rock') or (self.ch=='Scissors' and comp_ch=='Paper') or (self.ch=='Rock' and comp_ch=='Scissors'):
            pts = random.choice([0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5])
            if pts:
                await self.view.bot.add_coins(self.view.inter.author.id, 1)
            title = f"You defeated me! ({pts} {self.view.bot.petal})"
        else:
            title = "I defeated you!"
        embed = discord.Embed(title=title, description=f"**You Chose: **{self.emoj[self.ch]}\n**I Chose: **{self.emoj[comp_ch]}", color=0xfcb8b8)
        self.view.clear_items()
        self.view.add_item(self.view.tryagain)
        await inter.response.edit_message(embed=embed, view=self.view)


class RPS(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.u_ch = None
        self.c_ch = None
        self.remove_item(self.tryagain)
        self.add_item(RPSButton("Rock"))
        self.add_item(RPSButton("Paper"))
        self.add_item(RPSButton("Scissors"))


    @discord.ui.button(label="Try Again", style=discord.ButtonStyle.red, row=1)
    async def tryagain(self, button, inter):
        self.add_item(RPSButton("Rock"))
        self.add_item(RPSButton("Paper"))
        self.add_item(RPSButton("Scissors"))
        self.remove_item(self.tryagain)
        embed = discord.Embed(title="An intense game of Rock, Paper and Scissors!", description="Select an option from below!", color=0xfcb8b8)
        await inter.response.edit_message(embed=embed, view=self)



    
