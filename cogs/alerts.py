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


# =============================
# DEFENSE SELECT
# =============================
class DefenderSelect(discord.ui.UserSelect):
    def __init__(self, bot, alert_id):
        super().__init__(
            placeholder="Sélectionne des défenseurs…",
            min_values=1,
            max_values=MAX_DEFENDERS,
        )
        self.bot = bot
        self.alert_id = alert_id

    async def callback(self, interaction: discord.Interaction):
        data = alerts_data.get(self.alert_id)
        if not data:
            return

        for user in self.values:
            data["defenders"].add(user.id)

        cog = self.bot.get_cog("AlertsCog")
        if cog:
            await cog.update_msg(self.alert_id)

        await interaction.response.edit_message(
            content="Défenseurs ajoutés.",
            view=None
        )


class DefenderSelectView(discord.ui.View):
    def __init__(self, bot, alert_id):
        super().__init__(timeout=60)
        self.add_item(DefenderSelect(bot, alert_id))


class AlertView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Ajout défenseurs",
        style=discord.ButtonStyle.success,
        custom_id="alert_add_defender",
    )
    async def defender_button(self, interaction: discord.Interaction, _):
        alert_id = interaction.message.id
        data = alerts_data.get(alert_id)
        if not data:
            return

        if interaction.user.id not in data["defenders"]:
            return await interaction.response.send_message(
                "Tu dois avoir 👍 sur l’alerte.",
                ephemeral=True,
            )

        view = DefenderSelectView(self.bot, alert_id)
        await interaction.response.send_message(
            "Sélectionne les défenseurs :",
            view=view,
            ephemeral=True,
        )

    # =============================
    # SOLO BUTTON FIXÉ
    # =============================
    @discord.ui.button(
        label="Solo",
        style=discord.ButtonStyle.danger,
        custom_id="alert_solo",
    )
    async def solo_button(self, interaction: discord.Interaction, _):
        alert_id = interaction.message.id
        data = alerts_data.pop(alert_id, None)

        if not data:
            return await interaction.response.defer()

        try:
            await interaction.message.delete()
        except:
            pass

        channel = interaction.guild.get_channel(ALERT_CHANNEL_ID)
        if channel:
            username = interaction.user.display_name
            await channel.send(
                f"⚠️ Une alerte a été supprimée par **{username}**"
            )

        await interaction.response.defer()


# =============================
# COG
# =============================
class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.view = AlertView(bot)
        bot.add_view(self.view)

    # =============================
    def build_embed(self, data):
        state = "⏳ En cours"
        if data["result"] == "win":
            state = "🏆 Victoire"
        elif data["result"] == "lose":
            state = "❌ Défaite"

        if data["incomplete"]:
            state += " (😡 incomplète)"

        defenders = (
            ", ".join(f"<@{d}>" for d in data["defenders"])
            if data["defenders"]
            else "Aucun"
        )

        embed = discord.Embed(
            title="⚠️ Percepteur attaqué",
            description="🗡️ Un percepteur est en cours d’attaque !",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🔔 Déclenché par",
            value=f"<@{data['author']}>",
            inline=False
        )

        embed.add_field(
            name=f"🛡️ Défenseurs ({len(data['defenders'])}/{MAX_DEFENDERS})",
            value=defenders,
            inline=False
        )

        embed.add_field(
            name="📊 État de l’attaque",
            value=state,
            inline=False
        )

        embed.set_footer(
            text="👍 j’ai défendu • 🏆 victoire • ❌ défaite • 😡 défense incomplète"
        )

        return embed

    # =============================
    async def update_msg(self, message_id):
        data = alerts_data.get(message_id)
        if not data:
            return

        channel = self.bot.get_channel(ALERT_CHANNEL_ID)
        msg = await channel.fetch_message(message_id)

        await msg.edit(embed=self.build_embed(data), view=self.view)

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

        msg = await channel.send(embed=self.build_embed(data), view=self.view)
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

        msg = await channel.send(embed=self.build_embed(data), view=self.view)
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
            ("Wanted 1", "🗡️", discord.ButtonStyle.primary, w1),
            ("Wanted 2", "🗡️", discord.ButtonStyle.primary, w2),
            ("A-team", "🗡️", discord.ButtonStyle.primary, at),
            ("MOC", "🗡️", discord.ButtonStyle.primary, moc),
            ("Rush", "🚨", discord.ButtonStyle.danger, rush),
            ("Test", "⚠️", discord.ButtonStyle.secondary, test),
        ]

        for label, emoji, style, cb in buttons:
            b = discord.ui.Button(label=label, emoji=emoji, style=style)
            b.callback = cb
            view.add_item(b)

        await interaction.response.send_message(
            "⚔️ Panel de défense percepteurs\nClique sur un bouton pour envoyer une alerte.",
            view=view
        )


async def setup(bot):
    await bot.add_cog(AlertsCog(bot))