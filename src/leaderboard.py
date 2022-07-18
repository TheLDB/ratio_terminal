import discord.ext.commands
from models.server_info import ServerInfo


def generate_leaderboard(items: ServerInfo) -> discord.Embed:
    embed_description = []
    for item in items.leaderboard:
        embed_description.append(f'<@{item.user_id}> - `{item.score}`')
    return discord.Embed(
        title='✨ Ratio Leaderboard',
        description='\n'.join(embed_description)
    )
