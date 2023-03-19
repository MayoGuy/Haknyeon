import disnake as discord
import random
import asyncio


class Menu(discord.ui.View):
    def __init__(self, embeds, files=None):
        super().__init__(timeout=30)
        self.files=files
        self.embeds = embeds
        self.index = 0
        self.remove.label = f"Page 1/{len(self.embeds)}"
        self._update_state()
        if len(self.embeds) < 3:
            self.skip_page.disabled = True


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


    def _update_state(self) -> None:
        self.first_page.disabled = self.prev_page.disabled = self.index == 0
        self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1
        self.remove.label = f"Page {self.index + 1}/{len(self.embeds)}"
        if self.files:
            self.first_page.disabled = True
            self.prev_page.disabled = True


    @discord.ui.button(emoji="<:HN_Rewind:1035179518400405605>", style=discord.ButtonStyle.gray)
    async def first_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index = 0
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            file = discord.File(self.files[self.index], "image.png")
            self.embeds[self.index].set_image(file=file)
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)


    @discord.ui.button(emoji="<:HN_ArrowLeft:1035177424947773541>", style=discord.ButtonStyle.gray)
    async def prev_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index -= 1
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            file = discord.File(self.files[self.index], "image.png")
            self.embeds[self.index].set_image(file=file)
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)


    @discord.ui.button(label="Page 1", style=discord.ButtonStyle.grey, disabled=True)
    async def remove(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        pass

    @discord.ui.button(emoji="<:HN_ArrowRight:1035177472179830875>", style=discord.ButtonStyle.gray)
    async def next_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index += 1
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            file = discord.File(self.files[self.index], "image.png")
            self.embeds[self.index].set_image(file=file)
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(emoji="<:HN_FastForward:1035179433004371999>", style=discord.ButtonStyle.gray)
    async def last_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index = len(self.embeds) - 1
        self._update_state()
        if not self.files:
            await inter.response.edit_message(embed=self.embeds[self.index], view=self,)
        else:
            file = discord.File(self.files[self.index], "image.png")
            self.embeds[self.index].set_image(file=file)
            await inter.response.edit_message(embed=self.embeds[self.index], view=self)


    @discord.ui.button(label="Skip to page", style=discord.ButtonStyle.gray)
    async def skip_page(self, b, inter:discord.MessageInteraction):
        ran = random.randint(0, 10000000)
        print(ran)
        await inter.response.send_modal(
            title="Skip to page",
            custom_id=f"page_skip_{ran}",
            components=[
                discord.ui.TextInput(
                    label="Page Number",
                    placeholder=f"Enter a number between 1 and {len(self.embeds)}",
                    custom_id=f"name_skip_{ran}",
                    style=discord.TextInputStyle.single_line,
                    min_length=1,
                    max_length=len(str(len(self.embeds))),
                ),
            ]
        )
        try:
            modal_inter: discord.ModalInteraction = await self.inter.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == f"page_skip_{ran}" and i.author.id == inter.author.id,
                timeout=30,
        )
        except asyncio.TimeoutError:
            return
        page = modal_inter.text_values[f"name_skip_{ran}"]
        try:
            int(page)
        except:
            return await modal_inter.response.send_message("Not a valid integer!", ephemeral=True)
        if int(page) in list(range(1, len(self.embeds))):
            self.index = int(page)-1
            self._update_state()
            await modal_inter.response.edit_message(embed=self.embeds[self.index], view=self)
    

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True  #type:ignore
        await self.inter.edit_original_message(view=self)  #type:ignore
        del self.embeds
        if self.files:
            del self.files


class MenuSelect(discord.ui.Select):
    def __init__(self, ids):
        self.ids = ids
        options = []
        for id in ids:
            options.append(discord.SelectOption(
                label = id
            ))
        super().__init__(
            placeholder="Select the cards to add into your folder...",
            min_values=1,
            max_values=len(ids),
            options=options
        )

    async def callback(self, inter):
        for v in self.values:
            if not v in self.view.ids:
                self.view.ids.append(v)
        await inter.response.edit_message(embed=discord.Embed(title="Select cards from dropdown menu", description=f"**Folder Name: **{self.view.fdn}\n\n**Selected Cards: **\n-" + "\n-".join(id for id in self.view.ids), color=0xfcb8b8))


class SelectPages(discord.ui.View):
    def __init__(self, ids, fdn):
        super().__init__(timeout=60)
        self.fids = ids
        self.ids = []
        self.index = 0
        self.selected_ids = []
        self.fdn = fdn
        self.selects = []
        for id in range(0, len(ids), 25):
            nl = ids[id:id+25]
            print(nl)
            self.selects.append(MenuSelect(nl))
        self.add_item(self.selects[0])
        self._update_state()


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


    def _update_state(self) -> None:
        self.prev_page.disabled = self.index == 0
        self.next_page.disabled = self.index == len(self.selects) - 1
        self.remove.label = f"Page {self.index + 1}/{len(self.selects)}"


    def remove_select(self):
        for child in self.children:
            if isinstance(child, MenuSelect):
                self.remove_item(child)
                break   
        self.add_item(self.selects[self.index])

    
    @discord.ui.button(emoji="<:HN_ArrowLeft:1035177424947773541>", style=discord.ButtonStyle.gray)
    async def prev_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index -= 1
        self._update_state()
        self.remove_select()
        await inter.response.edit_message(view=self)

    
    @discord.ui.button(label="Page 1", style=discord.ButtonStyle.grey, disabled=True)
    async def remove(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        pass

    
    @discord.ui.button(emoji="<:HN_ArrowRight:1035177472179830875>", style=discord.ButtonStyle.gray)
    async def next_page(self, button: discord.ui.Button, inter: discord.MessageInteraction):
        self.index += 1
        self._update_state()
        self.remove_select()
        await inter.response.edit_message(view=self)

    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True  #type:ignore
        await self.inter.edit_original_message(view=self)  #type:ignore


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button, inter):
        await inter.response.edit_message(embed=discord.Embed(title="Task Successfully completed!", description=f"**Folder Name: **{self.fdn}\n\n**Selected Cards: **\n-" + "\n-".join(id for id in self.ids), color=0xfcb8b8), view=None)
        self.value = True
        self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button, inter):
        await inter.response.edit_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled this your folder creation!", color=0xfcb8b8), view=None)
        self.value = False
        self.stop()



    