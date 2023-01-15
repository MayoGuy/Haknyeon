import disnake as discord


class MenuSelect(discord.ui.Select):
    def __init__(self, ids):
        self.ids = ids
        options = []
        for id in ids:
            options.append(discord.SelectOption(
                label = id,
                value = id
            ))
        super().__init__(
            placeholder="Select the cards to add into the list",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, inter):
        self.view: SelectPages
        for v in self.values:
            self.view.selected_ids.append(v)
        if len(self.view.selected_ids) == 5:
            self.disabled = True
            self.view.confirm.disabled = False
            self.view.next_page.disabled = True
            self.view.prev_page.disabled = True
        await inter.response.edit_message(embed=discord.Embed(title="Binder Creation", description=f"**Selected Cards: **\n-" + "\n-".join(id for id in self.view.selected_ids), color=0xfcb8b8), view=self.view)


class SelectPages(discord.ui.View):
    def __init__(self, ids):
        super().__init__(timeout=60)
        self.ids = ids
        self.index = 0
        self.selected_ids = []
        self.selects = []
        for id in range(0, len(ids), 25):
            nl = ids[id:id+25]
            for n in nl:
                if nl.count(n) > 1:
                    nl.remove(n)
            self.selects.append(MenuSelect(nl))
        self.add_item(self.selects[0])
        self.confirm.disabled = True
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
        print("\n".join([l.label for l in self.selects[self.index].options]) + "\nblock")
        await inter.response.edit_message(view=self)

    
    async def on_timeout(self):
        for child in self.children:
            child.disabled = True  #type:ignore
        await self.inter.edit_original_message(view=self)  #type:ignore


    @discord.ui.button(label="Undo Selection", style=discord.ButtonStyle.blurple)
    async def undo(self, b, inter):
        self.confirm.disabled = True
        self.next_page.disabled = False
        self.prev_page.disabled = False
        self._update_state()
        self.selected_ids.pop()
        self.selects[self.index].disabled = False
        await inter.response.edit_message(embed=discord.Embed(title="Binder Creation", description=f"**Selected Cards: **\n-" + "\n-".join(id for id in self.selected_ids), color=0xfcb8b8), view=self)


    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button, inter):
        await inter.response.edit_message(embed=discord.Embed(title="Binder Successfully Created!", description=f"**Selected Cards: **\n-" + "\n-".join(id for id in self.selected_ids), color=0xfcb8b8), view=None)
        self.value = True
        self.stop()


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button, inter):
        await inter.response.edit_message(embed=discord.Embed(description="<:HN_X:1035085573104345098> You cancelled your binder creation!", color=0xfcb8b8), view=None)
        self.value = False
        self.stop()