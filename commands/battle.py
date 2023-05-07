import discord
import sqlite3
import asyncio

# connect to the teams database
teams_conn = sqlite3.connect('db/teams.db')
teams_cursor = teams_conn.cursor()

# connect to the cards database
cards_conn = sqlite3.connect('db/cards.db')
cards_cursor = cards_conn.cursor()

# create the teams table if it doesn't exist
teams_cursor.execute('''CREATE TABLE IF NOT EXISTS teams (
                        user_id INTEGER PRIMARY KEY,
                        card_1 INTEGER,
                        card_2 INTEGER,
                        card_3 INTEGER,
                        card_4 INTEGER,
                        FOREIGN KEY(card_1) REFERENCES cards(id),
                        FOREIGN KEY(card_2) REFERENCES cards(id),
                        FOREIGN KEY(card_3) REFERENCES cards(id),
                        FOREIGN KEY(card_4) REFERENCES cards(id)
                    )''')

async def battle(ctx, opponent):
    if opponent == ctx.author:
        await ctx.send('You cannot battle yourself.')
        return
    elif opponent.bot:
        await ctx.send('You cannot battle a bot.')
        return
    elif not opponent:
        await ctx.send('You must specify an opponent.')
        return
    
    # Send a message to the opponent to confirm the battle
    message = await ctx.send(f"{opponent.mention}, {ctx.author.mention} has challenged you to a battle. Do you accept? Type 'yes' or 'no'.")
    
    def check(msg):
        # Check if the message is from the opponent and it's either 'yes' or 'no'
        return msg.author == opponent and msg.content.lower() in ['yes', 'no']
    
    try:
        # Wait for the opponent's response
        response = await ctx.bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await message.edit(content=f"{opponent.mention}, you took too long to respond.")
        return
    else:
        if response.content.lower() == 'no':
            await message.edit(content=f"{opponent.mention} has declined the battle.")
            return

    user_id = ctx.author.id
    opponent_id = opponent.id

    # check if user has a team
    teams_cursor.execute('SELECT * FROM teams WHERE user_id = ?', (user_id,))
    user_team = teams_cursor.fetchone()
    if not user_team:
        await ctx.send('You do not have a team.')
        return

    # check if opponent has a team
    teams_cursor.execute('SELECT * FROM teams WHERE user_id = ?', (opponent_id,))
    opponent_team = teams_cursor.fetchone()
    if not opponent_team:
        await ctx.send('Opponent does not have a team.')
        return

    # calculate user's total value
    user_total = 0
    for card_id in user_team[1:]:
        if card_id:
            cards_cursor.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, card_id))
            card_value = cards_cursor.fetchone()
            user_total += card_value[0] if card_value else 0

    # calculate opponent's total value
    opponent_total = 0
    for card_id in opponent_team[1:]:
        if card_id:
            cards_cursor.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, card_id))
            card_value = cards_cursor.fetchone()
            opponent_total += card_value[0] if card_value else 0

    # compare the two totals and send the result
    if user_total > opponent_total:
        await ctx.send(f"{ctx.author.mention} wins with a score of {user_total} to {opponent_total}!")
    elif user_total < opponent_total:
        await ctx.send(f"{opponent.mention} wins with a score of {opponent_total} to {user_total}!")
    else:
        await ctx.send(f"It's a tie! Both players scored {user_total}.")