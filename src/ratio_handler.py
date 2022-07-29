from database import Database

import discord
import random
import datetime



timeouts = {}

ratio_accepted_url = "https://cdn.discordapp.com/attachments/997612107291959447/997612302683619418/ratioaccepted.png"
ratio_declined_url = "https://cdn.discordapp.com/attachments/997612107291959447/997612302968827964/ratiodeclined.png"


async def handle_ratio(message: discord.Message, db: Database, is_bot: bool):
    current_date = datetime.datetime.now()
    # Check if user is in 15 s timeouts
    try:
        last_ratio: datetime.date = timeouts[message.author.id]
        seconds_since_last_ratio: float = (current_date - last_ratio).total_seconds()
        print(seconds_since_last_ratio)
        if seconds_since_last_ratio < 15:
            await message.add_reaction('💀')
            return
    except KeyError:
        pass

    # Save new ratio time
    timeouts[message.author.id] = current_date
    # Actually ratio or counter
    is_accepted = random.randint(0, 100) % 2 == 1
    
    # If user is a bot, don't submit score
    if not is_bot:
        db.change_score(message.author.id, message.guild.id, is_accepted)
    
    # Reply
    await message.add_reaction('👍' if is_accepted else '👎')
    await message.channel.send(
        content=ratio_accepted_url if is_accepted else ratio_declined_url,
        reference=message)