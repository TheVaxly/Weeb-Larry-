import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import commands.addchips as addchips, commands.bal as bal
import commands.card as card, commands.cards as cards, commands.pull as pull

load_dotenv()

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Anime Tiddies"))
    await client.tree.sync()

@client.command(name="cards", help="Check your cards")
async def view_cards(ctx, arg=None):
    if arg == "all":
        await cards.carddd(ctx)
    elif arg is None:
        await card.view_collection(ctx)
    else:
        return
    
@client.command(name="addcard", help="Add a card to your collection")
async def addcardy(ctx, card_id: int):
    await card.add_card(ctx, card_id)

@client.command(name="pull", help="Pull a card")
async def pully(ctx, amount: int=1):
    await pull.pull(ctx, amount)

@client.command(name='bal', help="Check your Blackjack balance")
async def balance(ctx):
    await bal.balance(ctx)

@client.command(name="addchips", help="Add chips to a user (Admin only)")
@commands.has_role('Cheats')
async def add_chipsy(ctx, amount: int=None):
    await addchips.add_chips(ctx, amount)

client.run(os.getenv('token'))