import disnake as discord


class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.value = None


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        if self.inter.author.id != inter.author.id: #type:ignore
            return await inter.send("You can't use that!")
        await inter.response.defer()
        self.value = True
        self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        if self.inter.author.id != inter.author.id: #type:ignore
            return await inter.send("You can't use that!")
        await inter.response.defer()
        self.value = False
        self.stop()


    async def on_timeout(self):
        for child in self.children:
            child.disabled=True
        await self.inter.edit_original_message(view=self)