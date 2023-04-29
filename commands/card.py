import discord
import json
import sqlite3
import random

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

ITEMS = {
    'truck_kun': 3.25,
    'super_dragon_balls': 2.85,
    'death_note': 2.5,
    'sword_of_rupture': 2.3,
    'truth_seeking_orbs': 2.2,
    'gun': 2,
    'murasame': 1.9,
    'dragon_slayer': 1.8,
    'odm_gear': 1.7,
    'super_tengen_toppa_gurren_lagann': 2,
    'spear_of_longinus': 1.5,
    'lostvayne': 1.4,
    'katana': 1.3,
    'kunai': 1.2,
    'shuriken': 1.15,
    'eggplant': 1.1,
}

# Create owned_cards table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS owned_cards
             (user_id INTEGER,
              card_id INTEGER,
              value INTEGER,
              item_id INTEGER,
              equiped INTEGER,
              FOREIGN KEY(card_id) REFERENCES cards(id))''')

c.execute('''CREATE TABLE IF NOT EXISTS cards
             (id INTEGER PRIMARY KEY,
              name TEXT,
              value INTEGER,
              url TEXT,
              rank TEXT,
              rarity TEXT,
              anime TEXT)''')

# Load card data
def add_new_cards():
    try:
        with open('db/cards.json', 'r') as f:
            data = json.load(f)
            
        cards = data['cards']
        random.shuffle(cards)  # shuffle the cards list
        
        for card in cards:
            try:
                card_id = card['id']
            except KeyError:
                card_id = None
            c.execute('INSERT INTO cards VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (card_id, card['name'], card['value'], card['url'], card['rank'], card["rarity"], card['anime']))
                     
        conn.commit()
    except FileNotFoundError:
        print('cards.json file not found.')

#add_new_cards()

async def add_card(ctx, card_id: int):
    with open('db/cards.json', 'r') as f:
            data = json.load(f)
    # Check if card_id is valid
    if card_id < 1 or card_id > len(data['cards']):
        await ctx.send('Invalid card ID.')
        return
    
    c.execute('SELECT value FROM cards WHERE id = ?', (card_id,))
    value = c.fetchone()[0]

    # Check if card is already owned by the user
    user_id = ctx.author.id
    c.execute('''SELECT * FROM owned_cards
                 WHERE user_id = ? AND card_id = ? AND value = ?''',
              (user_id, card_id, value))
    result = c.fetchone()
    if result:
        await ctx.send('You already own this card.')
        return

    # Add card to user's collection
    c.execute('INSERT INTO owned_cards VALUES (?, ?, ?, ?, ?)',
              (user_id, card_id, value, 0, 0))
    conn.commit()
    await ctx.send('Card added to your collection.')

async def view_collection(ctx):
    user_id = ctx.author.id
    c.execute('''SELECT cards.id, cards.name, cards.value, cards.url, cards.rank, cards.anime, cards.rarity, owned_cards.item_id
                 FROM owned_cards
                 INNER JOIN cards ON owned_cards.card_id = cards.id
                 WHERE owned_cards.user_id = ?''', (user_id,))
    results = c.fetchall()
    print(results)
    if not results:
        await ctx.send('You don\'t have any cards yet.')
        return

    # Create embed with user's card collection
    embed = discord.Embed(title=f"**{ctx.author.name}'s Card Collection**", color=discord.Color.blurple())
    current_index = 0
    def update_embed():
        nonlocal current_index
        results.sort(key=lambda x: -x[2] * ITEMS.get(x[7], 1))
        embed.clear_fields()
        card_id, name, value, url, rank, anime, rarity, item_id = results[current_index]
        item_name = "---"
        if item_id in ITEMS:
            item_name = list(ITEMS.keys())[list(ITEMS.values()).index(ITEMS[item_id])]
            item_name = f"{item_name.replace('_', ' ').title()} ({ITEMS[item_id]}x)"
            value = int(value * ITEMS[item_id])
        embed.title = f"**{name}**"
        embed.add_field(name="", value=f'**Anime**: {anime}\n**Power**: {value}\n**Rarity**: {rarity}\n**Equipped**: {item_name}', inline=False)
        embed.set_thumbnail(url=rank)
        embed.set_image(url=url)
        embed.set_footer(text=f"{ctx.author.name}'s cards--{current_index+1}/{len(results)} | Card id: {card_id}", icon_url=ctx.author.avatar)

    
    update_embed()
    message = await ctx.send(embed=embed)
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and reaction.message == message and reaction.emoji in ["⬅️", "➡️"]
    

    while True:
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=1800.0, check=check)
        except:
            break

        if reaction.emoji == "➡️":
            current_index = (current_index + 1) % len(results)
        elif reaction.emoji == "⬅️":
            current_index = (current_index - 1) % len(results)

        update_embed()
        await message.edit(embed=embed)
        await reaction.remove(user)

    await message.clear_reactions()