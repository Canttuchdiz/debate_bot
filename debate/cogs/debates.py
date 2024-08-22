import asyncio
import discord
from discord import app_commands, Interaction, User, Member, Color, Embed, CategoryChannel
from discord.ext import commands
from debate.utils.extentsions import PrismaExt
from discord.types.snowflake import Snowflake
from typing import Union
import traceback


class Debates(commands.Cog):
    group = app_commands.Group(name="debate", description="Debate related commands")

    def __init__(self, bot: commands.Bot) -> None:
        self.client = bot
        self.prisma = PrismaExt()
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.prisma.connect_client())

    @app_commands.command(name="debates", description="Lists all logged debates")
    async def debates(self, interaction: Interaction) -> None:
        embed = discord.Embed(title="Debate Logs", color=Color.blue())
        records = await self.prisma.debate.find_many()
        for record in records:
            user1 = interaction.guild.get_member(record.userID1)
            user2 = interaction.guild.get_member(record.userID2)
            winner = interaction.guild.get_member(record.winnerID)

            embed.add_field(name=f"{user1.name} vs {user2.name}",
                            value=f"Topic: {record.topic}\nWinner: {winner.name}\nID: {record.id}")
        await interaction.response.send_message(embed=embed)

    @group.command(name="add", description="Adds debate to records")
    async def add(self, interaction: Interaction, debater1: Member, debater2: Member, topic: str, winner: Member) -> None:
        await self.prisma.debate.create(
            data={
                'userID1': debater1.id,
                'userID2': debater2.id,
                'topic': topic,
                'winnerID': winner.id
            }
        )
        await interaction.response.send_message("Debate result logged!")

    @group.command(name="remove", description="Removes debate from records")
    async def remove(self, interaction: Interaction, debate_id: str) -> None:
        await self.prisma.debate.delete(
            where={
                'id': debate_id
            }
        )
        await interaction.response.send_message("Record removed!")


async def setup(bot):
    await bot.add_cog(Debates(bot))
