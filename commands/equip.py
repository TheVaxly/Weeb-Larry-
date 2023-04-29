import sqlite3
import json

conn = sqlite3.connect('db/cards.db')
c = conn.cursor()

conn_inv = sqlite3.connect('db/inv.db')
c_inv = conn_inv.cursor()

conn_used = sqlite3.connect('db/used_items.db')
c_used = conn_used.cursor()

c_used.execute('''CREATE TABLE IF NOT EXISTS used_items (user_id INTEGER, used_truck_kun INTEGER, used_super_dragon_balls INTEGER, used_death_note INTEGER, used_sword_of_rupture INTEGER, used_truth_seeking_orbs INTEGER, used_gun INTEGER, used_surasame INTEGER, used_dragon_slayer INTEGER, used_odm_gear INTEGER, used_super_tengen_toppa_gurren_lagann INTEGER, used_spear_of_longinus INTEGER, used_lostvayne INTEGER, used_katana INTEGER, used_kunai INTEGER, used_shuriken INTEGER, used_eggplant INTEGER)''')

with open('db/items.json', 'r') as f:
    data = json.load(f)

with open('db/cards.json', 'r') as f:
    card_data = json.load(f)

ITEMS = {
    'truck kun',
    'super dragon balls',
    'death note',
    'sword of rupture',
    'truth seeking orbs',
    'gun',
    'surasame',
    'dragon slayer',
    'odm gear',
    'super tengen toppa gurren lagann',
    'spear of longinus',
    'lostvayne',
    'katana',
    'kunai',
    'shuriken',
    'eggplant',
}

DB_ITEMS = {
    'truck_kun',
    'super_dragon_balls',
    'death_note',
    'sword_of_rupture',
    'truth_seeking_orbs',
    'gun',
    'surasame',
    'dragon_slayer',
    'odm_gear',
    'super_tengen_toppa_gurren_lagann',
    'spear_of_longinus',
    'lostvayne',
    'katana',
    'kunai',
    'shuriken',
    'eggplant',
}

async def equip(ctx, card_id, item_name):
    original_item = ' '.join(item_name)
    item = '_'.join(item_name)
    if item not in DB_ITEMS:
        await ctx.send('Invalid item.')
        return
    c.execute('SELECT * FROM owned_cards WHERE user_id = ? AND card_id = ?', (ctx.author.id, card_id))
    result = c.fetchone()
    if result is None:
        await ctx.send('You do not own this card.')
        return
    else:
        if result[4] == 1:
            await ctx.send('This card is equipped with an item. Please unequip the item first.')
            return
        elif result[4] == 0:
            pass
    c_inv.execute(f'SELECT {item} FROM inv WHERE user_id = ?', (ctx.author.id,))
    resultim = c_inv.fetchone()
    if resultim == (0,):
        await ctx.send('You do not own this item.')
        return
    result_list = list(resultim)
    c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
    results = c_used.fetchone()
    if results is None:
        c_used.execute(f'INSERT INTO used_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (ctx.author.id, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0, 0))
        conn_used.commit()
        c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
        results = c_used.fetchone()
    results_list = list(results)
    if result_list[0] == results_list[0]:
        await ctx.send(f"You have all {original_item} on use.")
        return
    elif result_list[0] > results_list[0]:
        c_used.execute(f'UPDATE used_items SET used_{item} = ? WHERE user_id = ?', (results_list[0] + 1, ctx.author.id))
        conn_used.commit()
    if card_id < 1 or card_id > len(card_data['cards']):
        await ctx.send('Invalid card ID.')
        return
    else:
        c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
        result = c_used.fetchone()
        if result is None:
            c_used.execute(f'INSERT INTO used_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (ctx.author.id, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0, 0))
            conn_used.commit()
            c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
            result = c_used.fetchone()
        list_resulty = list(resultim)
        if result[0] > list_resulty[0]:
            await ctx.send(f"You have all {original_item} on use.")
            return
        c.execute('UPDATE owned_cards SET item_id = ? WHERE user_id = ? AND card_id = ?', (item, ctx.author.id, card_id))
        c.execute('UPDATE owned_cards SET equiped = ? WHERE user_id = ? AND card_id = ?', (1, ctx.author.id, card_id))
        conn.commit()
    await ctx.send(f'Equipped item {original_item} to card {card_id}.')
    return

async def unequip(ctx, card_id):
    if card_id < 1 or card_id > len(card_data['cards']):
        await ctx.send('Invalid card ID.')
        return
    c.execute('SELECT * FROM owned_cards WHERE user_id = ? AND card_id = ?', (ctx.author.id, card_id))
    result = c.fetchone()
    if result is None:
        await ctx.send('You do not own this card.')
        return
    if result[3] == 0:
        await ctx.send('This card does not have an item equipped.')
        return
    else:
        item = result[3]
        c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
        result = c_used.fetchone()
        if result is None:
            c_used.execute(f'INSERT INTO used_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (ctx.author.id, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0, 0))
            conn_used.commit()
            c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
            result = c_used.fetchone()
        c_used.execute(f'UPDATE used_items SET used_{item} = ? WHERE user_id = ?', (result[0] - 1, ctx.author.id))
        conn_used.commit()
        c.execute('UPDATE owned_cards SET item_id = ? WHERE user_id = ? AND card_id = ?', (0, ctx.author.id, card_id))
        c.execute('UPDATE owned_cards SET equiped = ? WHERE user_id = ? AND card_id = ?', (0, ctx.author.id, card_id))
        conn.commit()
        conn_used.commit()
    await ctx.send(f'Unequipped item from card {card_id}.')
    return

async def unequip_item(ctx, item):
    
    c.execute('SELECT * FROM owned_cards WHERE user_id = ? AND item_id = ?', (ctx.author.id, item))
    result = c.fetchone()
    if result is None:
        return
    else:
        c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
        result = c_used.fetchone()
        if result is None:
            c_used.execute(f'INSERT INTO used_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (ctx.author.id, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0, 0))
            conn_used.commit()
            c_used.execute(f'SELECT used_{item} FROM used_items WHERE user_id = ?', (ctx.author.id,))
            result = c_used.fetchone()
        result_list = list(result)
        if result_list[0] == 0:
            return
        c_inv.execute(f'SELECT {item} FROM inv WHERE user_id = ?', (ctx.author.id,))
        resulty = c_inv.fetchone()
        print (resulty)
        c_used.execute(f'UPDATE used_items SET used_{item} = ? WHERE user_id = ?', (result[0] - result_list[0], ctx.author.id))
        c.execute('UPDATE owned_cards SET equiped = ? WHERE user_id = ? AND item_id = ?', (0, ctx.author.id, item))
        c.execute('UPDATE owned_cards SET item_id = ? WHERE user_id = ? AND item_id = ?', (0, ctx.author.id, item))
        conn_used.commit()
        conn.commit()
    return