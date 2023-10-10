import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import sqlite3
import asyncio
import commands.free_chips as free_chips, commands.shop as shop, commands.buy as buy
import commands.addchips as addchips, commands.bal as bal, commands.mission as mission, commands.cards_team as cards_team
import commands.card as card, commands.cards as cards, commands.pull as pull, commands.show as show
import commands.equip as equip, commands.battle as battle
   

load_dotenv()

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

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
    
@client.command(name="addcard", help="Add a card to your collection (Admin only)", aliases=['ac'])
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
async def add_chipsy(ctx, amount: int=None, user: discord.Member=None):
    if amount == None:
        await addchips.add_chips(ctx, amount)
    else:
        await addchips.add_chips(ctx, amount, user)

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
            'Mogus',
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
    if len(item) == 0:
        await ctx.send("Please enter an item to sell")
        return
    amount = 1
    item_name = ""
    for word in item:
        if word.isdigit():
            amount = int(word)
            break
        else:
            item_name += " " + word
    item_name = item_name.strip()

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

@client.command(name="help", help="Shows this message")
async def help(ctx, command: str = None):
    if command is None:
        embed = discord.Embed(title="Weeb Larry commands", color=16750592, description="The prefix is ! and is not currently changeable!\nUse !help <command> for more info on a specific command!")

        income_commands = {
            "addcard (Admin only)": "Add a card to your collection",
            "addchips (Admin only)": "Add chips to a user",
            "bal": "Check your Blackjack balance",
            "battle": "Battle another user",
            "daily": "Get 1000 chips once per day",
            "quiz": "Do anime-related missions",
            "weekly": "Get 5000 chips once per week"
        }

        card_commands = {
            "pull": "Gacha the cards",
            "team": "See your team",
            "show": "Show a specific card",
            "all": "See all cards",
            "cards": "Check your cards"
        }

        gear_commands = {
            "shop": "Buy items",
            "inv": "Check your inventory",
            "buy": "Buy an item from the shop",
            "sell": "Sell an item from your inventory",
            "equip": "Equip an item from your inventory",
            "unequip": "Unequip an item from your inventory"
        }

        other_commands = {
            "help": "Shows this message",
        }

        income_commands_list = "\n".join(f"- **{cmd}**: {desc}" for cmd, desc in income_commands.items())
        card_commands_list = "\n".join(f"- **{cmd}**: {desc}" for cmd, desc in card_commands.items())
        gear_commands_list = "\n".join(f"- **{cmd}**: {desc}" for cmd, desc in gear_commands.items())

        embed.add_field(name=":money_mouth: Income", value=income_commands_list, inline=False)
        embed.add_field(name=":credit_card: Cards", value=card_commands_list, inline=False)
        embed.add_field(name=":crossed_swords: Gear", value=gear_commands_list, inline=False)
        embed.add_field(name=":question: Other", value="\n".join(f"- **{cmd}**: {desc}" for cmd, desc in other_commands.items()), inline=False)

        await ctx.send(embed=embed)
    else:

        await ctx.send(f"Command **{command}** doesen't have help yet **{ctx.author.name}!**")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.HTTPException):
        if error.status == 429:

            retry_after = error.retry_after
            print(f'Rate limited. Retrying after {retry_after} seconds.')
            await asyncio.sleep(retry_after)
            await ctx.reinvoke() 
    else:

        pass

import requests
import random
from bs4 import BeautifulSoup

def get_random_doujin(tag):
    try:

        tag_url = f'https://asmhentai.com/tag/{tag}/'
        response = requests.get(tag_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        pagination = soup.find('ul', class_='pagination')
        pages = pagination.find_all('li', class_='page-item')
        highest_page = max([int(page.find('a').text) for page in pages if page.find('a').text.isdigit()])

        page_number = random.randint(1, highest_page)
        tag_url = f'https://asmhentai.com/tag/{tag}/?page={page_number}'

        response = requests.get(tag_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        doujin_divs = soup.find_all('div', class_='image')

        doujin_urls = []
        for div in doujin_divs:
            a_element = div.find('a', href=True)
            if a_element and 'href' in a_element.attrs:
                doujin_url = f"https://asmhentai.com{a_element['href']}"
                doujin_urls.append(doujin_url)

        if not doujin_urls:
            return "No doujins found for the provided tag.", None

        random_doujin_url = random.choice(doujin_urls)
        return None, random_doujin_url, highest_page

    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching doujins: {e}", None

    except Exception as e:
        return f"An error occurred while parsing doujins: {e}", None


@client.command(name='doujin', help='Get a random doujin for the provided tag', aliases=['d'])
async def doujin(ctx, *, tag: str):
    tags = tag.lower()
    tags = tags.replace(' ', '-')
    error_message, doujin_url, page = get_random_doujin(tags)
    if error_message:
        await ctx.send(error_message)
    else:
        try:
            response = requests.get(doujin_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            cover_img = soup.find('div', class_='cover').find('img', class_='lazy')
            cover_img_url = cover_img['data-src']
            cover_img_url = cover_img_url.replace('//', 'https://')
            doujin_title = cover_img['alt']

            embed = discord.Embed(title=doujin_title, color=discord.Color.dark_purple())
            embed.add_field(name="", value=f"URL: {doujin_url}", inline=False)
            embed.set_image(url=cover_img_url)
            embed.set_footer(text=f"Tag: {tag} ({page*20})\nRequested by {ctx.author.name}", icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)

        except requests.exceptions.RequestException as e:
            await ctx.send(f"An error occurred while fetching the doujin image: {e}")

        except Exception as e:
            await ctx.send(f"An error occurred while parsing the doujin page: {e}")

from bs4 import BeautifulSoup
import re

@client.command(name='read', help='Read a doujin by code', aliases=['r'])
async def read(ctx, code: str):
    try:
        doujin_url = f"https://asmhentai.com/gallery/{code}/1/"
        response = requests.get(doujin_url)
        if response.status_code == 404:
            await ctx.send(f"Could not find the doujin")
            return
        soup = BeautifulSoup(response.content, 'html.parser')
        page_img = soup.find('a', class_='fw_img').find('img', class_='lazy')
        page_img_url = page_img['data-src']

        page_button = soup.find('button', class_='pages_btn')
        page_text = page_button.find('span', class_='tp').text

        max_page = re.search(r'\d+', page_text).group()

        max_page = int(max_page)

        doujin_url2 = f"https://asmhentai.com/g/{code}/"

        response = requests.get(doujin_url2)
        soupa = BeautifulSoup(response.content, 'html.parser')

        title_tag = soupa.find('title')

        if title_tag:
            doujin_title = title_tag.text.strip()
        else:
            raise Exception("Could not find the doujin title")

        for i in range(1, max_page):
            doujin_url = f"https://asmhentai.com/gallery/{code}/{i}/"
            response = requests.get(doujin_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            page_img = soup.find('a', class_='fw_img').find('img', class_='lazy')
            page_img_url = page_img['data-src']

            embed = discord.Embed(title=f"**{doujin_title}**", color=discord.Color.dark_purple())
            embed.add_field(name="", value=f"**Sauce: {code}**", inline=False)
            embed.set_image(url=page_img_url)
            embed.set_footer(text=f"Read by {ctx.author.name}", icon_url=ctx.author.avatar)
            
            await ctx.send(embed=embed)
            
    except requests.exceptions.RequestException as e:
        await ctx.send(f"An error occurred while fetching the doujin page: {e}")

    except Exception as e:
        await ctx.send(f"An error occurred while parsing the doujin page: {e}")

client.run(os.getenv('token'))