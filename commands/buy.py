import discord
import sqlite3
import commands.equip as equip

# Create the database connection
conn = sqlite3.connect('db/inv.db')
conn.execute('CREATE TABLE IF NOT EXISTS inv (user_id INTEGER PRIMARY KEY, truck_kun INTEGER, super_dragon_balls INTEGER, death_note INTEGER, sword_of_rupture INTEGER, truth_seeking_orbs INTEGER, gun INTEGER, surasame INTEGER, dragon_slayer INTEGER, odm_gear INTEGER, super_tengen_toppa_gurren_lagann INTEGER, spear_of_longinus INTEGER, lostvayne INTEGER, katana INTEGER, kunai INTEGER, shuriken INTEGER, eggplant INTEGER)')
conn.commit()

conn_bal = sqlite3.connect('db/balances.db')

TICKETS_ITEMS = {
    'truck_kun': 49999,
    'super_dragon_balls': 9999,
    'death_note': 4500,
    'sword_of_rupture': 3400,
    'truth_seeking_orbs': 2400,
    'gun': 1600,
    'murasame': 900,
    'dragon_slayer': 400,
    'odm_gear': 150,
}

CHIP_ITEMS = {
    'super_tengen_toppa_gurren_lagann': 30000,
    'spear_of_longinus': 18000,
    'lostvayne': 12000,
    'katana': 9000,
    'kunai': 6000,
    'shuriken': 3000,
    'eggplant': 1500,
}

ALL_ITEMS = {
    **TICKETS_ITEMS,
    **CHIP_ITEMS,
}



def inv_add(user_id, item, amount):
    conn = sqlite3.connect('db/inv.db')
    c = conn.cursor()
    ITEMS = ALL_ITEMS

    # Check if the row exists in the database
    c.execute("SELECT * FROM inv WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    # If the row doesn't exist, insert a new row with a value of 0 for every item
    if not row:
        values = ', '.join('?' for _ in ITEMS)
        c.execute(f"INSERT INTO inv (user_id, {', '.join(ITEMS)}) VALUES (?, {values})", (user_id, *(0 for _ in ITEMS)))
        conn.commit()

    # Add the amount to the item in the inventory
    c.execute(f"UPDATE inv SET {item} = {item} + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()

    conn.close()

async def buy(ctx, item: str, amount: int):
    # Get the user's balance from the database
    original_item = []
    original_item.append(item)
    item = item.lower().replace(' ', '_').replace('-', '_')
    user_id = str(ctx.author.id)

    # Check if the item exists and the user has enough balance
    if item not in CHIP_ITEMS and item not in TICKETS_ITEMS:
        await ctx.send(f"{item} is not a valid item.")
        return
    if item in CHIP_ITEMS:
        ITEMS = CHIP_ITEMS
        column = 'balance'
        currency = 'Ryō'
    elif item in TICKETS_ITEMS:
        ITEMS = TICKETS_ITEMS
        column = 'special'
        currency = 'Special Tickets'
    price = ITEMS[item] * amount
    c = conn_bal.cursor()
    c.execute(f"SELECT {column} FROM balances WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row is None:
        conn_bal.execute(f"INSERT INTO balances (user_id, {column}) VALUES (?, ?)", (user_id, 0))
        conn_bal.commit()
        return 0
    balance = row[0]
    if balance < price:
        await ctx.send(f"**{ctx.author.name}** does not have enough {currency} to buy {amount} {original_item[0]}.")
        return

    # Update the user's balance and inventory in the database
    new_balance = balance - price
    c.execute(f"UPDATE balances SET {column}=? WHERE user_id=?", (new_balance, user_id))
    inv_add(user_id, item, amount)
    conn_bal.commit()

    # Send a confirmation message
    embed=discord.Embed(title="Success", description=f"You have bought {amount} {original_item[0]} for {price} {currency}", color=0x00ff00)
    embed.set_footer(text=f"Bought by {ctx.author.name}", icon_url=ctx.author.avatar)
    await ctx.send(embed=embed)


async def sell(ctx, item, amount):
    # Get the user's balance from the database
    original_items = []
    original_items.append(item)
    item = item.lower().replace(' ', '_').replace('-', '_')
    user_id = str(ctx.author.id)

    # Check if the item exists and the user has enough balance
    if item not in CHIP_ITEMS and item not in TICKETS_ITEMS:
        await ctx.send(f"{item} is not a valid item.")
        return
    if item in CHIP_ITEMS:
        ITEMS = CHIP_ITEMS
        column = 'balance'
        currency = 'Ryō'
    elif item in TICKETS_ITEMS:
        ITEMS = TICKETS_ITEMS
        column = 'special'
        currency = 'Special Tickets'

    c = conn_bal.cursor()
    c.execute(f"SELECT {column} FROM balances WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row is None:
        conn_bal.execute(f"INSERT INTO balances (user_id, {column}) VALUES (?, ?)", (user_id, 0))
        conn_bal.commit()
        return 0
    balance = row[0]

    price = ITEMS[item] * amount
    cursor = conn.execute(f"SELECT {item} FROM inv WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        await ctx.send(f"**{ctx.author.name}** does not have any {original_items[0]}.")
        return
    if row[0] == 0:
        await ctx.send(f"**{ctx.author.name}** does not have any {original_items[0]}.")
        return
    else:
        if row[0] < amount:
            await ctx.send(f"**{ctx.author.name}** does not have {amount} {original_items[0]} to sell.")
            return

    # Update the user's balance and inventory in the database
    new_balance = balance + int(price * 0.9)
    c.execute(f"UPDATE balances SET {column}=? WHERE user_id=?", (new_balance, user_id))
    inv_add(user_id, item, -amount) 
    await equip.unequip_item(ctx, item)
    
    conn_bal.commit()

    # Send a confirmation message
    embeds=discord.Embed(title="Success", description=f"You sold {amount} {original_items[0]} for {int(price * 0.9)} {currency}", color=0x00ff00)
    embeds.set_footer(text=f"Sold by {ctx.author.name}", icon_url=ctx.author.avatar)
    await ctx.send(embed=embeds)