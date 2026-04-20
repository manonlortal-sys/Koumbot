import discord
from discord.ext import commands
from cogs.alerts import alerts_data


class Reactions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return

        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in alerts_data:
            return

        emoji = str(payload.emoji)

        # 🏆 victoire
        if emoji == "🏆":
            alerts_data[payload.message_id]["result"] = "win"

        # ❌ défaite
        elif emoji == "❌":
            alerts_data[payload.message_id]["result"] = "lose"

        # 😡 défense incomplète (toggle)
        elif emoji == "😡":
            alerts_data[payload.message_id]["incomplete"] = not alerts_data[payload.message_id].get("incomplete", False)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return

        if payload.message_id not in alerts_data:
            return

        emoji = str(payload.emoji)

        # 👍 retiré → on ne fait rien dans cette version
        if emoji == "👍":
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))