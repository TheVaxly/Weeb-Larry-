import discord
import sqlite3
import asyncio

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
    if card[5] == "UR":
        embed = discord.Embed(title=f"**{card[1]}**", description=f"**Power**: {card[2]}\n**Rarity**: {card[5]}\n**Anime**: {card[6]}", color=0xeee657)
        if result:
            embed.set_footer(text=f"Owned by {ctx.author.name} ✅ | Card id: {id}")
        elif not result:
            embed.set_footer(text=f"Owned by {ctx.author.name} ❌ | Card id: {id}")
        embed.set_thumbnail(url=card[4])
        embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
        msg = await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title=f"**{card[1]}**", description=f"**Value**: {card[2]}\n**Rarity**: {card[5]}\n**Anime**: {card[6]}", color=0xeee657)
        if result:
            embed.set_footer(text=f"Owned by {ctx.author.name} ✅ | Card id: {id}")
        elif not result:
            embed.set_footer(text=f"Owned by {ctx.author.name} ❌ | Card id: {id}") 
        embed.set_thumbnail(url=card[4])
        embed.set_image(url=card[3])
        msg = await ctx.send(embed=embed)
        return
    
    while True:
        await msg.add_reaction("👀")
        def check(reaction, user):
            return user == ctx.author and reaction.message == msg and reaction.emoji == "👀"
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
            await msg.edit(embed=embed)
            await msg.clear_reactions()
            return
        if embed.image.url == card[3]:
            embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
        elif embed.image.url == "https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png":
            embed.set_image(url=card[3])
        await msg.edit(embed=embed)
        await reaction.remove(user)