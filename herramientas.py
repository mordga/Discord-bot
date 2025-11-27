import discord
from discord.ext import commands
from discord import HTTPException, Forbidden


class Herramientas(commands.Cog):
    """Cog con comandos de herramientas útiles para el servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de herramientas.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    @commands.command(name="say")
    async def say(self, ctx: commands.Context, *, mensaje: str) -> None:
        """Repite un mensaje y elimina el comando.
        
        Args:
            ctx: Contexto del comando
            mensaje: Mensaje a repetir
        """
        try:
            await ctx.message.delete()
            await ctx.send(mensaje)
        except Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al enviar el mensaje: {e}")

    @commands.command(name="sayembed")
    async def sayembed(self, ctx: commands.Context, *, mensaje: str) -> None:
        """Repite un mensaje en un embed y elimina el comando.
        
        Args:
            ctx: Contexto del comando
            mensaje: Mensaje a mostrar en el embed
        """
        try:
            await ctx.message.delete()
            embed = discord.Embed(description=mensaje, color=discord.Color.blue())
            embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al enviar el mensaje: {e}")

    @commands.command(name="announce")
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx: commands.Context, canal: discord.TextChannel, *, mensaje: str) -> None:
        """Envía un anuncio a un canal especificado.
        
        Args:
            ctx: Contexto del comando
            canal: Canal de destino para el anuncio
            mensaje: Contenido del anuncio
        """
        if not canal:
            await ctx.send("❌ Debes especificar un canal válido.")
            return

        try:
            embed = discord.Embed(
                title="📢 Anuncio",
                description=mensaje,
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"Enviado por {ctx.author}", icon_url=ctx.author.display_avatar.url)
            await canal.send(embed=embed)
            await ctx.send("✅ Anuncio enviado correctamente.")
        except Forbidden:
            await ctx.send(f"❌ No tengo permisos para enviar mensajes en {canal.mention}")
        except HTTPException as e:
            await ctx.send(f"❌ Error al enviar el anuncio: {e}")


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de herramientas en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(Herramientas(bot))