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

        alerts_cog = self.bot.get_cog("AlertsCog")
        if not alerts_cog:
            return

        emoji = str(payload.emoji)

        # 👍 Ajout défenseur (non fonctionnel côté UI sans stockage mais logique conservée)
        if emoji == "👍":
            # actuellement désactivé fonctionnellement car pas de stockage utilisateur détaillé
            pass

        # 🏆 Victoire
        elif emoji == "🏆":
            alerts_data[payload.message_id]["result"] = "win"
            await alerts_cog.update_alert_message(payload.message_id)

        # ❌ Défaite
        elif emoji == "❌":
            alerts_data[payload.message_id]["result"] = "lose"
            await alerts_cog.update_alert_message(payload.message_id)

        # 😡 Incomplet
        elif emoji == "😡":
            alerts_data[payload.message_id]["incomplete"] = not alerts_data[payload.message_id]["incomplete"]
            await alerts_cog.update_alert_message(payload.message_id)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return

        if payload.message_id not in alerts_data:
            return

        # 👍 retrait défenseur (désactivé fonctionnellement sans système de stockage avancé)
        if str(payload.emoji) == "👍":
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Reactions(bot))