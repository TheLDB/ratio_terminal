import os
import re

import discord
from dotenv import load_dotenv

from database import Database
from enums.leaderboard_order import LeaderboardOrder
from leaderboard import generate_leaderboard
from models.leaderboard_entry import LeaderboardEntry
from models.score import Score
from ratio_handler import handle_ratio


# Set intents
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)
leaderboard = discord.SlashCommandGroup("leaderboard", "Leaderboard commands")


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')


@bot.event
async def on_message(message: discord.Message):
    global db
    # Don't let the bot reply to other bots
    if message.author.bot:
        return
    
    content = message.content.lower()

    # Check if message is a ratio or a counter
    valid_message = re.search(r"(?:^|\W)ratio+(?:$|\W)|counter(?:$|\W)", content) is not None
    if valid_message:
        await handle_ratio(message, db)


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
    user_server_temp: LeaderboardEntry = db.get_user_server_data(str(user_id), str(context.guild.id))
    user_server: Score = Score(user_server_temp.accepted_score, user_server_temp.declined_score)
    await context.respond(embed=discord.Embed(
        title=f'✨ Ratio score - {user_data}',
        fields=[
            discord.EmbedField(name='🌍 Global', 
                                value=f'{user_global.final}'),
            discord.EmbedField(name='🌍 👍 Accepted', 
                                value=f'{user_global.accepted} ({user_global.accepted_ratio}%)', inline=True),
            discord.EmbedField(name='🌍 👎 Declined', 
                                value=f'{user_global.declined} ({user_global.declined_ratio}%)', inline=True),
            discord.EmbedField(name='📍 This server', 
                                value=f'{user_server.final}'),
            discord.EmbedField(name='📍 👍 Accepted', 
                                value=f'{user_server.accepted} ({user_server.accepted_ratio}%)', inline=True),
            discord.EmbedField(name='📍 👎 Declined', 
                                value=f'{user_server.declined} ({user_server.declined_ratio}%)', inline=True),
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
