from disnake.ext import commands
import disnake as discord
from db import Hanknyeon
from views.tictactoe import TicTacToeView
import random
from akinator import AsyncAkinator, Theme
from views.rps import RPS
from views.minesweeper import MineView
from views.memory import Memory
from views import SokobanView
from views.akinatorview import AkiView


aki_enum = commands.option_enum({"Character":"ch", "Object":"obj"})


class Fun(commands.Cog):
    def __init__(self, bot:Hanknyeon) -> None:
        self.bot = bot


    @commands.slash_command(description="Play a game of Tic Tace Toe!")
    async def tictactoe(self, inter):
        ch = random.choice((0, 1))
        await inter.response.defer()
        if ch:
            view = TicTacToeView(inter.author)
            await inter.edit_original_message("Your turn.", view=view)
            view.m = await inter.original_message() #type:ignore
        else:
            view = TicTacToeView(inter.author)
            await view.next_ai_move()
            await inter.edit_original_message("Your turn.", view=view)
            view.m = await inter.original_message() #type:ignore

    
    @commands.slash_command(description="Play a minesweeper game!")
    async def minesweeper(self, inter):
        await inter.response.defer()
        v = MineView(inter.author)
        v.bot = self.bot
        await inter.edit_original_message(f"{inter.author.display_name}'s minesweeper game...", view=v)


    @commands.slash_command(description="Play a round of Rock Paper and scissors with the bot!")
    async def rps(self, inter):
        embed = discord.Embed(title="An intense game of Rock, Paper and Scissors!", description="Select an option from below!", color=self.bot.get_color())
        v = RPS()
        v.bot = self.bot
        v.inter = inter
        await inter.send(embed=embed, view=v)


    @commands.slash_command(description="A traditional memory game")
    async def memory(self, inter):
        v = Memory()
        v.bot = self.bot
        v.inter = inter
        await inter.send(f"{inter.author}'s memory game", view=v)

    
    @commands.slash_command(description="A sokoban game")
    async def sokoban(self, inter):
        v = SokobanView()
        v.inter = inter
        v.bot = self.bot
        v.get_board()
        await inter.send(v.get_board(), view=v)


    @commands.slash_command(name="akinator", description="Let Haknyeon guess your character or an object!")
    async def akinato(self, inter, what_to_guess:aki_enum):
        await inter.response.defer()
        theme = Theme.Characters if what_to_guess=="ch" else Theme.Objects
        aki = AsyncAkinator(theme=theme)
        akiv = AkiView(aki)
        akiv.inter = inter
        await aki.start_game()
        emb = discord.Embed(title=f"{inter.author.display_name}'s Akinator Game!", description=f"**Question: {aki.step}:**\n{aki.question}", color=self.bot.get_color())
        await inter.edit_original_message(embed=emb, view=akiv)


def setup(bot: Hanknyeon):
    bot.add_cog(Fun(bot))