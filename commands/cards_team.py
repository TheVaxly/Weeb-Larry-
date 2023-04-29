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


async def team(ctx, option=None, card_id=None, client=None):
    if option is None:
        user_id = ctx.author.id
        tc.execute('''SELECT card_1, card_2, card_3, card_4 FROM teams
                     WHERE user_id = ?''', (user_id,))
        team = tc.fetchone()
        if team:
            team = list(filter(None, team))
            team_str = ','.join([str(id) for id in team])
            c.execute(f"SELECT name, value, url, rank, rarity FROM cards WHERE id IN ({team_str}) ORDER BY value DESC")
            cards = c.fetchall()

            embed = discord.Embed(title=f"**{ctx.author.name}'s Team**", color=discord.Color.blurple())
            current_index = 0
            card_name, card_value, card_url, card_rank, rarity = cards[current_index]

            embed.add_field(name=f"**Name**: {card_name}", value=f"**Value**: {card_value}\n**Rank**: {rarity}", inline=False)
            embed.set_image(url=card_url)
            embed.set_thumbnail(url=card_rank)
            embed.set_footer(text=f"Card ID: {card_id}", icon_url=ctx.author.avatar)

            msg = await ctx.send(embed=embed)
            await msg.add_reaction('◀️')
            await msg.add_reaction('▶️')

            def check(reaction, user):
                return user == ctx.author and reaction.message.id == msg.id and reaction.emoji in ['◀️', '▶️']

            while True:
                try:
                    reaction, user = await client.wait_for('reaction_add', timeout=30, check=check)
                    if reaction.emoji == '◀️':
                        current_index -= 1
                        if current_index < 0:
                            current_index = len(cards) - 1
                        card_name, card_value, card_url, card_rank, rarity = cards[current_index]
                    elif reaction.emoji == '▶️':
                        current_index += 1
                        if current_index >= len(cards):
                            current_index = 0
                        card_name, card_value, card_url, card_rank, rarity = cards[current_index]
                    await msg.remove_reaction(reaction, user)
                    embed.set_field_at(0, name=f"**Name**: {card_name}", value=f"**Value**: {card_value}\n**Rank**: {rarity}", inline=False)
                    embed.set_image(url=card_url)
                    embed.set_thumbnail(url=card_rank)
                    embed.set_footer(text=f"Card ID: {card_id}", icon_url=ctx.author.avatar)
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

