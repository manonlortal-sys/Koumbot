import discord
from discord.ext import commands
from cogs.alerts import alerts_data


class Reactions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.guild_id is None:
            return

        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in alerts_data:
            return

        # logique conservée mais safe
        if str(payload.emoji) in ["🏆", "❌", "😡"]:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))