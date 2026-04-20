from __future__ import annotations

import time
import discord
from discord.ext import commands
from discord import app_commands

# =============================
# CONFIG
# =============================
ALERT_CHANNEL_ID = 1488527268287610964

ROLE_WANTED_1 = 1419320456263237663
ROLE_WANTED_2 = 1421860260377006295
ROLE_ATEAM = 1437841408856948776
ROLE_MOC = 1421927953188524144

ROLE_TEST_ID = 1421867268421320844

COOLDOWN = 30
last_ping = {}

alerts_data: dict[int, dict] = {}

# =============================
# UTILS
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

    def build_embed(self, user_id):
        embed = discord.Embed(
            title="⚠️ Percepteur attaqué",
            description="🗡️ Alerte en cours",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Déclenché par",
            value=f"<@{user_id}>",
            inline=False
        )

        return embed

    async def send_alert(self, interaction, role_id):
        if not check_cooldown(str(role_id)):
            return await interaction.response.send_message("Cooldown actif", ephemeral=True)

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Alerte envoyée", ephemeral=True)

        await channel.send(f"<@&{role_id}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

        alerts_data[msg.id] = {"result": None, "incomplete": False}

    async def send_rush(self, interaction):
        if not check_cooldown("rush"):
            return await interaction.response.send_message("Cooldown actif", ephemeral=True)

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Rush envoyé", ephemeral=True)

        await channel.send("@everyone")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

        alerts_data[msg.id] = {"result": None, "incomplete": False}

    async def send_test(self, interaction):
        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)

        await interaction.response.send_message("Test envoyé", ephemeral=True)

        await channel.send(f"<@&{ROLE_TEST_ID}>")

        msg = await channel.send(
            embed=self.build_embed(interaction.user.id),
            view=self.alert_view
        )

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

        alerts_data[msg.id] = {"result": None, "incomplete": False}

    # =============================
    # PANEL
    # =============================
    @app_commands.command(name="pingpanel", description="Panel alertes")
    async def pingpanel(self, interaction: discord.Interaction):

        view = discord.ui.View(timeout=None)

        async def w1(i): await self.send_alert(i, ROLE_WANTED_1)
        async def w2(i): await self.send_alert(i, ROLE_WANTED_2)
        async def at(i): await self.send_alert(i, ROLE_ATEAM)
        async def moc(i): await self.send_alert(i, ROLE_MOC)
        async def rush(i): await self.send_rush(i)
        async def test(i): await self.send_test(i)

        buttons = [
            ("Wanted 1", "🗡️", w1, discord.ButtonStyle.primary),
            ("Wanted 2", "🗡️", w2, discord.ButtonStyle.primary),
            ("A-team", "🗡️", at, discord.ButtonStyle.primary),
            ("MOC", "🗡️", moc, discord.ButtonStyle.primary),
            ("Rush", "🚨", rush, discord.ButtonStyle.danger),
            ("Test", "⚠️", test, discord.ButtonStyle.secondary),
        ]

        for label, emoji, cb, style in buttons:
            btn = discord.ui.Button(label=label, emoji=emoji, style=style)
            btn.callback = cb
            view.add_item(btn)

        embed = discord.Embed(
            title="⚔️ Panel défense",
            description="Clique pour envoyer une alerte",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(AlertsCog(bot))