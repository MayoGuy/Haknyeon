import akinator
import disnake as discord


class AkiView(discord.ui.View):
    def __init__(self, aki: akinator.AsyncAkinator):
        super().__init__(timeout=180)
        self.aki = aki
    

    async def interaction_check(self, inter):
        if self.inter.author.id != inter.author.id:  #type:ignore
            return False
        else:
            return True

    
    async def on_error(self, error, item, inter) -> None:
        if self.inter.author.id != inter.author.id:  #type:ignore
            return await inter.send("You can't use that!")
        else:
            raise error


    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, b, inter):
        if self.aki.progression <= 85:
            await self.aki.answer(akinator.Answer.Yes)
            emb = discord.Embed(title=f"{self.inter.author.display_name}'s Akinator Game!", description=f"**Question#{self.aki.step+1}:**\n{self.aki.question}", color=0xfcb8b8)
            await inter.response.edit_message(embed=emb)
        else:
            fg = await self.aki.win()
            if fg:
                emb = discord.Embed(title="My guess is...", description=f"**{fg.name}**\n{fg.description}\nRanked as: **#{fg.ranking}**", color=0xfcb8b8)
                emb.set_image(url=fg.absolute_picture_path)
                await inter.response.edit_message(embed=emb, view=None)

    
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, b, inter):
        if self.aki.progression <= 85:
            await self.aki.answer(akinator.Answer.No)
            emb = discord.Embed(title=f"{self.inter.author.display_name}'s Akinator Game!", description=f"**Question#{self.aki.step+1}:**\n{self.aki.question}", color=0xfcb8b8)
            await inter.response.edit_message(embed=emb)
        else:
            fg = await self.aki.win()
            if fg:
                emb = discord.Embed(title="My guess is...", description=f"**{fg.name}**\n{fg.description}\nRanked as: **#{fg.ranking}**", color=0xfcb8b8)
                emb.set_image(url=fg.absolute_picture_path)
                await inter.response.edit_message(embed=emb, view=None)

    
    @discord.ui.button(label="I don't know", style=discord.ButtonStyle.blurple)
    async def idk(self, b, inter):
        if self.aki.progression <= 85:
            await self.aki.answer(akinator.Answer.Idk)
            emb = discord.Embed(title=f"{self.inter.author.display_name}'s Akinator Game!", description=f"**Question#{self.aki.step+1}:**\n{self.aki.question}", color=0xfcb8b8)
            await inter.response.edit_message(embed=emb)
        else:
            fg = await self.aki.win()
            if fg:
                emb = discord.Embed(title="My guess is...", description=f"**{fg.name}**\n{fg.description}\nRanked as: **#{fg.ranking}**", color=0xfcb8b8)
                emb.set_image(url=fg.absolute_picture_path)
                await inter.response.edit_message(embed=emb, view=None)


    @discord.ui.button(label="Probably", style=discord.ButtonStyle.blurple)
    async def probyes(self, b, inter):
        if self.aki.progression <= 85:
            await self.aki.answer(akinator.Answer.Probably)
            emb = discord.Embed(title=f"{self.inter.author.display_name}'s Akinator Game!", description=f"**Question#{self.aki.step+1}:**\n{self.aki.question}", color=0xfcb8b8)
            await inter.response.edit_message(embed=emb)
        else:
            fg = await self.aki.win()
            if fg:
                emb = discord.Embed(title="My guess is...", description=f"**{fg.name}**\n{fg.description}\nRanked as: **#{fg.ranking}**", color=0xfcb8b8)
                emb.set_image(url=fg.absolute_picture_path)
                await inter.response.edit_message(embed=emb, view=None)


    @discord.ui.button(label="Probably Not", style=discord.ButtonStyle.blurple)
    async def probno(self, b, inter):
        if self.aki.progression <= 85:
            await self.aki.answer(akinator.Answer.ProbablyNot)
            emb = discord.Embed(title=f"{self.inter.author.display_name}'s Akinator Game!", description=f"**Question#{self.aki.step+1}:**\n{self.aki.question}", color=0xfcb8b8)
            await inter.response.edit_message(embed=emb)
        else:
            fg = await self.aki.win()
            if fg:
                emb = discord.Embed(title="My guess is...", description=f"**{fg.name}**\n{fg.description}\nRanked as: **#{fg.ranking}**", color=0xfcb8b8)
                emb.set_image(url=fg.absolute_picture_path)
                await inter.response.edit_message(embed=emb, view=None)


    @discord.ui.button(label="Go Back", style=discord.ButtonStyle.red)
    async def back(self, b, inter):
        try:
            await self.aki.back()
            emb = discord.Embed(title=f"{self.inter.author.display_name}'s Akinator Game!", description=f"**Question#{self.aki.step+1}:**\n{self.aki.question}", color=0xfcb8b8)
            await inter.response.edit_message(embed=emb)
        except akinator.CantGoBackAnyFurther:
            await inter.response.defer()