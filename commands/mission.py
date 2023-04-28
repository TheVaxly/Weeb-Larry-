import discord
import json
import random
import sqlite3
import asyncio
import time

conn_bal = sqlite3.connect('db/balances.db')

def get_balance(user_id):
    cursor = conn_bal.execute("SELECT balance FROM balances WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        conn_bal.execute("INSERT INTO balances (user_id, balance) VALUES (?, ?)", (user_id, 1000))
        conn_bal.commit()
        return 1000
    else:
        return row[0]

# Load questions from JSON file
with open('db/questions.json', 'r') as f:
    questions = json.load(f)['questions']

last_mission_times = {}

async def mission(message, client):
    # Check if user must wait before using mission command again
    current_time = time.time()
    last_mission_time = last_mission_times.get(message.author.id)
    if last_mission_time is not None and current_time - last_mission_time < 60:
        wait_time = int(60 - (current_time - last_mission_time))
        await message.channel.send(f"Wait {wait_time}s for your next quiz **{message.author.name}**.")
        return
    # Update user's last mission time
    last_mission_times[message.author.id] = current_time
    # Select a random question
    question = random.choice(questions)

    # Shuffle the answers
    answers = question['answers']
    random.shuffle(answers)

    # Send the question and the answers
    question_text = ""
    for i, answer in enumerate(answers):
        question_text += f"{i+1}. {answer}\n"
    embed = discord.Embed(title=f'{question["question"]}', description=question_text, color=0x00ff00)
    embed.set_footer(text=f"You have 20 seconds to answer the question.", icon_url=message.author.avatar)
    embed.set_thumbnail(url="https://assets.pokemon.com/assets/cms2/img/pokedex/full/025.png")
    msg = await message.channel.send(embed=embed)

    # Add reaction emojis
    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")
    await msg.add_reaction("3️⃣")

    def check(reaction, user):
        return user == message.author and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣"]

    # Check if the reaction is correct within 20 seconds
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=20, check=check)
    except asyncio.TimeoutError:
        response_text = "Time is up! ⌛️"
        embed.set_footer(text=response_text, icon_url=message.author.avatar)
        await msg.edit(embed=embed)
        return

    # Calculate the reward
    reward = random.randint(5, 10) * 50

    # Check the answer
    if answers[int(str(reaction.emoji)[0])-1] == question['correct']:
        response_text = f"Correct answer ✅! You have earned {reward} Ryō."
        conn_bal.execute("UPDATE balances SET balance = ? WHERE user_id = ?", (reward+get_balance(message.author.id), message.author.id))
        conn_bal.commit()
    else:
        response_text = f"Wrong answer ❌!"

    # Add the response as a footer to the original message
    embed.set_footer(text=response_text, icon_url=message.author.avatar)
    await msg.edit(embed=embed)
