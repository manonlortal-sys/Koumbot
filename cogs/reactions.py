import discord
from discord.ext import commands
from cogs.alerts import alerts_data


class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def refresh(self, payload):
        cog = self.bot.get_cog("AlertsCog")
        if not cog:
            return

        data = alerts_data.get(payload.message_id)
        if not data:
            return

        await cog.update_msg(payload.message_id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id not in alerts_data:
            return

        data = alerts_data[payload.message_id]
        emoji = str(payload.emoji)

        if emoji == "🏆":
            data["result"] = "win"
        elif emoji == "❌":
            data["result"] = "lose"
        elif emoji == "😡":
            data["incomplete"] = not data["incomplete"]

        await self.refresh(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        pass


async def setup(bot):
    await bot.add_cog(Reactions(bot))