import sqlite3
import datetime
import discord

#Connect to the balances and last_used databases
conn_balances = sqlite3.connect('db/balances.db')
conn_last_used = sqlite3.connect('db/last_used.db')
conn_last_week = sqlite3.connect('db/last_week.db')

# Create the balances table if it doesn't exist
conn_balances.execute('CREATE TABLE IF NOT EXISTS balances (user_id INTEGER PRIMARY KEY, balance INTEGER NOT NULL DEFAULT 0, special INTEGER NOT NULL DEFAULT 0)')

# Create the last_used table if it doesn't exist
conn_last_used.execute('CREATE TABLE IF NOT EXISTS last_used (user_id INTEGER PRIMARY KEY, last_used TEXT)')

# Create the last_week table if it doesn't exist
conn_last_week.execute('CREATE TABLE IF NOT EXISTS last_week (user_id INTEGER PRIMARY KEY, last_week TEXT)')

async def once_per_day(ctx):
    # Check if user has already used the command today
    cursor = conn_last_used.execute('SELECT last_used FROM last_used WHERE user_id=?', (ctx.author.id,))
    row = cursor.fetchone()
    if row is not None:
        last_used = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.datetime.now() - last_used < datetime.timedelta(hours=12):
            time_delta = datetime.timedelta(hours=12) - (datetime.datetime.now() - last_used)
            time_delta_str = str(time_delta).split(".")[0]  # Remove milliseconds
            time_delta_formatted = datetime.datetime.strptime(time_delta_str, "%H:%M:%S")
            time_delta_str_formatted = time_delta_formatted.strftime("%H:%M:%S")
            # User has already used the command today, so send an error message
            await ctx.send(f"**{ctx.author.name}** can use **!daily** again in {time_delta_str_formatted}")
            return

    # User hasn't used the command today, so execute the command and update the last used time
    embed=discord.Embed(title="You claimed 3000 Ryō!", description="Come back tomorrow for more!", color=discord.Color.dark_gold())
    embed.set_thumbnail(url="https://www.transparentpng.com/thumb/coin-stack/whiEaR-coin-stack-transparent-image.png")
    embed.set_footer(text="Claimed by " + ctx.author.name, icon_url=ctx.author.avatar)
    await ctx.send(embed=embed)
    cursor = conn_balances.execute('SELECT balance FROM balances WHERE user_id=?', (ctx.author.id,))
    row = cursor.fetchone()
    balance = row[0] + 3000
    conn_balances.execute('UPDATE balances SET balance=? WHERE user_id=?', (balance, ctx.author.id))
    conn_balances.commit()
    conn_last_used.execute('REPLACE INTO last_used VALUES (?, ?)', (ctx.author.id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
    conn_last_used.commit()

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


async def once_per_week(ctx):
    # Check if user has already used the command today
    cursor = conn_last_week.execute('SELECT last_week FROM last_week WHERE user_id=?', (ctx.author.id,))
    row = cursor.fetchone()
    if row is not None:
        last_week = datetime.datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
        if datetime.datetime.now() - last_week < datetime.timedelta(days=7):
            delta = datetime.timedelta(days=7) - (datetime.datetime.now() - last_week)
            delta_str = strfdelta(delta, "{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}")
            # User has already used the command today, so send an error message
            await ctx.send(f"**{ctx.author.name}** can use **!weekly** again in {delta_str}")
            return

    # User hasn't used the command today, so execute the command and update the last used time
    embed=discord.Embed(title="You claimed 10000 Ryō!", description="Come back next week for more!", color=discord.Color.dark_gold())
    embed.set_thumbnail(url="https://www.transparentpng.com/thumb/coin-stack/whiEaR-coin-stack-transparent-image.png")
    embed.set_footer(text="Claimed by " + ctx.author.name, icon_url=ctx.author.avatar)
    await ctx.send(embed=embed)
    cursor = conn_balances.execute('SELECT balance FROM balances WHERE user_id=?', (ctx.author.id,))
    row = cursor.fetchone()
    balance = row[0] + 10000
    conn_balances.execute('UPDATE balances SET balance=? WHERE user_id=?', (balance, ctx.author.id))
    conn_balances.commit()
    conn_last_week.execute('REPLACE INTO last_week VALUES (?, ?)', (ctx.author.id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
    conn_last_week.commit()