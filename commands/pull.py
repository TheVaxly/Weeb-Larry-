import discord
import sqlite3
import random
import json

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

conn_bal = sqlite3.connect('db/balances.db')
c_bal = conn_bal.cursor()

# Create a balances table if it doesn't exist
c_bal.execute('''CREATE TABLE IF NOT EXISTS balances
                    (user_id INTEGER PRIMARY KEY,
                    balance INTEGER)''')

def get_balance(user_id):
    cursor = conn_bal.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn_bal.execute("INSERT INTO balances (user_id, balance) VALUES (?, ?)", (user_id, 1000))
        conn_bal.commit()
        return 1000
    else:
        return row[0]

async def add_card(ctx, card_id: int):
    with open('db/cards.json', 'r') as f:
            data = json.load(f)
    # Check if card_id is valid
    if card_id < 1 or card_id > len(data['cards']):
        await ctx.send('Invalid card ID.')
        return
    
    user_id = ctx.author.id
    # Add card to user's collection
    c.execute('INSERT INTO owned_cards VALUES (?, ?)',
              (user_id, card_id))
    conn.commit()
    
async def pull(ctx, num_pulls):
    user_id = ctx.author.id
    cost_per_pull = 1000
    total_cost = cost_per_pull * num_pulls

    if num_pulls <= 0:
        await ctx.send(f"{ctx.author.mention}, you can't do {num_pulls} pull!")
        return

    if num_pulls > 10:
        await ctx.send(f"{ctx.author.mention}, you can only do 10 pulls at a time.")
        return

    # Check if user has enough balance
    bal = get_balance(user_id)

    if bal < total_cost:
        await ctx.send(f"{ctx.author.mention}, you don't have enough chips to perform {num_pulls} pull! Least you can do is {bal // cost_per_pull} pull.")
        return

    # Subtract the total cost from user's balance
    new_balance = bal - total_cost
    c_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn_bal.commit()

    # Perform the specified number of pulls
    new_cards = []
    for i in range(num_pulls):
        card_id = random.randint(1, 3)
        c.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        result = c.fetchone()

        user_id = ctx.author.id
        c.execute('''SELECT * FROM owned_cards
                     WHERE user_id = ? AND card_id = ?''',
                  (user_id, card_id))
        already_owned = c.fetchone()
        if already_owned:
            continue

        await add_card(ctx, card_id)
        new_cards.append(result)

    if num_pulls == 1:
        if len(new_cards) == 0:
            name, value, url, rank = result[1], result[2], result[3], result[4]
            embed = discord.Embed(title=f"**You pulled {name}**", color=0x00ff00)
            embed.set_footer(text=f"Card already owned! Get {500} chips back\nPulled by {ctx.author.name}")
            embed.add_field(name=f"**Card nr {card_id}**", value=f"**Power**: {value}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+500, user_id))
            conn_bal.commit()
            return
        else:
            name, value, url, rank = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4]
            embed = discord.Embed(title=f"**You pulled {name}**", color=0x00ff00)
            embed.set_footer(text=f"1 New card pulled!\nPulled by {ctx.author.name}")
            embed.add_field(name=f"**Card nr {card_id}**", value=f"**Power**: {value}", inline=False)
            embed.set_image(url=url)
            await ctx.send(embed=embed)
            return
    elif len(new_cards) == 1:
        name, value, url, rank = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4]
        embed = discord.Embed(title=f"**You pulled {name}**", color=0x00ff00)
        embed.set_footer(text=f"1 New card pulled! Get {(num_pulls-len(new_cards))*1000//2} chips back\nPulled by {ctx.author.name}")
        embed.add_field(name=f"**Card nr {card_id}**", value=f"**Power**: {value}", inline=False)
        embed.set_image(url=url)
        embed.set_thumbnail(url=rank)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+((num_pulls-len(new_cards))*1000//2), user_id))
        conn_bal.commit()
        return
    elif len(new_cards) > 1:
        embed = discord.Embed(title=f"**You pulled {len(new_cards)} new cards**", color=0x00ff00)
        embed.set_footer(text=f"{num_pulls-len(new_cards)} duplicates! Get {(num_pulls-len(new_cards))*1000//2} chips back\nPulled by {ctx.author.name}")
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+((num_pulls-len(new_cards))*1000//2), user_id))
        conn_bal.commit()
    else:
        await ctx.send(f"You didn't pull anything new. Get {(num_pulls-len(new_cards))*1000//2} chips back.")
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+((num_pulls-len(new_cards))*1000//2), user_id))
        conn_bal.commit()