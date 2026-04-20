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
ROLE_TEST = 1421867268421320844

MAX_DEFENDERS = 4
COOLDOWN = 30

last_ping = {}
alerts_data = {}


def check_cd(key):
    now = time.time()
    if key in last_ping and now - last_ping[key] < COOLDOWN:
        return False
    last_ping[key] = now
    return True


class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =============================
    def build_embed(self, data):
        embed = discord.Embed(
            title="⚠️ Alerte Percepteur",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Auteur",
            value=f"<@{data['author']}>",
            inline=False
        )

        defenders = (
            ", ".join(f"<@{d}>" for d in data["defenders"])
            if data["defenders"]
            else "Aucun"
        )

        embed.add_field(
            name=f"Défenseurs ({len(data['defenders'])}/{MAX_DEFENDERS})",
            value=defenders,
            inline=False
        )

        state = "⏳ En cours"
        if data["result"] == "win":
            state = "🏆 Victoire"
        elif data["result"] == "lose":
            state = "❌ Défaite"

        if data["incomplete"]:
            state += " (incomplète)"

        embed.add_field(name="État", value=state, inline=False)

        embed.set_footer(text="Réactions live")

        return embed

    # =============================
    async def update_msg(self, message_id):
        data = alerts_data.get(message_id)
        if not data:
            return

        channel = self.bot.get_channel(ALERT_CHANNEL_ID)
        msg = await channel.fetch_message(message_id)

        await msg.edit(embed=self.build_embed(data))

    # =============================
    async def send_alert(self, interaction, role_id):
        if not check_cd(role_id):
            return await interaction.response.send_message("Cooldown", ephemeral=True)

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)
        await interaction.response.send_message("Alerte envoyée", ephemeral=True)

        await channel.send(f"<@&{role_id}>")

        data = {
            "author": interaction.user.id,
            "defenders": set(),
            "result": None,
            "incomplete": False,
        }

        msg = await channel.send(embed=self.build_embed(data))
        alerts_data[msg.id] = data

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

    # =============================
    async def send_rush(self, interaction):
        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)
        await interaction.response.send_message("Rush envoyé", ephemeral=True)
        await channel.send("@everyone")

    # =============================
    async def send_test(self, interaction):
        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)
        await interaction.response.send_message("Test envoyé", ephemeral=True)

        await channel.send(f"<@&{ROLE_TEST}>")

        data = {
            "author": interaction.user.id,
            "defenders": set(),
            "result": None,
            "incomplete": False,
        }

        msg = await channel.send(embed=self.build_embed(data))
        alerts_data[msg.id] = data

        for e in ("👍", "🏆", "❌", "😡"):
            await msg.add_reaction(e)

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
            ("Wanted 1", "⚔️", discord.ButtonStyle.primary, w1),
            ("Wanted 2", "⚔️", discord.ButtonStyle.primary, w2),
            ("A-team", "⚔️", discord.ButtonStyle.primary, at),
            ("MOC", "⚔️", discord.ButtonStyle.primary, moc),
            ("Rush", "🚨", discord.ButtonStyle.danger, rush),
            ("Test", "⚠️", discord.ButtonStyle.secondary, test),
        ]

        for label, emoji, style, cb in buttons:
            b = discord.ui.Button(label=label, emoji=emoji, style=style)
            b.callback = cb
            view.add_item(b)

        await interaction.response.send_message("Panel alertes", view=view)


async def setup(bot):
    await bot.add_cog(AlertsCog(bot))