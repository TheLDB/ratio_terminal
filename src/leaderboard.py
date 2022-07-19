from attr import fields
import discord.ext.commands
from models.score import Score
from models.server_info import ServerInfo


def generate_leaderboard(items: ServerInfo) -> discord.Embed:
    embed_description = []
    server_accepted = 0
    server_declined = 0
    for item in items.leaderboard:
        embed_description.append(f'<@{item.user_id}> - `{item.score}`')
        server_accepted += item.accepted_score
        server_declined += item.declined_score
    scores = Score(server_accepted, server_declined)
    return discord.Embed(
        title='✨ Ratio Leaderboard',
        description='\n'.join(embed_description),
        fields=[ 
            discord.EmbedField(name='📍 Server stats', 
                                value=f'{scores.final}'),
            discord.EmbedField(name='📍 👍 Accepted', 
                                value=f'{scores.accepted} ({scores.accepted_ratio}%)', inline=True),
            discord.EmbedField(name='📍 👎 Declined', 
                                value=f'{scores.declined} ({scores.declined_ratio}%)', inline=True),
        ]
    )
