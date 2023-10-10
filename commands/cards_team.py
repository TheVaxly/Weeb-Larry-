import sqlite3
import discord
from discord.ext import commands
import asyncio

# Create connection to cards database
card_conn = sqlite3.connect('db/cards.db')
c = card_conn.cursor()

# Create connection to teams database
team_conn = sqlite3.connect('db/teams.db')
tc = team_conn.cursor()

tc.execute('''CREATE TABLE IF NOT EXISTS teams
                (user_id INTEGER PRIMARY KEY,
                    card_1 INTEGER,
                    card_2 INTEGER,
                    card_3 INTEGER,
                    card_4 INTEGER,
                    FOREIGN KEY(card_1) REFERENCES cards(id),
                    FOREIGN KEY(card_2) REFERENCES cards(id),
                    FOREIGN KEY(card_3) REFERENCES cards(id),
                    FOREIGN KEY(card_4) REFERENCES cards(id))''')
DB_ITEMS = {
    'mogus': 5,
    'truck_kun': 3.25,
    'super_dragon_balls': 2.85,
    'death_note': 2.5,
    'sword_of_rupture': 2.3,
    'truth_seeking_orbs': 2.2,
    'gun': 2,
    'murasame': 1.9,
    'dragon_slayer': 1.8,
    'odm_gear': 1.7,
    'super_tengen_toppa_gurren_lagann': 2,
    'spear_of_longinus': 1.5,
    'lostvayne': 1.4,
    'katana': 1.3,
    'kunai': 1.2,
    'shuriken': 1.15,
    'eggplant': 1.1,
}

