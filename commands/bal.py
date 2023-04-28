import sqlite3
import discord

# create a connection to the database
conn = sqlite3.connect('db/balances.db')

# create a table to store the balances
conn.execute('''CREATE TABLE IF NOT EXISTS balances
             (user_id INT PRIMARY KEY NOT NULL, balance INT NOT NULL, special INT NOT NULL)''')

def get_balance(user_id):
    cursor = conn.execute("SELECT balance, special FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn.execute("INSERT INTO balances (user_id, balance, special) VALUES (?, ?, ?)", (user_id, 1000, 0))
        conn.commit()
        return 1000, 0
    else:
        return row[0], row[1]

async def balance(ctx):
    chips, tickets = get_balance(ctx.author.id)[0], get_balance(ctx.author.id)[1]
    player = ctx.author
    embed = discord.Embed(title="Balance", color=discord.Color.gold())
    embed.set_thumbnail(url="https://static.wikia.nocookie.net/shinobi-life-2-reel/images/0/08/Ryo.png/revision/latest?cb=20220216114843")
    embed.add_field(name=f"{player.name}", value=f"Ryō: {chips}\nSpecial tickets: {tickets}", inline=False)
    await ctx.send(embed=embed)