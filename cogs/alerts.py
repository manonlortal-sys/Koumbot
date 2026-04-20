from __future__ import annotations

import time
import json
import os
import discord
from discord.ext import commands
from discord import app_commands

# =============================
# CONFIG NOUVEAU BOT
# =============================
ALERT_CHANNEL_ID = 1488527268287610964
PANEL_CHANNEL_ID = 1419318225232986294

ROLE_WANTED_1 = 1419320456263237663
ROLE_WANTED_2 = 1421860260377006295
ROLE_ATEAM = 1437841408856948776
ROLE_MOC = 1421927953188524144

ROLE_TEST_ID = 1421867268421320844

ADMIN_ROLE_ID = 1139578015676895342

COOLDOWN = 30
last_ping = {}

alerts_data: dict[int, dict] = {}

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
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot


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
    def build_embed(self, author_id: int, label: str):
        embed = discord.Embed(
            title="⚠️ Percepteur attaqué",
            description=label,
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Déclenché par",
            value=f"<@{author_id}>",
            inline=False
        )

        return embed

    # =============================
    # ALERT
    # =============================
    async def send_alert(self, interaction, role_id: int):
        if not check_cooldown(str(role_id)):
            return await interaction.response.send_message(
                "Cooldown actif",
                ephemeral=True
            )

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Alerte envoyée", ephemeral=True)

        await channel.send(f"<@&{role_id}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id, "Alerte percepteur"),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    # TEST
    # =============================
    async def send_test(self, interaction):
        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Test envoyé", ephemeral=True)

        await channel.send(f"<@&{ROLE_TEST_ID}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id, "TEST"),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    # PANEL
    # =============================
    @app_commands.command(name="pingpanel", description="Panel alertes")
    async def pingpanel(self, interaction: discord.Interaction):

        view = discord.ui.View(timeout=None)

        async def wanted1(i):
            await self.send_alert(i, ROLE_WANTED_1)

        async def wanted2(i):
            await self.send_alert(i, ROLE_WANTED_2)

        async def ateam(i):
            await self.send_alert(i, ROLE_ATEAM)

        async def moc(i):
            await self.send_alert(i, ROLE_MOC)

        async def rush(i):
            await self.send_alert(i, ROLE_WANTED_1)
            await i.channel.send("@everyone")

        async def test(i):
            await self.send_test(i)

        buttons = [
            ("Wanted 1", "🗡️", wanted1),
            ("Wanted 2", "🗡️", wanted2),
            ("A-team", "🗡️", ateam),
            ("MOC", "🗡️", moc),
            ("Rush", "🚨", rush),
            ("Test", "⚠️", test),
        ]

        for label, emoji, cb in buttons:
            style = discord.ButtonStyle.primary if label != "Rush" else discord.ButtonStyle.danger
            if label == "Test":
                style = discord.ButtonStyle.secondary

            btn = discord.ui.Button(label=label, emoji=emoji, style=style)
            btn.callback = cb
            view.add_item(btn)

        embed = discord.Embed(
            title="Panel alertes",
            description="Clique pour envoyer une alerte",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AlertsCog(bot))