import discord
from discord.ext import commands
from cogs.alerts import alerts_data


class Reactions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =============================
    # AJOUT RÉACTIONS
    # =============================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return

        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id not in alerts_data:
            return

        alerts_cog = self.bot.get_cog("AlertsCog")
        if not alerts_cog:
            return

        emoji = str(payload.emoji)

        # 🏆 Victoire
        if emoji == "🏆":
            alerts_data[payload.message_id]["result"] = "win"
            await self._refresh(alerts_cog, payload.message_id)

        # ❌ Défaite
        elif emoji == "❌":
            alerts_data[payload.message_id]["result"] = "lose"
            await self._refresh(alerts_cog, payload.message_id)

        # 😡 Incomplet
        elif emoji == "😡":
            alerts_data[payload.message_id]["incomplete"] = not alerts_data[payload.message_id].get("incomplete", False)
            await self._refresh(alerts_cog, payload.message_id)

    # =============================
    # RETRAIT RÉACTIONS
    # =============================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return

        if payload.message_id not in alerts_data:
            return

        # (optionnel ici, on garde léger)
        emoji = str(payload.emoji)

        if emoji == "👍":
            # réservé si tu réactives système défense plus tard
            pass

    # =============================
    # REFRESH SAFE
    # =============================
    async def _refresh(self, alerts_cog, message_id: int):
        try:
            await alerts_cog.update_alert_message(message_id)
        except Exception:
            # évite crash total bot
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))