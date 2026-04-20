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

ROLE_MAP = {
    "wanted1": 1419320456263237663,
    "wanted2": 1421860260377006295,
    "ateam": 1437841408856948776,
    "moc": 1421927953188524144,
}

TEST_ROLE_ID = 1421867268421320844

COOLDOWN = 30
last_ping = {}

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
# VIEW
# =============================
class AlertView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


# =============================
# COG
# =============================
class AlertsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # =============================
    # EMBED
    # =============================
    def build_embed(self, author_id: int, label: str):
        embed = discord.Embed(
            title="⚠️ Percepteur attaqué",
            description=f"Type : {label}",
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
    # ALERT
    # =============================
    async def send_alert(self, interaction, key: str, role_id: int | None):
        if not check_cooldown(key):
            return await interaction.response.send_message(
                "❌ Cooldown actif.",
                ephemeral=True
            )

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Alerte envoyée.", ephemeral=True)

        if role_id:
            await channel.send(f"<@&{role_id}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id, key),
            view=AlertView()
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    # TEST
    # =============================
    async def send_test(self, interaction):
        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Test envoyé.", ephemeral=True)

        await channel.send(f"<@&{TEST_ROLE_ID}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id, "TEST"),
            view=AlertView()
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    # PANEL
    # =============================
    @app_commands.command(name="panel", description="Panel alertes")
    async def panel(self, interaction: discord.Interaction):

        view = discord.ui.View(timeout=None)

        def make_button(label, role_key):
            async def callback(i: discord.Interaction):
                await self.send_alert(i, role_key, ROLE_MAP[role_key])

            return callback

        # Wanted 1
        b1 = discord.ui.Button(label="Wanted 1", style=discord.ButtonStyle.primary, emoji="⚔️")
        b1.callback = make_button("Wanted 1", "wanted1")
        view.add_item(b1)

        # Wanted 2
        b2 = discord.ui.Button(label="Wanted 2", style=discord.ButtonStyle.primary, emoji="⚔️")
        b2.callback = make_button("Wanted 2", "wanted2")
        view.add_item(b2)

        # A-team
        b3 = discord.ui.Button(label="A-team", style=discord.ButtonStyle.primary, emoji="⚔️")
        b3.callback = make_button("A-team", "ateam")
        view.add_item(b3)

        # MOC
        b4 = discord.ui.Button(label="MOC", style=discord.ButtonStyle.primary, emoji="⚔️")
        b4.callback = make_button("MOC", "moc")
        view.add_item(b4)

        # Rush
        async def rush_callback(i: discord.Interaction):
            await self.send_alert(i, "rush", None)
            await i.channel.send("@everyone")

        rush = discord.ui.Button(label="Rush", style=discord.ButtonStyle.danger, emoji="🚨")
        rush.callback = rush_callback
        view.add_item(rush)

        # Test
        test = discord.ui.Button(label="Test", style=discord.ButtonStyle.secondary, emoji="⚠️")
        test.callback = lambda i: self.send_test(i)
        view.add_item(test)

        embed = discord.Embed(
            title="⚔️ Panel Alertes",
            description="Clique pour envoyer une alerte",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AlertsCog(bot))