import sqlite3
import discord

# create a connection to the database
conn = sqlite3.connect('db/balances.db')

# create a table to store the balances
conn.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INT PRIMARY KEY NOT NULL, balance INT NOT NULL)''')

def get_balance(user_id):
    cursor = conn.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.execute("INSERT INTO balances (user_id, balance) VALUES (?, ?)", (user_id, 1000))
        conn.commit()
        return 1000
    else:
        return row[0]

async def balance(ctx):
    player = ctx.author
    balance = get_balance(player.id)

    embed = discord.Embed(title="Balance", color=discord.Color.gold())
    embed.add_field(name=f"{player.name}", value=f"{balance} chips", inline=False)
    await ctx.send(embed=embed)