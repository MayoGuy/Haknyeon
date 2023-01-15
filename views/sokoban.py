import disnake as discord
import random


class SokobanView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.board = [
            ["<:200:850334736769482783>", "<:200:850334736769482783>", "<:200:850334736769482783>", "<:200:850334736769482783>","<:200:850334736769482783>", "<:200:850334736769482783>", "<:200:850334736769482783>"],
            ["<:200:850334736769482783>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>","<:greenbg:850329478022299648>" "<:200:850334736769482783>"],
            ["<:200:850334736769482783>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>","<:greenbg:850329478022299648>" "<:200:850334736769482783>"],
            ["<:200:850334736769482783>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>","<:greenbg:850329478022299648>" "<:200:850334736769482783>"],
            ["<:200:850334736769482783>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>","<:greenbg:850329478022299648>" "<:200:850334736769482783>"],
            ["<:200:850334736769482783>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>", "<:greenbg:850329478022299648>","<:greenbg:850329478022299648>" "<:200:850334736769482783>"],
            ["<:200:850334736769482783>", "<:200:850334736769482783>", "<:200:850334736769482783>", "<:200:850334736769482783>","<:200:850334736769482783>", "<:200:850334736769482783>", "<:200:850334736769482783>"]
        ]
        self.curr_pos = self.new_pos([])
        self.box_pos = self.new_pos([self.curr_pos], box=True)
        self.cross_pos = self.new_pos([self.curr_pos, self.box_pos])


    def new_pos(self,p, box=False):
        if not box:
            x = [random.randint(1,5), random.randint(1,5)]
        else:
            x = [random.randint(2,4), random.randint(2,4)]
        for pos in p:
            if pos == x:
                self.new_pos(p)
        return x


    def move(self, action):
        if action == "up" and self.curr_pos[0] > 1:
            self.board[self.curr_pos[0]][self.curr_pos[1]] = "<:greenbg:850329478022299648>"
            if self.board[self.curr_pos[0]-1][self.curr_pos[1]] == "<:box:850336337420615700>" and self.box_pos[0]-1 > 0:
                self.curr_pos[0] -= 1
                self.box_pos[0] -= 1
            else:
                self.curr_pos[0] -= 1
        elif action == "down" and self.curr_pos[0] < 5:
            self.board[self.curr_pos[0]][self.curr_pos[1]] = "<:greenbg:850329478022299648>"
            if self.board[self.curr_pos[0]+1][self.curr_pos[1]] == "<:box:850336337420615700>" and self.box_pos[0]-1 < 6:
                self.curr_pos[0] += 1
                self.box_pos[0] += 1
            else:
                self.curr_pos[0] += 1
        elif action == "r" and self.curr_pos[1] < 5:
            self.board[self.curr_pos[0]][self.curr_pos[1]] = "<:greenbg:850329478022299648>"
            if self.board[self.curr_pos[0]][self.curr_pos[1]+1] == "<:box:850336337420615700>" and self.box_pos[1]+1 < 6:
                self.curr_pos[1] += 1
                self.box_pos[1] += 1
            else:
                self.curr_pos[1] += 1
        elif action == "l" and self.curr_pos[1] > 1:
            self.board[self.curr_pos[0]][self.curr_pos[1]] = "<:greenbg:850329478022299648>"
            if self.board[self.curr_pos[0]][self.curr_pos[1]-1] == "<:box:850336337420615700>" and self.box_pos[1]-1 > 0:
                self.curr_pos[1] -= 1
                self.box_pos[1] -= 1
            else:
                self.curr_pos[1] -= 1

    
    def get_board(self):
        try:
            self.board[1][6] = "<:200:850334736769482783>"
        except:
            self.board[1].append(" ")
        try:
            self.board[2][6] = "<:200:850334736769482783>"
        except:
            self.board[2].append(" ")
        try:
            self.board[3][6] = "<:200:850334736769482783>"
        except:
            self.board[3].append(" ")
        try:
            self.board[4][6] = "<:200:850334736769482783>"
        except:
            self.board[4].append(" ")
        try:
            self.board[5][6] = "<:200:850334736769482783>"
        except:
            self.board[5].append(" ")
        self.board[self.cross_pos[0]][self.cross_pos[1]] = "<:cross:850337959609106452>"
        self.board[self.box_pos[0]][self.box_pos[1]] = "<:box:850336337420615700>"
        self.board[self.curr_pos[0]][self.curr_pos[1]] = "<:man:850333572794548286>"
        
        _map = ""
        for y in self.board:
            for x in y:
                _map += str(x)
            _map += "\n"
        return _map

    
    def check_win(self):
        if self.box_pos == self.cross_pos:
            return True
        else:
            return False


    def disable_all(self):
        for child in self.children:
            if not child.label == "Next Game":
                child.disabled = True

    
    @discord.ui.button(label=" ", disabled=True)
    async def dis1(self, b, inter):
        pass

    
    @discord.ui.button(label="Up", style=discord.ButtonStyle.blurple)
    async def up(self, b, inter):
        self.move("up")
        board = self.get_board()
        if self.check_win():
            self.disable_all()
            pts = random.randint(1, 5)
            await self.bot.add_coins(self.inter.author.id, pts)
            await inter.response.edit_message(content=f"You win! ({pts} {self.bot.petal})\n" + board, view=self)
        else:
            await inter.response.edit_message(content=board)


    @discord.ui.button(label=" ", disabled=True)
    async def dis2(self, b, inter):
        pass
        

    @discord.ui.button(label=" ", disabled=True)
    async def dis3(self, b, inter):
        pass


    @discord.ui.button(label="Next Game", style=discord.ButtonStyle.green)
    async def next(self, b, inter):
        self.board[self.curr_pos[0]][self.curr_pos[1]] = "<:greenbg:850329478022299648>"
        self.board[self.box_pos[0]][self.box_pos[1]] = "<:greenbg:850329478022299648>"
        self.board[self.cross_pos[0]][self.cross_pos[1]] = "<:greenbg:850329478022299648>"
        self.curr_pos = self.new_pos([])
        self.box_pos = self.new_pos([self.curr_pos], box=True)
        self.cross_pos = self.new_pos([self.curr_pos, self.box_pos])
        for child in self.children:
            if not child.label == " ":
                child.disabled = False
        await inter.response.edit_message(content=self.get_board(), view=self)


    @discord.ui.button(label="Left", style=discord.ButtonStyle.blurple)
    async def left(self, b, inter):
        self.move("l")
        board = self.get_board()
        if self.check_win():
            self.disable_all()
            pts = random.randint(1, 5)
            await self.bot.add_coins(self.inter.author.id, pts)
            await inter.response.edit_message(content=f"You win! ({pts} {self.bot.petal})\n" + board, view=self)
        else:
            await inter.response.edit_message(content=board)


    @discord.ui.button(label="Down", style=discord.ButtonStyle.blurple)
    async def down(self, b, inter):
        self.move("down")
        board = self.get_board()
        if self.check_win():
            self.disable_all()
            pts = random.randint(1, 5)
            await self.bot.add_coins(self.inter.author.id, pts)
            await inter.response.edit_message(content=f"You win! ({pts} {self.bot.petal})\n" + board, view=self)
        else:
            await inter.response.edit_message(content=board)
    

    @discord.ui.button(label="Right", style=discord.ButtonStyle.blurple)
    async def right(self, b, inter):
        self.move("r")
        board = self.get_board()
        if self.check_win():
            self.disable_all()
            pts = random.randint(1, 5)
            await self.bot.add_coins(self.inter.author.id, pts)
            await inter.response.edit_message(content=f"You win! ({pts} {self.bot.petal})\n" + board, view=self)
        else:
            await inter.response.edit_message(content=board)


    @discord.ui.button(label=" ", disabled=True)
    async def dis4(self, b, inter):
        pass
        
    @discord.ui.button(label="Exit", style=discord.ButtonStyle.red)
    async def exit(self, b, inter):
        self.clear_items()
        await inter.response.edit_message(view=self)