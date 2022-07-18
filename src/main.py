import datetime
import os
import random
import re

import discord
from dotenv import load_dotenv

from database import Database
from enums.leaderboard_order import LeaderboardOrder
from leaderboard import generate_leaderboard
from models.leaderboard_entry import LeaderboardEntry
from models.score import Score

# Set intents
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)
leaderboard = discord.SlashCommandGroup("leaderboard", "Leaderboard commands")

timeouts = {}

ratio_accepted_url = "https://cdn.discordapp.com/attachments/997612107291959447/997612302683619418/ratioaccepted.png"
ratio_declined_url = "https://cdn.discordapp.com/attachments/997612107291959447/997612302968827964/ratiodeclined.png"


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')


@bot.event
async def on_message(message: discord.Message):
    global db
    global timeouts
    # Don't let the bot reply to other bots
    if message.author.bot:
        return
    
    content = message.content.lower()

    # Check if message is a ratio or a counter
    valid_message = re.search(r"(?:^|\W)ratio+(?:$|\W)|counter(?:$|\W)", content) is not None
    if valid_message:
        # Check if user is in 15 s timeout
        try:
            last_ratio: datetime.date = timeouts[message.author.id]
            seconds_since_last_ratio: int = (datetime.datetime.now() - last_ratio).total_seconds()
            if seconds_since_last_ratio < 15:
                await message.add_reaction('💀')
                return
        except KeyError:
            pass

        # Actually ratio or counter
        is_accepted = random.randint(0, 100) % 2 == 1
        db.change_score(message.author.id, message.guild.id, is_accepted)
        await message.add_reaction('👍' if is_accepted else '👎')
        await message.channel.send(
            content=ratio_accepted_url if is_accepted else ratio_declined_url,
            reference=message)
        # Save new ratio time
        timeouts[message.author.id] = datetime.datetime.now()


@leaderboard.command(description='🥇 Ratio gods')
async def top(context: discord.ApplicationContext, 
            limit: discord.Option(int, required=False, default=10, description="Limit amount of leaderboard results. Set zero for all.")):
    items = db.get_server(str(context.guild.id), order=LeaderboardOrder.TOP, limit=limit)
    await context.respond(embed = generate_leaderboard(items))


@leaderboard.command(description='😐 lmao get fucked')
async def last(context: discord.ApplicationContext, 
            limit: discord.Option(int, required=False, default=10, description="Limit amount of leaderboard results. Set zero for all.")):
    items = db.get_server(str(context.guild.id), order=LeaderboardOrder.LAST, limit=limit)
    await context.respond(embed = generate_leaderboard(items))


@bot.slash_command(description='Get your ✨ ratio score ✨')
async def score(context: discord.ApplicationContext,
                user: discord.Option(discord.Member, description="Get someone else's ratio score", required=False)):
    user_data = context.author if user is None else user
    user_id = user_data.id

    if bot.user.id == user_id:
        await context.respond('lol no')
        return

    user_global: Score = db.get_user_global(str(user_id))
    user_server: LeaderboardEntry = db.get_user_server_data(str(user_id), str(context.guild.id))
    await context.respond(embed=discord.Embed(
        title=f'✨ Ratio score - {user_data}',
        fields=[
            discord.EmbedField(name='🌍 Global', value=str(user_global.final), inline=True),
            discord.EmbedField(name='📍 This server', value=str(user_server.score), inline=True)
        ]
    ))


if __name__ == '__main__':
    global db
    exist = os.path.isdir('data')
    if not exist:
        os.mkdir('data')
    # Load environment variables
    load_dotenv(os.path.join("data", ".env"))
    # Do bot stuff
    db = Database()
    bot.add_application_command(leaderboard)
    bot.run(os.environ['DISCORD_TOKEN'])