async def team(ctx, option=None, card_id=None, client=None):
    if option is None:
        user_id = ctx.author.id
        tc.execute('''SELECT card_1, card_2, card_3, card_4 FROM teams
                     WHERE user_id = ?''', (user_id,))
        team = tc.fetchone()
        if not team:
            await ctx.send("You haven't set up a team yet. Use `!team add <card_id>` to add a card to your team.")
            return
        team = list(filter(None, team))
        c.execute("SELECT item_id FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, team[0]))
        card_item = c.fetchone()
        card_item = list(filter(None, card_item))
        total_value = 0
        if team:
            team = list(filter(None, team))
            team_str = ','.join([str(id) for id in team])
            c.execute(f"SELECT name, value, url, rank, rarity, id FROM cards WHERE id IN ({team_str})")
            cards = c.fetchall()
            cards.sort(key=lambda x: x[1], reverse=True)
            c.execute(f"SELECT level FROM owned_cards WHERE user_id = ? AND card_id IN ({team_str})", (user_id,))
            levels = c.fetchall()
            card_ids = [card[5] for card in cards]
            if len(team) == 1:
                c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, team[0]))
                card_value = c.fetchone()[0]
            elif len(team) >= 2:
                c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id IN ({})".format(','.join(['?'] * len(team))), tuple([user_id] + team))
                card_values = c.fetchall()
                card_value = sum(value for (value,) in card_values)
            total_value += card_value
            total_value = round(total_value, 0)
            embed = discord.Embed(title=f"**{ctx.author.name}'s Team**", color=discord.Color.blurple())
            current_index = 0
            card_name, card_value, card_url, card_rank, rarity, card_id = cards[current_index]
            c.execute(f"SELECT item_id FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, card_id))
            card_item = c.fetchone()
            card_item = list(filter(None, card_item))

            if card_item:
                if card_item[0] in DB_ITEMS:
                    card_item_name = f"{card_item[0].replace('_', ' ').title()} ({DB_ITEMS[card_item[0]]}x)"
                    multiplier = DB_ITEMS[card_item[0]]
                    modified_value = int(multiplier * card_value)
                else:
                    card_item_name = "---"
                    modified_value = card_value
            else:
                card_item_name = "---"
                modified_value = card_value

            embed.title = f"**{card_name} | Lvl {levels[current_index][0]}**"
            embed.add_field(name="", value=f"**Power**: {modified_value}\n**Rank**: {rarity}\n**Equipped**: {card_item_name}", inline=False)
            embed.set_image(url=card_url)
            embed.set_thumbnail(url=card_rank)
            embed.set_footer(text=f"Team power: {total_value}\n{ctx.author.name}'s team--{current_index + 1}/{len(cards)} | Card ID: {card_id}", icon_url=ctx.author.avatar)

            msg = await ctx.send(embed=embed)
            await msg.add_reaction('◀️')
            await msg.add_reaction('▶️')

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and reaction.emoji in ['◀️', '▶️']

            while True:
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=180, check=check)
                    if reaction.emoji == '◀️':
                        current_index -= 1
                        if current_index < 0:
                            current_index = len(cards) - 1
                    elif reaction.emoji == '▶️':
                        current_index += 1
                        if current_index >= len(cards):
                            current_index = 0
                    
                    card_id, card_value, card_url, card_rank, rarity, card_id = cards[current_index]
                    c.execute(f"SELECT item_id FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, card_id))
                    card_item = c.fetchone()
                    card_item = list(filter(None, card_item))
                    
                    if card_item:
                        if card_item[0] in DB_ITEMS:
                            card_item_name = f"{card_item[0].replace('_', ' ').title()} ({DB_ITEMS[card_item[0]]}x)"
                            multiplier = DB_ITEMS[card_item[0]]
                            modified_value = int(multiplier * card_value)
                        else:
                            card_item_name = "---"
                            modified_value = card_value
                    else:
                        card_item_name = "---"
                        modified_value = card_value

                    await msg.remove_reaction(reaction, user)
                    embed.title = f"**{card_name} | Lvl {levels[current_index][0]}**"
                    embed.set_field_at(0, name="", value=f"**Power**: {modified_value}\n**Rank**: {rarity}\n**Equipped**: {card_item_name}", inline=False)
                    embed.set_image(url=card_url)
                    embed.set_thumbnail(url=card_rank)
                    embed.set_footer(text=f"Team power: {total_value}\n{ctx.author.name}'s team--{current_index + 1}/{len(cards)} | Card ID: {card_id}", icon_url=ctx.author.avatar)
                    await msg.edit(embed=embed)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    break
        else:
            await ctx.send("You haven't set up a team yet. Use `!team add <card_id>` to add a card to your team.")
    elif option.lower() == "add":
        if card_id is None:
            await ctx.send("Please provide a card ID to add to your team.")
            return

        user_id = ctx.author.id
        c.execute('SELECT item_id FROM owned_cards WHERE user_id = ? AND card_id = ?', (user_id, card_id))
        item_id = c.fetchone()
        if not item_id:
            await ctx.send("You don't own this card.")
            return

        tc.execute('SELECT card_1, card_2, card_3, card_4 FROM teams WHERE user_id = ?', (user_id,))
        team = tc.fetchone()
        if not team:
            tc.execute('INSERT INTO teams (user_id, card_1) VALUES (?, ?)', (user_id, card_id))
            team_conn.commit()
            await ctx.send(f"Card added to your team!")
        else:
            empty_slot = False
            for i, b in enumerate(team):
                if b is None:
                    empty_slot = True
                    c_index = i + 1
                    break
            if not empty_slot:
                await ctx.send("Your team is full!")
            else:
                tc.execute(f'UPDATE teams SET card_{c_index} = ? WHERE user_id = ?', (card_id, user_id))
                team_conn.commit()
                await ctx.send(f"Card added to your team!")
    elif option.lower() == "remove":
        if card_id is None:
            await ctx.send("Please provide a card ID to remove from your team.")
            return

        user_id = ctx.author.id
        tc.execute('SELECT card_1, card_2, card_3, card_4 FROM teams WHERE user_id = ?', (user_id,))
        team = tc.fetchone()
        if not team:
            await ctx.send("You haven't set up a team yet. Use `!team add <card_id>` to add a card to your team.")
        else:
            card_index = None
            for i, b in enumerate(team):
                if b == card_id:
                    card_index = i + 1
                    break
            if card_index is None:
                await ctx.send("You don't have this card in your team.")
            else:
                tc.execute(f'UPDATE teams SET card_{card_index} = NULL WHERE user_id = ?', (user_id,))
                team_conn.commit()
                await ctx.send(f"Card removed from your team!")
    else:
        await ctx.send("Invalid option. Use `!team add <card_id>` to add a card to your team.")