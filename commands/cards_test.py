import discord
import json
import sqlite3
import asyncio

with open('db/cards.json', 'r') as f:
    data = json.load(f)

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

nr = 1

async def carddd(ctx):
    global nr
    data["cards"] = sorted(data["cards"], key=lambda c: c["value"], reverse=True)
    a = data["cards"][nr-1] # get the card data for the new page
    name = a["name"]
    value = a["value"]
    url = a["url"]
    rank = a["rank"]
    rarity = a["rarity"]
    anime = a["anime"]
    user_id = ctx.author.id
    # Create embed with user's card collection
    embed = discord.Embed(title=f'**{name}**', color=discord.Color.dark_red())
    current_index = 0

    card_id = current_index + 1
    embed.title = f'**{name}**'
    c.execute('''SELECT id FROM cards
                WHERE name = ?''',
            (name,))
    result = c.fetchone()
    if result:
        card_original_id = result[0]
    else:
        card_original_id = "Unknown"
    c.execute('''SELECT * FROM owned_cards
                WHERE user_id = ? AND card_id = ? AND value = ?''',
            (user_id, card_id, value))
    result = c.fetchone()
    embed.clear_fields()
    if result:
        embed.set_footer(text=f"Owned by {ctx.author.name} ✅\nAll cards--{current_index+1}/{len(data['cards'])} | Card ID: {card_original_id}", icon_url=ctx.author.avatar)
    elif not result:
        embed.set_footer(text=f"Owned by {ctx.author.name} ❌\nAll cards--{current_index+1}/{len(data['cards'])} | Card ID: {card_original_id}", icon_url=ctx.author.avatar)
    embed.add_field(name="", value=f'**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}', inline=False)
    embed.set_thumbnail(url=rank)
    if rarity == "UR":
        embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
    else:
        embed.set_image(url=url)

    message = await ctx.send(embed=embed)
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    # await message.add_reaction("👀")

    def check(reaction, user):
        return user == ctx.author and reaction.message == message and reaction.emoji in ["⬅️", "➡️", "👀"]

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            if rarity == "UR":
                embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
            else:
                embed.set_image(url=url)
            await message.edit(embed=embed)
            await message.clear_reactions()
            return
        if reaction.emoji == "👀":
            if rarity == "UR" and embed.image.url == "https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png":
                embed.set_image(url=url)
            elif rarity == "UR" and embed.image.url == url:
                embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
        if reaction.emoji == "➡️":
            current_index = (current_index + 1) % len(data['cards'])
            a = data["cards"][current_index] # get the card data for the new page
            name = a["name"]
            value = a["value"]
            url = a["url"]
            rank = a["rank"]
            rarity = a["rarity"]
            anime = a["anime"]
            card_id = current_index + 1
            embed.title = f'**{name}**'
            c.execute('''SELECT id FROM cards
                        WHERE name = ?''',
                    (name,))
            result = c.fetchone()
            if result:
                card_original_id = result[0]
            else:
                card_original_id = "Unknown"
            c.execute('''SELECT * FROM owned_cards
                        WHERE user_id = ? AND card_id = ? AND value = ?''',
                    (user_id, card_id, value))
            result = c.fetchone()
            embed.clear_fields()
            if result:
                embed.set_footer(text=f"Owned by {ctx.author.name} ✅\nAll cards--{current_index+1}/{len(data['cards'])} | Card ID: {card_original_id}", icon_url=ctx.author.avatar)
            elif not result:
                embed.set_footer(text=f"Owned by {ctx.author.name} ❌\nAll cards--{current_index+1}/{len(data['cards'])} | Card ID: {card_original_id}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f'**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}', inline=False)
            embed.set_thumbnail(url=rank)
            if rarity == "UR":
                embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
            else:
                embed.set_image(url=url)
        elif reaction.emoji == "⬅️":
            current_index = (current_index - 1) % len(data['cards'])
            a = data["cards"][current_index]
            name = a["name"]
            value = a["value"]
            url = a["url"]
            rank = a["rank"]
            rarity = a["rarity"]
            anime = a["anime"]
            card_id = current_index + 1
            embed.title = f'**{name}**'
            c.execute('''SELECT id FROM cards
                        WHERE name = ?''',
                    (name,))
            result = c.fetchone()
            if result:
                card_original_id = result[0]
            else:
                card_original_id = "Unknown"
            c.execute('''SELECT * FROM owned_cards
                        WHERE user_id = ? AND card_id = ? AND value = ?''',
                    (user_id, card_id, value))
            result = c.fetchone()
            embed.clear_fields()
            if result:
                embed.set_footer(text=f"Owned by {ctx.author.name} ✅\nAll cards--{current_index+1}/{len(data['cards'])} | Card ID: {card_original_id}", icon_url=ctx.author.avatar)
            elif not result:
                embed.set_footer(text=f"Owned by {ctx.author.name} ❌\nAll cards--{current_index+1}/{len(data['cards'])} | Card ID: {card_original_id}", icon_url=ctx.author.avatar)
            embed.add_field(name="", value=f'**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}', inline=False)
            embed.set_thumbnail(url=rank)
            if rarity == "UR":
                embed.set_image(url="https://cdn.discordapp.com/attachments/1094961509727211590/1101233376054235237/image.png")
            else:
                embed.set_image(url=url)
        await message.edit(embed=embed)
        await message.remove_reaction(reaction, user)