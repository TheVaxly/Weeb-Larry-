import discord
import sqlite3

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

def get_card(id):
    cursor = conn.execute("SELECT * FROM cards WHERE id=?", (id,))
    row = cursor.fetchone()
    if row is None:
        return None
    else:
        return row

async def show(ctx, id):
    card = get_card(id)
    if card is None:
        await ctx.send("Invalid card ID.")
        return
    c.execute('''SELECT * FROM owned_cards
                 WHERE user_id = ? AND card_id = ? AND value = ?''',
              (ctx.author.id, id, card[2]))
    result = c.fetchone()
    embed = discord.Embed(title=f"**{card[1]}**", description=f"**Value**: {card[2]}\n**Rarity**: {card[5]}\n**Anime**: {card[6]}", color=0xeee657)
    if result:
        embed.set_footer(text=f"Owned by {ctx.author.name} ✅")
    elif not result:
        embed.set_footer(text=f"Owned by {ctx.author.name} ❌") 
    embed.set_thumbnail(url=card[4])
    embed.set_image(url=card[3])
    await ctx.send(embed=embed)