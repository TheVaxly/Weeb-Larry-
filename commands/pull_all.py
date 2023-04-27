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

async def add_card(ctx, card_id: int, value: int):
    with open('db/cards.json', 'r') as f:
            data = json.load(f)
    # Check if card_id is valid
    if card_id < 1 or card_id > len(data['cards']):
        await ctx.send('Invalid card ID.')
        return
    
    user_id = ctx.author.id
    # Add card to user's collection
    c.execute('INSERT INTO owned_cards VALUES (?, ?, ?)',
              (user_id, card_id, value))
    conn.commit()
    
async def pull(ctx):
    user_id = ctx.author.id
    cost_per_pull = 1000
    bals = get_balance(user_id)
    num_pulls = bals // cost_per_pull
    print(num_pulls)
    total_cost = cost_per_pull * num_pulls

    if bals < total_cost or num_pulls == 0:
        await ctx.send(f"{ctx.author.mention}, you don't have enough chips to perform {num_pulls} pull! Least you can do is {bals // cost_per_pull} pull.")
        return

    # Subtract the total cost from user's balance
    new_balance = bals - total_cost
    c_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn_bal.commit()

    # Perform the specified number of pulls
    new_cards = []
    rarities = ['SS', 'S', 'A', 'B', 'C']
    weights = [0.01, 0.05, 0.3, 0.4, 0.6]
    pulled_rarities = []
    owned = []
    for i in range(num_pulls):
        rarity = random.choices(rarities, weights=weights)[0]
        pulled_rarities.append(rarity)
        c.execute("SELECT * FROM cards WHERE rarity = ? ORDER BY RANDOM() LIMIT 1", (rarity,))
        result = c.fetchone()

        user_id = ctx.author.id
        c.execute('''SELECT * FROM owned_cards
                    WHERE user_id = ? AND card_id = ?''',
                (user_id, result[0]))
        already_owned = c.fetchone()
        if already_owned:
            owned.append(rarity)
            continue

        await add_card(ctx, result[0], result[2])
        new_cards.append(result)

    if num_pulls == 1:
        if len(new_cards) == 0:
            name, value, url, rank, rarity, anime = result[1], result[2], result[3], result[4], result[5], result[6]
            embed = discord.Embed(title=f"**You pulled {name}**", color=0x00ff00)
            embed.set_footer(text=f"Card already owned! Get {500} chips back\nPulled by {ctx.author.name}")
            embed.add_field(name=f"**Card nr {result[0]}**", value=f"**Anime: {anime}**\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+500, user_id))
            conn_bal.commit()
            return
        else:
            name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
            embed = discord.Embed(title=f"**You pulled {name}**", color=0x00ff00)
            embed.set_footer(text=f"1 New card pulled!\nPulled by {ctx.author.name}")
            embed.add_field(name=f"**Card nr {result[0]}**", value=f"**Anime: {anime}**\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            return
    elif len(new_cards) == 1:
        name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
        embed = discord.Embed(title=f"**You pulled {name}**", color=0x00ff00)
        embed.set_footer(text=f"{num_pulls-len(new_cards)} duplicate! Get {(num_pulls-len(new_cards))*1000//2} chips back\nPulled by {ctx.author.name}")
        embed.add_field(name=f"**Card nr {result[0]}**", value=f"**Anime: {anime}**\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
        embed.set_image(url=url)
        embed.set_thumbnail(url=rank)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+((num_pulls-len(new_cards))*1000//2), user_id))
        conn_bal.commit()
        return
    elif len(new_cards) > 1:
        embed = discord.Embed(title=f"**You pulled {len(new_cards)} new cards**", description=f"New **SS**: {pulled_rarities.count('SS')}, Duplicates: {owned.count('SS')}\nNew **S**: {pulled_rarities.count('S')}, Duplicates: {owned.count('S')}\nNew **A**: {pulled_rarities.count('A')}, Duplicates: {owned.count('A')}\nNew **B**: {pulled_rarities.count('B')}, Duplicates: {owned.count('B')}\nNew **C**: {pulled_rarities.count('C')}, Duplicates: {owned.count('C')}", color=0x00ff00)
        embed.set_footer(text=f"Pulled by {ctx.author.name}")
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+((num_pulls-len(new_cards))*1000//2), user_id))
        conn_bal.commit()
    else:
        await ctx.send(f"You didn't pull anything new. Get {(num_pulls-len(new_cards))*1000//2} chips back.")
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance+((num_pulls-len(new_cards))*1000//2), user_id))
        conn_bal.commit()