import discord
import json
import sqlite3

with open('db/cards.json', 'r') as f:
    data = json.load(f)

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

nr = 1
    
async def carddd(ctx):
    a = data["cards"][nr-1] # get the card data for the new page
    name = a["name"]
    value = a["value"]
    url = a["url"]
    rank = a["rank"]
    user_id = ctx.author.id
    # Create embed with user's card collection
    embed = discord.Embed(title='**Entire Collection**', color=discord.Color.dark_red())
    current_index = 0

    def update_embed():
        nonlocal current_index, name, value, url
        card_id = current_index + 1
        c.execute('''SELECT * FROM owned_cards
                 WHERE user_id = ? AND card_id = ?''',
              (user_id, card_id))
        result = c.fetchone()
        embed.clear_fields()
        if result:
            embed.set_footer(text=f"Owned by {ctx.author.name} ✅ | Card {current_index+1}/{len(data['cards'])}")
        elif not result:
            embed.set_footer(text=f"Owned by {ctx.author.name} ❌ | Card {current_index+1}/{len(data['cards'])}")
        embed.add_field(name=name, value=f'**Power**: {value}', inline=False)
        embed.set_thumbnail(url=rank)
        embed.set_image(url=url)
    
    update_embed()
    message = await ctx.send(embed=embed)
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and reaction.message == message and reaction.emoji in ["⬅️", "➡️"]

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except:
            break

        if reaction.emoji == "➡️":
            current_index = (current_index + 1) % len(data['cards'])
            a = data["cards"][current_index] # get the card data for the new page
            name = a["name"]
            value = a["value"]
            url = a["url"]
        elif reaction.emoji == "⬅️":
            current_index = (current_index - 1) % len(data['cards'])
            a = data["cards"][current_index] # get the card data for the new page
            name = a["name"]
            value = a["value"]
            url = a["url"]

        update_embed()
        await message.edit(embed=embed)
        await reaction.remove(user)

    await message.clear_reactions()
