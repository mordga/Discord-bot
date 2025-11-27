import discord
from discord.ext import commands
from discord import Forbidden, HTTPException, TextChannel


class Limpieza(commands.Cog):
    """Cog con comandos para limpiar mensajes del servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de limpieza.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    def _embed(self, titulo: str, ctx: commands.Context, info: str) -> discord.Embed:
        """Crea un embed estándar para los comandos de limpieza.
        
        Args:
            titulo: Título del embed
            ctx: Contexto del comando
            info: Información a mostrar
            
        Returns:
            Embed creado
        """
        e = discord.Embed(title=titulo, color=discord.Color.green())
        channel = ctx.channel
        if isinstance(channel, TextChannel):
            e.add_field(name="Canal", value=channel.mention, inline=False)
        e.add_field(name="Resultado", value=info, inline=False)
        e.set_footer(text=f"Solicitado por {ctx.author}")
        return e

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, cantidad: int) -> None:
        """Limpia una cantidad de mensajes del canal.
        
        Args:
            ctx: Contexto del comando
            cantidad: Cantidad de mensajes a eliminar
        """
        if cantidad < 1:
            await ctx.send("❌ La cantidad debe ser mayor a 0.")
            return
        try:
            channel = ctx.channel
            if isinstance(channel, TextChannel):
                eliminados = await channel.purge(limit=cantidad + 1)
                await ctx.send(
                    embed=self._embed("🧹 Limpieza", ctx, f"Se eliminaron **{len(eliminados)-1}** mensajes."),
                    delete_after=5
                )
        except Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al eliminar mensajes: {e}")

    @commands.command(name="clearuser")
    @commands.has_permissions(manage_messages=True)
    async def clearuser(self, ctx: commands.Context, usuario: discord.Member, cantidad: int = 100) -> None:
        """Limpia mensajes de un usuario específico.
        
        Args:
            ctx: Contexto del comando
            usuario: Usuario cuyos mensajes se limpiarán
            cantidad: Cantidad máxima de mensajes a revisar
        """
        def check(m: discord.Message) -> bool:
            return m.author.id == usuario.id

        try:
            channel = ctx.channel
            if isinstance(channel, TextChannel):
                eliminados = await channel.purge(limit=cantidad + 1, check=check)
                await ctx.send(
                    embed=self._embed("🧹 Limpieza por usuario", ctx, f"Se eliminaron {len(eliminados)-1} mensajes de {usuario.mention}."),
                    delete_after=5
                )
        except Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al eliminar mensajes: {e}")

    @commands.command(name="clearcontains")
    @commands.has_permissions(manage_messages=True)
    async def clearcontains(self, ctx: commands.Context, palabra: str, cantidad: int = 100) -> None:
        """Limpia mensajes que contengan una palabra específica.
        
        Args:
            ctx: Contexto del comando
            palabra: Palabra a buscar
            cantidad: Cantidad máxima de mensajes a revisar
        """
        def check(m: discord.Message) -> bool:
            return palabra.lower() in (m.content or "").lower()

        try:
            channel = ctx.channel
            if isinstance(channel, TextChannel):
                eliminados = await channel.purge(limit=cantidad + 1, check=check)
                await ctx.send(
                    embed=self._embed("🧹 Limpieza por palabra", ctx, f"Se eliminaron {len(eliminados)-1} mensajes que contenían '{palabra}'."),
                    delete_after=5
                )
        except Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al eliminar mensajes: {e}")

    @commands.command(name="clearbots")
    @commands.has_permissions(manage_messages=True)
    async def clearbots(self, ctx: commands.Context, cantidad: int = 100) -> None:
        """Limpia mensajes enviados por bots.
        
        Args:
            ctx: Contexto del comando
            cantidad: Cantidad máxima de mensajes a revisar
        """
        def check(m: discord.Message) -> bool:
            return m.author.bot
        
        try:
            channel = ctx.channel
            if isinstance(channel, TextChannel):
                eliminados = await channel.purge(limit=cantidad + 1, check=check)
                await ctx.send(
                    embed=self._embed("🤖 Limpieza de Bots", ctx, f"Se eliminaron {len(eliminados)-1} mensajes enviados por bots."),
                    delete_after=5
                )
        except Forbidden:
            await ctx.send("❌ No tengo permisos para eliminar mensajes.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al eliminar mensajes: {e}")


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de limpieza en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(Limpieza(bot))