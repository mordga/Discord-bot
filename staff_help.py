import discord
from discord.ext import commands


class StaffHelp(commands.Cog):
    """Cog con comandos de ayuda para el personal del servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de ayuda de staff.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    @commands.command(name="staffhelp")
    async def staffhelp(self, ctx: commands.Context) -> None:
        """Muestra la ayuda de comandos disponibles para el staff del servidor.
        
        Solo los miembros con permisos de kick pueden ver esta información.
        
        Args:
            ctx: Contexto del comando
        """
        if not isinstance(ctx.author, discord.Member) or not ctx.author.guild_permissions.kick_members:
            embed = discord.Embed(
                title="❌ Acceso denegado",
                description="Solo el personal del servidor puede usar este comando.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="📘 Ayuda de Staff",
            description="Comandos de administración disponibles para el personal.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔨 Moderación",
            value="`ban` - Banear usuario\n`unban` - Desbanear usuario\n`kick` - Expulsar usuario\n`timeout` - Silenciar usuario\n`untimeout` - Quitar silencio\n`softban` - Ban temporal\n`voicemute` - Silenciar en voz\n`voiceunmute` - Dessilenciar en voz",
            inline=False
        )
        
        embed.add_field(
            name="🧹 Limpieza",
            value="`clear` - Limpiar mensajes\n`clearuser` - Limpiar mensajes de usuario\n`clearcontains` - Limpiar por contenido\n`clearbots` - Limpiar mensajes de bots",
            inline=False
        )
        
        embed.add_field(
            name="👥 Roles",
            value="`rol` - Agregar rol\n`removerrol` - Remover rol\n`rolesmiembro` - Ver roles de miembro",
            inline=False
        )
        
        embed.add_field(
            name="✏️ Nicknames",
            value="`nick` - Cambiar nickname\n`nickreset` - Restaurar nickname",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ Sistemas Anti",
            value="`antilink` - Anti-links\n`whitelist` - Whitelist de dominios\n`antispam` - Anti-spam\n`anticaps` - Anti-mayúsculas\n`filter` - Filtro de palabras",
            inline=False
        )
        
        embed.add_field(
            name="📞 Utilidades",
            value="`say` - Enviar mensaje\n`sayembed` - Enviar embed\n`announce` - Anuncio importante",
            inline=False
        )
        
        embed.set_footer(text=f"Solicitado por {ctx.author} • Usa s?help para más información")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de ayuda de staff en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(StaffHelp(bot))