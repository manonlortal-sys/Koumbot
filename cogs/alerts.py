from __future__ import annotations

import time
import discord
from discord.ext import commands
from discord import app_commands

# =============================
# CONFIG
# =============================
PANEL_CHANNEL_ID = 1419318225232986294
ALERT_CHANNEL_ID = 1488527268287610964

PING_TEST_ROLE = 1421867268421320844

ROLE_MAP = {
    "wanted1": 1419320456263237663,
    "wanted2": 1421860260377006295,
    "ateam": 1437841408856948776,
    "moc": 1421927953188524144,
}

COOLDOWN = 30
last_ping = {}

MAX_DEFENDERS = 4

alerts_data = {}

# =============================
# COOLDOWN
# =============================
def check_cooldown(key: str) -> bool:
    now = time.time()
    if key in last_ping and now - last_ping[key] < COOLDOWN:
        return False
    last_ping[key] = now
    return True


# =============================
# VIEW ALERT
# =============================
class AlertView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Ajout défenseurs", style=discord.ButtonStyle.success)
    async def add_def(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "Sélection non activée sans stockage JSON.",
            ephemeral=True
        )

    @discord.ui.button(label="Solo", style=discord.ButtonStyle.danger)
    async def solo(self, interaction: discord.Interaction, _):
        await interaction.response.defer()


# =============================
# COG
# =============================
class AlertsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.alert_view = AlertView(bot)
        bot.add_view(self.alert_view)

    # =============================
    # EMBED
    # =============================
    def build_embed(self, author_id: int, role_name: str = ""):
        embed = discord.Embed(
            title="⚠️ Percepteur attaqué",
            description=f"Type : {role_name}",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="🔔 Déclenché par",
            value=f"<@{author_id}>",
            inline=False
        )

        embed.set_footer(text="Temps réel")
        return embed

    # =============================
    # SEND ALERT
    # =============================
    async def send_alert(self, interaction, role_key: str, ping: str):
        if not check_cooldown(role_key):
            return await interaction.response.send_message(
                "❌ Cooldown actif.",
                ephemeral=True
            )

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Alerte envoyée.", ephemeral=True)

        await channel.send(ping)

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id, role_key),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    # TEST ALERT
    # =============================
    async def send_test(self, interaction):
        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Test envoyé.", ephemeral=True)

        await channel.send(f"<@&{PING_TEST_ROLE}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id, "TEST"),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    # PANEL
    # =============================
    @app_commands.command(name="panel", description="Panel alertes")
    async def panel(self, interaction: discord.Interaction):

        view = discord.ui.View(timeout=None)

        # Wanted 1
        b1 = discord.ui.Button(label="Wanted 1", style=discord.ButtonStyle.primary, emoji="⚔️")
        b1.callback = lambda i: self.send_alert(i, "wanted1", f"<@&{ROLE_MAP['wanted1']}>")
        view.add_item(b1)

        # Wanted 2
        b2 = discord.ui.Button(label="Wanted 2", style=discord.ButtonStyle.primary, emoji="⚔️")
        b2.callback = lambda i: self.send_alert(i, "wanted2", f"<@&{ROLE_MAP['wanted2']}>")
        view.add_item(b2)

        # A-team
        b3 = discord.ui.Button(label="A-team", style=discord.ButtonStyle.primary, emoji="⚔️")
        b3.callback = lambda i: self.send_alert(i, "ateam", f"<@&{ROLE_MAP['ateam']}>")
        view.add_item(b3)

        # MOC
        b4 = discord.ui.Button(label="MOC", style=discord.ButtonStyle.primary, emoji="⚔️")
        b4.callback = lambda i: self.send_alert(i, "moc", f"<@&{ROLE_MAP['moc']}>")
        view.add_item(b4)

        # Rush
        rush = discord.ui.Button(label="Rush", style=discord.ButtonStyle.danger, emoji="🚨")
        async def rush_cb(i):
            await self.send_alert(i, "rush", "@everyone")
        rush.callback = rush_cb
        view.add_item(rush)

        # Test
        test = discord.ui.Button(label="Test", style=discord.ButtonStyle.secondary, emoji="⚠️")
        test.callback = lambda i: self.send_test(i)
        view.add_item(test)

        embed = discord.Embed(
            title="⚔️ Panel Alertes",
            description="Clique pour envoyer une alerte.",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, view=view)


# =============================
# SETUP
# =============================
async def setup(bot: commands.Bot):
    await bot.add_cog(AlertsCog(bot))