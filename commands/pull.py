import discord
import sqlite3
import random
import json
import time

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

conn_bal = sqlite3.connect('db/balances.db')
c_bal = conn_bal.cursor()

# Create a balances table if it doesn't exist
c_bal.execute('''CREATE TABLE IF NOT EXISTS balances
                    (user_id INTEGER PRIMARY KEY,
                    balance INTEGER, special INTEGER)''')

def get_balance(user_id):
    cursor = conn_bal.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn_bal.execute("INSERT INTO balances (user_id, balance) VALUES (?, ?)", (user_id, 1000))
        conn_bal.commit()
        return 1000
    else:
        return row[0]

def get_tickets(user_id):
    cursor = conn_bal.execute("SELECT special FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn_bal.execute("INSERT INTO balances (user_id, special) VALUES (?, ?)", (user_id, 0))
        conn_bal.commit()
        return 0
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
    c.execute('INSERT INTO owned_cards VALUES (?, ?, ?, ?, ?)',
              (user_id, card_id, value, 0, 0))
    conn.commit()

last_mission_times = {}

async def pull(ctx, num_pulls):
    current_time = time.time()
    last_mission_time = last_mission_times.get(ctx.author.id)
    if last_mission_time is not None and current_time - last_mission_time < 1:
        wait_time = 1 - (current_time - last_mission_time)
        await ctx.channel.send(f"Wait {wait_time:.2f}s for your next pull **{ctx.author.name}**.")
        return
    # Update user's last mission time
    last_mission_times[ctx.author.id] = current_time

    user_id = ctx.author.id
    cost_per_pull = 1000
    num_pulls = int(num_pulls)
    total_cost = cost_per_pull * num_pulls

    if num_pulls <= 0:
        await ctx.send(f"**{ctx.author.name}**, you can't do {num_pulls} pulls!")
        return

    if num_pulls > 10:
        await ctx.send(f"**{ctx.author.name}**, you can only do 10 pulls at a time. Or use !pullall (!pa)")
        return

    # Check if user has enough balance
    bal = get_balance(user_id)

    if bal < total_cost:
        await ctx.send(f"{ctx.author.mention}, you don't have enough Ryō to perform {num_pulls} pull! Least you can do is {bal // cost_per_pull} pulls.")
        return

    # Subtract the total cost from user's balance
    new_balance = bal - total_cost
    tickets = get_tickets(ctx.author.id)
    c_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn_bal.commit()

    # Perform the specified number of pulls
    new_cards = []
    rarities = ['UR', 'SS', 'S', 'A', 'B', 'C']
    weights = [0.001, 0.01, 0.05, 0.3, 0.4, 0.6]
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
            card_id, name, value, url, rank, rarity, anime = result[0], result[1], result[2], result[3], result[4], result[5], result[6]
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            special = random.randint(5, 10) * 10
            embed.set_footer(text=f"Card owned✅! Get {special} special tickets\nPulled by {ctx.author.name} | Card id: {card_id}")
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+special, user_id))
            conn_bal.commit()
            return
        else:
            card_id, name, value, url, rank, rarity, anime = new_cards[0][0], new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            embed.set_footer(text=f"New card! | Card id: {card_id}\nPulled by {ctx.author.name}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            return
    elif len(new_cards) == 1:
        card_id, name, value, url, rank, rarity, anime = new_cards[0][0], new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
        embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
        special = random.randint(5, 10) * 10
        embed.set_footer(text=f"1 new | {num_pulls-len(new_cards)} duplicate! Get {num_pulls-len(new_cards)*special} special tickets\nPulled by {ctx.author.name} | Card id: {card_id}", icon_url=ctx.author.avatar)
        embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
        embed.set_image(url=url)
        embed.set_thumbnail(url=rank)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
        return
    elif len(new_cards) > 1:
        special = random.randint(5, 10) * 10
        embed = discord.Embed(title=f"**You pulled {len(new_cards)} new cards**", description=f"New **SS**: {pulled_rarities.count('SS')-owned.count('SS')}, Duplicates: {owned.count('SS')}\nNew **S**: {pulled_rarities.count('S')-owned.count('S')}, Duplicates: {owned.count('S')}\nNew **A**: {pulled_rarities.count('A')-owned.count('A')}, Duplicates: {owned.count('A')}\nNew **B**: {pulled_rarities.count('B')-owned.count('B')}, Duplicates: {owned.count('B')}\nNew **C**: {pulled_rarities.count('C')-owned.count('C')}, Duplicates: {owned.count('C')}", color=0x00ff00)
        embed.set_footer(text=f"Pulled by {ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
    else:
        special = random.randint(5, 10) * 10
        await ctx.send(f"{ctx.author.name} didn't pull anything new. Get {num_pulls-len(new_cards)*special} special tickets.")
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()


last_times = {}
    
async def pull_all(ctx):
    current_time = time.time()
    last_time = last_times.get(ctx.author.id)
    if last_time is not None and current_time - last_time < 1:
        wait_time = 1 - (current_time - last_time)
        await ctx.channel.send(f"Wait {wait_time:.2f}s for your next pull **{ctx.author.name}**.")
        return
    # Update user's last mission time
    last_times[ctx.author.id] = current_time

    user_id = ctx.author.id
    cost_per_pull = 1000
    bals = get_balance(user_id)
    num_pulls = bals // cost_per_pull
    total_cost = cost_per_pull * num_pulls

    if bals < total_cost or num_pulls == 0:
        await ctx.send(f"{ctx.author.mention}, you don't have enough Ryō to perform {num_pulls} pull! Least you can do is {bals // cost_per_pull} pulls.")
        return

    # Subtract the total cost from user's balance
    new_balance = bals - total_cost
    tickets = get_tickets(ctx.author.id)
    c_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn_bal.commit()

    # Perform the specified number of pulls
    new_cards = []
    rarities = ['UR', 'SS', 'S', 'A', 'B', 'C']
    weights = [0.001, 0.01, 0.05, 0.3, 0.4, 0.6]
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
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            special = random.randint(5, 10) * 10
            embed.set_footer(text=f"Card owned✅! Get {special} special tickets\nPulled by {ctx.author.name} | Card id: {result[0]}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+special, user_id))
            conn_bal.commit()
            return
        else:
            name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            embed.set_footer(text=f"New card! | Card id: {result[0]}\nPulled by {ctx.author.name}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            return
    elif len(new_cards) == 1:
        name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
        embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
        special = random.randint(5, 10) * 10
        embed.set_footer(text=f"1 new |{num_pulls-len(new_cards)} duplicate! Get {(num_pulls-len(new_cards))*special} special tickets\nPulled by {ctx.author.name} | Card id: {result[0]}", icon_url=ctx.author.avatar)
        embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
        embed.set_image(url=url)
        embed.set_thumbnail(url=rank)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
        return
    elif len(new_cards) > 1:
        embed = discord.Embed(title=f"**You pulled {len(new_cards)} new cards**", description=f"New **SS**: {pulled_rarities.count('SS')-owned.count('SS')}, Duplicates: {owned.count('SS')}\nNew **S**: {pulled_rarities.count('S')-owned.count('S')}, Duplicates: {owned.count('S')}\nNew **A**: {pulled_rarities.count('A')-owned.count('A')}, Duplicates: {owned.count('A')}\nNew **B**: {pulled_rarities.count('B')-owned.count('B')}, Duplicates: {owned.count('B')}\nNew **C**: {pulled_rarities.count('C')-owned.count('C')}, Duplicates: {owned.count('C')}", color=0x00ff00)
        embed.set_footer(text=f"Pulled by {ctx.author.name}", icon_url=ctx.author.avatar)
        special = random.randint(5, 10) * 10
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
    else:
        special = random.randint(5, 10) * 10
        await ctx.send(f"You didn't pull anything new. Get {(num_pulls-len(new_cards))*special} special tickets.")
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()

times = {}

async def special(ctx, amount):
    current_time = time.time()
    timey = times.get(ctx.author.id)
    if timey is not None and current_time - timey < 1:
        wait_time = 1 - (current_time - timey)
        await ctx.channel.send(f"Wait {wait_time:.2f}s for your next pull **{ctx.author.name}**.")
        return
    # Update user's last mission time
    times[ctx.author.id] = current_time

    user_id = ctx.author.id
    cost_per_pull = 500
    bals = get_tickets(user_id)
    num_pulls = amount
    total_cost = cost_per_pull * num_pulls

    if bals < total_cost or num_pulls == 0:
        await ctx.send(f"{ctx.author.mention}, you don't have enough special tickets to perform {num_pulls} pull! Least you can do is {bals // cost_per_pull} pulls.")
        return

    # Subtract the total cost from user's balance
    new_balance = bals - total_cost
    c_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (new_balance, user_id))
    conn_bal.commit()
    tickets = get_tickets(ctx.author.id)
    # Perform the specified number of pulls
    new_cards = []
    rarities = ['SS'] * 3 + ['S'] * 7
    weights = [0.3] * 3 + [0.7] * 7
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
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            special = random.randint(5, 10) * 10
            embed.set_footer(text=f"Card owned✅! Get {special} special tickets\nPulled by {ctx.author.name} | Card id: {result[0]}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+special, user_id))
            conn_bal.commit()
            return
        else:
            name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            embed.set_footer(text=f"New card! | Card id: {result[0]}\nPulled by {ctx.author.name}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            return
    elif len(new_cards) == 1:
        name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
        embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
        special = random.randint(5, 10) * 10
        embed.set_footer(text=f"1 new |{num_pulls-len(new_cards)} duplicate! Get {(num_pulls-len(new_cards))*special} special tickets\nPulled by {ctx.author.name} | Card id: {result[0]}", icon_url=ctx.author.avatar)
        embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
        embed.set_image(url=url)
        embed.set_thumbnail(url=rank)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
        return
    elif len(new_cards) > 1:
        embed = discord.Embed(title=f"**You pulled {len(new_cards)} new cards**", description=f"New **SS**: {pulled_rarities.count('SS')-owned.count('SS')}, Duplicates: {owned.count('SS')}\nNew **S**: {pulled_rarities.count('S')-owned.count('S')}, Duplicates: {owned.count('S')}", color=0x00ff00)
        embed.set_footer(text=f"Pulled by {ctx.author.name}", icon_url=ctx.author.avatar)
        special = random.randint(5, 10) * 10
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
    else:
        special = random.randint(5, 10) * 10
        await ctx.send(f"You didn't pull anything new. Get {(num_pulls-len(new_cards))*special} special tickets back.")
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()

lasts = {}

async def special_all(ctx):
    current_time = time.time()
    last = lasts.get(ctx.author.id)
    if last is not None and current_time - last < 1:
        wait_time = 1 - (current_time - last)
        await ctx.channel.send(f"Wait {wait_time:.2f}s for your next pull **{ctx.author.name}**.")
        return
    # Update user's last mission time
    lasts[ctx.author.id] = current_time

    user_id = ctx.author.id
    cost_per_pull = 500
    bals = get_tickets(user_id)
    num_pulls = bals // cost_per_pull
    total_cost = cost_per_pull * num_pulls

    if bals < total_cost or num_pulls == 0:
        await ctx.send(f"{ctx.author.mention}, you don't have enough special tickets to perform {num_pulls} pull! Least you can do is {bals // cost_per_pull} pulls.")
        return

    # Subtract the total cost from user's balance
    new_balance = bals - total_cost
    c_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (new_balance, user_id))
    conn_bal.commit()
    tickets = get_tickets(ctx.author.id)

    # Perform the specified number of pulls
    new_cards = []
    rarities = ['SS'] * 3 + ['S'] * 7
    weights = [0.3] * 3 + [0.7] * 7
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
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            special = random.randint(5, 10) * 10
            embed.set_footer(text=f"Card owned✅! Get {special} special tickets\nPulled by {ctx.author.name} | Card id: {result[0]}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+special, user_id))
            conn_bal.commit()
            return
        else:
            name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
            embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
            embed.set_footer(text=f"New card! | Card id: {result[0]}\nPulled by {ctx.author.name}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
            embed.set_image(url=url)
            embed.set_thumbnail(url=rank)
            await ctx.send(embed=embed)
            return
    elif len(new_cards) == 1:
        name, value, url, rank, rarity, anime = new_cards[0][1], new_cards[0][2], new_cards[0][3], new_cards[0][4], new_cards[0][5], new_cards[0][6]
        embed = discord.Embed(title=f"**{name}**", color=0x00ff00)
        special = random.randint(5, 10) * 10
        embed.set_footer(text=f"1 new |{num_pulls-len(new_cards)} duplicate! Get {(num_pulls-len(new_cards))*special} special tickets\nPulled by {ctx.author.name} | Card id: {result[0]}", icon_url=ctx.author.avatar)
        embed.add_field(name="", value=f"**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}", inline=False)
        embed.set_image(url=url)
        embed.set_thumbnail(url=rank)
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
        return
    elif len(new_cards) > 1:
        embed = discord.Embed(title=f"**You pulled {len(new_cards)} new cards**", description=f"New **SS**: {pulled_rarities.count('SS')-owned.count('SS')}, Duplicates: {owned.count('SS')}\nNew **S**: {pulled_rarities.count('S')-owned.count('S')}, Duplicates: {owned.count('S')}", color=0x00ff00)
        embed.set_footer(text=f"Pulled by {ctx.author.name}", icon_url=ctx.author.avatar)
        special = random.randint(5, 10) * 10
        await ctx.send(embed=embed)
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()
    else:
        special = random.randint(5, 10) * 10
        await ctx.send(f"You didn't pull anything new. Get {(num_pulls-len(new_cards))*special} special tickets back.")
        conn_bal.execute("UPDATE balances SET special = ? WHERE user_id = ?", (tickets+((num_pulls-len(new_cards))*special), user_id))
        conn_bal.commit()