import sqlite3
import discord

conn = sqlite3.connect("db/balances.db")

def update_balance(user_id, amount):
    cursor = conn.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    balance = row[0] + amount
    conn.execute("UPDATE balances SET balance=? WHERE user_id=?", (balance, user_id))
    conn.commit()

async def add_chips(ctx, amount: int, user: discord.Member=None):
    if user is None:
        user = ctx.message.author
        user_id = user.id
    else:
        user_id = user.id
    if amount is None:
        await ctx.send(embed=discord.Embed(title="Please specify an amount of ryō to add.", color=0xff0000))
        return
    update_balance(user_id, amount)
    await ctx.send(embed=discord.Embed(title="Success", description=f"```Added {amount} ryō to {user.name}```", color=discord.Color.green()))
