import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import sqlite3
import commands.free_chips as free_chips, commands.shop as shop, commands.buy as buy
import commands.addchips as addchips, commands.bal as bal, commands.mission as mission, commands.cards_team as cards_team
import commands.card as card, commands.cards as cards, commands.pull as pull, commands.show as show
import commands.equip as equip, commands.battle as battle

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

@client.command(name="all", help="See all cards", aliases=['a'])
async def view_all(ctx):
    await cards.carddd(ctx)
    
@client.command(name="addcard", help="Add a card to your collection")
async def addcardy(ctx, card_id: int):
    await card.add_card(ctx, card_id)

@client.command(name="pull", help="Pull a card", aliases=['p'])
async def pully(ctx, amount: str=None, special_amount: str=None):
    if amount is None:
        amount = 1
        await pull.pull(ctx, amount)
    elif amount.lower() == "all" or amount.lower() == "a":
        await pull.pull_all(ctx)
    elif amount.lower() == "special" or amount.lower() == "s":
        if special_amount is None:
            special_amount = 1
            await pull.special(ctx, int(special_amount))
        elif special_amount.lower() == "all" or special_amount.lower() == "a":
            await pull.special_all(ctx)
        else:
            await pull.special(ctx, int(special_amount))
    else:
        await pull.pull(ctx, int(amount))

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

@client.command(name="daily", help="Get 1000 chips once per day")
async def once_per_day(ctx):
    await free_chips.once_per_day(ctx)

@client.command(name="weekly", help="Get 5000 chips once per week")
async def once_per_day(ctx):
    await free_chips.once_per_week(ctx)

@client.command(name="buy", help="Buy an item from the shop")
async def buyy(ctx, *item: str):
    amount = 1
    item_name = ""
    for word in item:
        if word.isdigit():
            amount = int(word)
            break
        else:
            item_name += " " + word
    item_name = item_name.strip() # Remove leading/trailing spaces

    await buy.buy(ctx, item_name, amount)


conn = sqlite3.connect('db/inv.db')
conn_cards = sqlite3.connect('db/cards.db')

@client.command(name="inv", help="Check your inventory", aliases=['inventory'])
async def inv(ctx):
    user_id = str(ctx.author.id)
    c = conn.cursor()
    c.execute("SELECT * FROM inv WHERE user_id=?", (user_id,))
    row = c.fetchone()

    if row is None:
        await ctx.send("You don't have any items in your inventory.")
    elif all(val is None for val in row[1:]):
        await ctx.send("You don't have any items in your inventory.")
    else:
        # Create an embed message
        embeds = discord.Embed(title=f"**{ctx.author.name}'s inventory**", color=discord.Color.gold())

        # Loop through each item in the inventory and add it to the embed
        items = [
            'Truck kun',
            'Super Dragon Balls',
            'Death Note',
            'Sword of Rupture',
            'Truth Seeking Orbs',
            'Gun',
            'Murasame',
            'Dragon Slayer',
            'ODM Gear',
            'Super Tengen Toppa Gurren Lagann',
            'Spear of Longinus',
            'Lostvayne',
            'Katana',
            'Kunai',
            'Shuriken',
            'Eggplant'
        ]

        for item in items:
            amount = row[items.index(item) + 1]

            # Check if the item has a corresponding card
            c_cards = conn_cards.cursor()
            item_name = item.lower().replace(' ', '_').replace('-', '_')
            c_cards.execute("SELECT * FROM owned_cards WHERE item_id=?", (item_name,))
            card_rows = c_cards.fetchall()

            if amount is not None and amount > 0:
                item_str = f"Amount: {amount}"
                for card_row in card_rows:
                    #make a card_id list so it shows only how many have equiped and make diffrent command for seeing the ids
                    card_id = card_row[1]
                    if card_row[2] > 0:
                        item_str += f" | Equipped by Card id: {card_id}"
                embeds.add_field(name=item, value=item_str, inline=True)

        if len(embeds.fields) == 0:
            await ctx.send("You don't have any items in your inventory.")
        else:
            await ctx.send(embed=embeds)

@client.command(name="sell", help="Sell an item from your inventory")
async def selly(ctx, *item: str):
    amount = 1
    item_name = ""
    for word in item:
        if word.isdigit():
            amount = int(word)
            break
        else:
            item_name += " " + word
    item_name = item_name.strip() # Remove leading/trailing spaces

    await buy.sell(ctx, item_name, amount)

@client.command(name="shop", help="Use Larry coins to buy items")
async def shops(ctx, client=client):
    await shop.shopy(ctx, client)

@client.command(name="equip", help="Equip an item from your inventory")
async def equipy(ctx, card_id: int=None, *item_name: str):
    item_name = list(item_name)
    item_name = [x.lower() for x in item_name]
    await equip.equip(ctx, card_id, item_name)

@client.command(name="unequip", help="Unequip an item from your inventory")
async def unequipy(ctx, card_id: int=None):
    await equip.unequip(ctx, card_id)

@client.command(name="team", help="See your team")
async def teamy(ctx, option: str=None, card_id: int=None, client=client):
    await cards_team.team(ctx, option, card_id, client)

@client.command(name="battle", help="Battle another user")
async def battley(ctx, user: discord.User=None):
    await battle.battle(ctx, user)

client.run(os.getenv('token'))