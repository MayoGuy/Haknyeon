import disnake as discord
import aiohttp
import asyncio

class TicTacToeButton(discord.ui.Button):
    def __init__(self, x, y, row):
        self.x = x
        self.y = y
        super().__init__(label=" ", style=discord.ButtonStyle.blurple, row=row)

    async def callback(self, inter):
        if not inter.author==self.view.user:
            return await inter.senf("You aren't playing this game!", ephemeral=True)
        self.disabled = True
        self.view.board[self.x][self.y] = "O"
        self.label = "O"
        self.view.disable()
        await inter.response.edit_message(content="Please Wait...", view=self.view)
        await asyncio.sleep(1)
        for child in self.view.children:
            if child.label not in ("O", "X"):
                child.disabled=False
        win = self.view.check_winner()
        if win:
            return await inter.edit_original_message(content=win, view=self.view)
        await self.view.next_ai_move()
        await inter.edit_original_message(content="Your Turn.", view=self.view)
        win = self.view.check_winner()
        if win:
            return await inter.edit_original_message(content=win, view=self.view)
            

class TicTacToeView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user
        self.board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, x))

    async def on_timeout(self):
        self.disable()
        await self.m.edit(view=self)
    
    def disable(self, xy=None):
        if xy!=None:
            for x, y in xy:
                for child in self.children:    
                    if (x, y) == (child.x, child.y):
                        
                        child.style = discord.ButtonStyle.red
                    child.disabled = True
        else:
            for child in self.children:
                child.disabled = True
    
    async def next_ai_move(self):
        async with aiohttp.ClientSession() as cs:
            board = "".join(x for sl in self.board for x in sl)
            headers = {
	        "X-RapidAPI-Key": "63648f2ab3msh712b3acd2ca0ff5p13d5e9jsne0bb2c00a482",
	        "X-RapidAPI-Host": "stujo-tic-tac-toe-stujo-v1.p.rapidapi.com"
            }
            async with cs.get(url=f"https://stujo-tic-tac-toe-stujo-v1.p.rapidapi.com/{board}/X", headers=headers) as r:
                data = await r.json()
                rec = data["recommendation"]
                x, y = divmod(rec, 3)
                self.board[x][y] = "X"
                for b in self.children:
                    if (x, y) == (b.x, b.y):
                        b.label = "X"
                        b.disabled = True

    def check_winner(self):
        tuples = self.board
        for line in range(3):
            if tuples[line][0] == tuples[line][1] == tuples[line][2] != "-":
                self.disable(xy=((line, 0), (line, 1), (line, 2)))
                return tuples[line][0] + " Won!"
            if tuples[0][line] == tuples[1][line] == tuples[2][line] != "-":
                self.disable(xy=((0, line), (1, line), (2, line)))
                return tuples[0][line] + " Won!"
                
        if tuples[0][0] == tuples[1][1] == tuples[2][2] != "-":
            self.disable(xy=((0,0), (1,1), (2,2)))
            return tuples[0][0] + " Won!"
            
        if tuples[0][2] == tuples[1][1] == tuples[2][0] != "-":
            self.disable(xy=((0,2), (1,1), (2,0)))
            return tuples[2][0] + " Won!"
            
        if not any("-" in nl for nl in self.board):
            self.disable()
            return "It's a Tie!"
        return None

    