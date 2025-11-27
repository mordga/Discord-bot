"""
Módulo de herramientas y utilidades para el bot de Discord.
"""

import discord
from discord.ext import commands
from typing import Optional, Union


class Herramientas:
    """Clase con funciones de utilidad para el bot."""

    @staticmethod
    def crear_embed(titulo: str, descripcion: str = "", color: discord.Color = discord.Color.blurple()) -> discord.Embed:
        """Crea un embed estándar."""
        embed = discord.Embed(title=titulo, description=descripcion, color=color)
        return embed

    @staticmethod
    async def verificar_permisos(ctx: commands.Context, permiso: str) -> bool:
        """Verifica si el usuario tiene un permiso específico."""
        if isinstance(ctx.author, discord.Member):
            return getattr(ctx.author.guild_permissions, permiso, False)
        return False

    @staticmethod
    def es_canal_texto(channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]) -> bool:
        """Verifica si el canal es un canal de texto."""
        return isinstance(channel, discord.TextChannel)
