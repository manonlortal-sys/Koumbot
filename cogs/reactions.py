import discord
from discord.ext import commands
from cogs.alerts import alerts_data


class Reactions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =============================
    # REFRESH SAFE
    # =============================
    async def refresh(self, payload: discord.RawReactionActionEvent):
        cog = self.bot.get_cog("AlertsCog")
        if not cog:
            return

        try:
            await cog.update_msg(payload.message_id)
        except Exception:
            pass

    # =============================
    # ADD REACTION
    # =============================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if payload.guild_id is None:
            return

        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in alerts_data:
            return

        data = alerts_data[payload.message_id]
        emoji = str(payload.emoji)

        # =====================
        # 👍 DEFENSEUR
        # =====================
        if emoji == "👍":
            data["defenders"].add(payload.user_id)

        # =====================
        # 🏆 VICTOIRE
        # =====================
        elif emoji == "🏆":
            data["result"] = "win"

        # =====================
        # ❌ DÉFAITE
        # =====================
        elif emoji == "❌":
            data["result"] = "lose"

        # =====================
        # 😡 INCOMPLET (TOGGLE)
        # =====================
        elif emoji == "😡":
            data["incomplete"] = not data.get("incomplete", False)

        await self.refresh(payload)

    # =============================
    # REMOVE REACTION
    # =============================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):

        if payload.guild_id is None:
            return

        if payload.message_id not in alerts_data:
            return

        data = alerts_data[payload.message_id]
        emoji = str(payload.emoji)

        # =====================
        # RETRAIT DEFENSEUR
        # =====================
        if emoji == "👍":
            data["defenders"].discard(payload.user_id)

        await self.refresh(payload)


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))