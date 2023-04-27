import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import commands.addchips as addchips, commands.bal as bal, commands.mission as mission, commands.pull_all as pull_all
import commands.card as card, commands.cards as cards, commands.pull as pull, commands.show as show

load_dotenv()

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Anime Tiddies"))
    await client.tree.sync()

@client.command(name="cards", help="Check your cards", aliases=['c'])
async def view_cards(ctx):
    await card.view_collection(ctx)

@client.command(name="pullall", help="Pull all cards", aliases=['pa'])
async def pull_all_cards(ctx):
    await pull_all.pull(ctx)

@client.command(name="all", help="See all cards", aliases=['a'])
async def view_all(ctx):
    await cards.carddd(ctx)
    
@client.command(name="addcard", help="Add a card to your collection")
async def addcardy(ctx, card_id: int):
    await card.add_card(ctx, card_id)

@client.command(name="pull", help="Pull a card", aliases=['p'])
async def pully(ctx, amount: int=None):
    if amount is None:
        amount = 1
        await pull.pull(ctx, amount)
    else:
        await pull.pull(ctx, amount)

@client.command(name='bal', help="Check your Blackjack balance", aliases=['balance'])
async def balance(ctx):
    await bal.balance(ctx)

@client.command(name="addchips", help="Add chips to a user (Admin only)", aliases=['adc'])
@commands.has_role('Cheats')
async def add_chipsy(ctx, amount: int=None):
    await addchips.add_chips(ctx, amount)

@client.command(name="quiz", help="Do anime related missions", aliases=['q'])
async def missiony(ctx, client=client):
    await mission.mission(ctx, client)

@client.command(name="show", help="Show specific card", aliases=['sh'])
async def showy(ctx, card_id: int=None):
    if card_id == None:
        await ctx.send("Please enter a card ID")
    else:
        await show.show(ctx, card_id)

client.run(os.getenv('token'))