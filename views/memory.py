import disnake as discord
import random
import asyncio


class MemoryButton(discord.ui.Button):
    def __init__(self, emoji):
        super().__init__(style=discord.ButtonStyle.blurple, label="\u200b")
        self.emoj = emoji[:-1]
        self.value = emoji
        self.closed = False

    
    async def callback(self, inter: discord.MessageInteraction, /):
        view: Memory = self.view
        if self.emoj == "🎉":
            self.disabled = True
            self.emoji = self.emoj
            self.closed = True
            view.closed.append(self.value)
            await inter.response.edit_message(view=view)
            return
        if not view.prev:
            view.prev = self
            self.disabled = True
            self.emoji = self.emoj
            await inter.response.edit_message(view=view)
        else:
            if view.prev.emoj != self.emoj:
                self.emoji = self.emoj
                view.disable_all()
                await inter.response.edit_message(view=view)
                await asyncio.sleep(2)
                self.emoji = None
                self.label = "\u200b"
                view.prev.emoji = None
                view.prev.label = "\u200b"
                view.enable_all()
                await inter.edit_original_message(view=view)
            else:
                self.emoji = self.emoj
                self.disabled = True
                await inter.response.edit_message(view=view)
                view.closed.append(view.prev.value)
                view.closed.append(self.value)
                self.closed = True
                view.prev.closed = True
            view.prev = None
        f = view.checkwin()
        if f:
            pts = random.randint(50, 75)
            await view.bot.add_coins(view.inter.author.id, pts)
            await inter.edit_original_message(content=f"You won! ({pts} {view.bot.petal})")


class Memory(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.elist = ['😈1', '😳1', '👾1', '😍1', '😜1', '🙄1', '🥺1', '😱1', '😴1', '😄1', '🤣1', '😡1', '😈2', '😳2', '👾2', '😍2', '😜2', '🙄2', '🥺2', '😱2', '😴2', '😄2', '🤣2', '😡2', '🎉1']
        random.shuffle(self.elist)
        for e in self.elist:
            self.add_item(MemoryButton(e))
        self.prev: MemoryButton = None
        self.closed = []
    
    def disable_all(self):
        for child in self.children:
            child.disabled = True
    
    
    def enable_all(self):
        for child in self.children:
            if not child.value in self.closed:
                child.disabled = False
    

    def checkwin(self):
        for e in self.children:
            if not e.closed:
                return False
        return True
