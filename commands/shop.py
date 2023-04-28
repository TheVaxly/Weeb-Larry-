import discord
from discord.ext import commands
import asyncio
import sqlite3

conn = sqlite3.connect("db/balances.db")

def get_balance(user_id):
    cursor = conn.execute("SELECT balance, special FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.execute("INSERT INTO balances (user_id, balance, special) VALUES (?, ?, ?)", (user_id, 1000, 0))
        conn.commit()
        return 1000, 0
    else:
        return row[0], row[1]

async def shopy(ctx, client):

    ryo = get_balance(ctx.author.id)[0]
    special = get_balance(ctx.author.id)[1]
    page_two = discord.Embed(title="**Gear Shop**", description="Items serve to multiply your card's power with the number in the brackets.", color=0x00ff00)
    page_two.add_field(name="══════════════════════════════", value="", inline=False)
    page_two.add_field(name="``Truck-kun - (3.25x)`` | 49999 special tickets", value="", inline=False)
    page_two.add_field(name="``Super Dragon Balls - (2.85x)`` | 9999 special tickets", value="", inline=False)
    page_two.add_field(name="``Death Note - (2.5x)`` | 4500 special tickets", value="", inline=False)
    page_two.add_field(name="``Sword of Rupture - (2.3x)`` | 3400 special tickets", value="", inline=False)
    page_two.add_field(name="``Truth Seeking Orbs - (2.2x)`` | 2400 special tickets", value="", inline=False)
    page_two.add_field(name="``Gun - (2x)`` | 1600 special tickets", value="", inline=False)
    page_two.add_field(name="``Murasame - (1.9x)`` | 900 special tickets", value="", inline=False)
    page_two.add_field(name="``Dragon Slayer - (1.8x)`` | 400 special tickets", value="", inline=False)
    page_two.add_field(name="``ODM gear - (1.7x)`` | 150 special tickets", value="", inline=False)
    page_two.add_field(name="══════════════════════════════", value="", inline=False)
    page_two.add_field(name="Use ``!buy <item name> <quantity>`` to purchase the item.\nUse ``!equip <ninja ID> <item name>`` to equip the item.\nUse ``!unequip <ninja ID>`` to unequip the item.\nUse ``!sell <item name> <quantity>`` to sell the item for 90% of the original price.", value="", inline=False)
    page_two.set_footer(text=f"Ryō: {ryo}\nSpecial tickets: {special}\nPage 2/2", icon_url=ctx.author.avatar)

    page_one = discord.Embed(title="**Gear Shop**", description="Items serve to multiply your card's power with the number in the brackets.", color=0x00ff00)
    page_one.add_field(name="══════════════════════════════", value="", inline=False)
    page_one.add_field(name="``Super Tengen Toppa Gurren Lagann - (2x)`` | 30000 ryō", value="", inline=False)
    page_one.add_field(name="``Spear Of Longinus - (1.5x)`` | 18000 ryō", value="", inline=False)
    page_one.add_field(name="``Lostvayne - (1.4x)`` | 12000 ryō", value="", inline=False)
    page_one.add_field(name="``Katana - (1.3x)`` | 9000 ryō", value="", inline=False)
    page_one.add_field(name="``Kunai - (1.2x)`` | 6000 ryō", value="", inline=False)
    page_one.add_field(name="``Shuriken - (1.15x)`` | 3000 ryō", value="", inline=False)
    page_one.add_field(name="``Eggplant - (1.1x)`` | 1500 ryō", value="", inline=False)
    page_one.add_field(name="══════════════════════════════", value="", inline=False)
    page_one.add_field(name="Use ``!buy <item name> <quantity>`` to purchase the item.\nUse ``!equip <ninja ID> <item name>`` to equip the item.\nUse ``!unequip <ninja ID>`` to unequip the item.\nUse ``!sell <item name> <quantity>`` to sell the item for 90% of the original price.", value="", inline=False)
    page_one.set_footer(text=f"Ryō: {ryo}\nSpecial tickets: {special}\nPage 1/2", icon_url=ctx.author.avatar)


    pages = [page_one, page_two]

    message = await ctx.send(embed=page_one)
    current_page = 0
    await message.add_reaction('⬅️')
    await message.add_reaction('➡️')

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == '➡️':
                current_page += 1
                await message.edit(embed=pages[current_page])
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '⬅️':
                current_page -= 1
                await message.edit(embed=pages[current_page])
                await message.remove_reaction(reaction, user)

            else:
                await message.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            await message.clear_reactions()
            break