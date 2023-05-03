import discord
import sqlite3

conn = sqlite3.connect('db/teams.db')
cursor = conn.cursor()

conn_cards = sqlite3.connect('db/cards.db')
c = conn_cards.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS teams
                (user_id INTEGER PRIMARY KEY,
                    card_1 INTEGER,
                    card_2 INTEGER,
                    card_3 INTEGER,
                    card_4 INTEGER,
                    FOREIGN KEY(card_1) REFERENCES cards(id),
                    FOREIGN KEY(card_2) REFERENCES cards(id),
                    FOREIGN KEY(card_3) REFERENCES cards(id),
                    FOREIGN KEY(card_4) REFERENCES cards(id))''')

async def battle(ctx, opponent):
    if opponent == ctx.author:
        await ctx.send('You cannot battle yourself.')
        return
    elif opponent.bot:
        await ctx.send('You cannot battle a bot.')
        return
    elif opponent == None:
        await ctx.send('You must specify an opponent.')
        return
    opponent_id = opponent.id
    user_id = ctx.author.id
    # Check if user has a user_team
    cursor.execute('SELECT * FROM teams WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if not result:
        await ctx.send('You do not have a team.')
        return
    # Check if opponent has a user_team
    cursor.execute('SELECT * FROM teams WHERE user_id = ?', (opponent_id,))
    result = cursor.fetchone()
    if not result:
        await ctx.send('Opponent does not have a team.')
        return
    
    user_total = 0
    opponent_total = 0

    # Get user's user_team
    cursor.execute('SELECT card_1, card_2, card_3, card_4 FROM teams WHERE user_id = ?', (user_id,))
    user_team = cursor.fetchone()
    if len(user_team) == 1:	
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
    elif len(user_team) == 2:
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[1]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
    elif len(user_team) == 3:
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[1]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[2]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
    elif len(user_team) == 4:
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[1]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[2]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (user_id, user_team[3]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value

    # Get opponent's user_team
    cursor.execute('SELECT card_1, card_2, card_3, card_4 FROM teams WHERE user_id = ?', (opponent_id,))
    opponent_team = cursor.fetchone()
    if len(opponent_team) == 1:	
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
    elif len(opponent_team) == 2:
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[1]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
    elif len(opponent_team) == 3:
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[1]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[2]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
    elif len(opponent_team) == 4:
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[0]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[1]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[2]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value
        c.execute("SELECT value FROM owned_cards WHERE user_id = ? AND card_id = ?", (opponent_id, opponent_team[3]))
        card_value = c.fetchone()
        if card_value == None:
            user_total += 0
        else:
            user_total += card_value

    if user_total > opponent_total:
        await ctx.send(f'{ctx.author.mention} wins!')
    elif user_total < opponent_total:
        await ctx.send(f'{opponent.mention} wins!')
    else:
        await ctx.send('Tie!')