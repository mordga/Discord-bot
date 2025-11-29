import discord
from discord.ext import commands
from discord import Forbidden, HTTPException


class Nick(commands.Cog):
    """Cog con comandos para gestionar nicknames de miembros."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de nicknames.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    @commands.command(name="nick")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx: commands.Context, miembro: discord.Member, *, nuevo_nick: str) -> None:
        """Cambia el nickname de un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro cuyo nickname será cambiado
            nuevo_nick: Nuevo nickname para el miembro
        """
        try:
            viejo = miembro.display_name
            await miembro.edit(nick=nuevo_nick)
            embed = discord.Embed(
                title="✏️ Nick cambiado",
                description=f"**{viejo} → {nuevo_nick}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Usuario", value=miembro.mention, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        except Forbidden:
            await ctx.send("❌ No tengo permisos para cambiar nicknames.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al cambiar el nick: {e}")

    @commands.command(name="nickreset")
    @commands.has_permissions(manage_nicknames=True)
    async def nickreset(self, ctx: commands.Context, miembro: discord.Member) -> None:
        """Reinicia el nickname de un miembro al nombre de usuario original.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro cuyo nickname será reiniciado
        """
        try:
            await miembro.edit(nick=None)
            embed = discord.Embed(
                title="🔄 Nick reiniciado",
                description=f"El nick de {miembro.mention} fue restaurado.",
                color=discord.Color.green()
            )
            embed.add_field(name="Miembro", value=miembro.mention, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        except Forbidden:
            await ctx.send("❌ No tengo permisos para cambiar nicknames.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al reiniciar el nick: {e}")


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de nicknames en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(Nick(bot))