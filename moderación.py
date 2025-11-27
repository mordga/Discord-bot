import discord
from discord.ext import commands
import asyncio
from datetime import timedelta
from typing import Optional


def _parse_time(s: str) -> Optional[int]:
    """Convierte una cadena de tiempo a segundos.
    
    Formatos soportados: 10s, 5m, 2h, 1d
    
    Args:
        s: Cadena de tiempo a parsear
        
    Returns:
        Segundos totales o None si es inválido
    """
    s = s.lower().strip()
    total = 0
    num = ''
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    if s.isdigit():
        return int(s)
    for ch in s:
        if ch.isdigit():
            num += ch
        elif ch in multipliers:
            if num == '':
                return None
            total += int(num) * multipliers[ch]
            num = ''
        elif ch in ' ,':
            continue
        else:
            return None
    return total if total > 0 else None

class Moderacion(commands.Cog):
    """Cog con comandos de moderación del servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de moderación.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    def _make_embed(self, action: str, miembro: discord.User | discord.Member, moderador: discord.Member, razon: Optional[str] = None, tiempo: Optional[str] = None) -> discord.Embed:
        """Crea un embed estándar para las acciones de moderación.
        
        Args:
            action: Nombre de la acción de moderación
            miembro: Miembro o usuario afectado
            moderador: Moderador que ejecuta la acción
            razon: Razón de la acción (opcional)
            tiempo: Tiempo asociado (opcional)
            
        Returns:
            Embed creado
        """
        e = discord.Embed(title=action, color=discord.Color.red(), timestamp=discord.utils.utcnow())
        e.add_field(name="Usuario", value=f"{miembro} (`{getattr(miembro, 'id', str(miembro))}`)", inline=False)
        e.add_field(name="Moderador", value=f"{moderador} (`{moderador.id}`)", inline=False)
        if razon:
            e.add_field(name="Razón", value=razon, inline=False)
        if tiempo:
            e.add_field(name="Tiempo", value=tiempo, inline=False)
        e.set_footer(text="Starry Bot • Moderación")
        return e

    async def _send_log(self, ctx: commands.Context, embed: discord.Embed) -> None:
        """Envía un log de moderación al canal de logs.
        
        Args:
            ctx: Contexto del comando
            embed: Embed a enviar
        """
        guild = ctx.guild
        if not guild:
            return
        candidatos = [c for c in guild.text_channels if any(n in c.name.lower() for n in ("mod-log", "modlogs", "logs", "mod"))]
        ch = candidatos[0] if candidatos else None
        if ch:
            try:
                await ch.send(embed=embed)
            except discord.HTTPException:
                pass

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, miembro: discord.Member, tiempo: Optional[str] = None, *, razon: str = "Sin razón") -> None:
        """Banea a un miembro del servidor.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a banear
            tiempo: Tiempo del ban (opcional)
            razon: Razón del ban
        """
        try:
            await miembro.ban(reason=razon)
            embed = self._make_embed("Ban", miembro, ctx.author, razon=razon, tiempo=tiempo)
            await ctx.send(embed=embed)
            await self._send_log(ctx, embed)

            try:
                await miembro.send(f"Has sido baneado de **{ctx.guild.name}**\nRazón: {razon}")
            except discord.HTTPException:
                pass

            if tiempo:
                seconds = _parse_time(tiempo)
                if seconds:
                    async def _unban_after() -> None:
                        await asyncio.sleep(seconds)
                        user = await self.bot.fetch_user(miembro.id)
                        try:
                            await ctx.guild.unban(user)
                        except discord.HTTPException:
                            pass
                    asyncio.create_task(_unban_after())
        except discord.HTTPException as e:
            await ctx.send(f"❌ Error ban: {e}")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int) -> None:
        """Desbanea a un usuario del servidor.
        
        Args:
            ctx: Contexto del comando
            user_id: ID del usuario a desbanear
        """
        user = await self.bot.fetch_user(user_id)
        try:
            await ctx.guild.unban(user)
            embed = self._make_embed("Unban", user, ctx.author)
            await ctx.send(embed=embed)
            await self._send_log(ctx, embed)
        except discord.HTTPException:
            await ctx.send("❌ Ese usuario no está baneado.")

    @commands.command(name="softban")
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx: commands.Context, miembro: discord.Member, *, razon: str = "Sin razón") -> None:
        """Soft-banea a un miembro (ban y desban inmediato).
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a soft-banear
            razon: Razón del soft-ban
        """
        try:
            await miembro.ban(reason=razon)
            await ctx.guild.unban(miembro)
            embed = self._make_embed("Softban", miembro, ctx.author, razon=razon)
            await ctx.send(embed=embed)
            await self._send_log(ctx, embed)
        except discord.HTTPException as e:
            await ctx.send(f"❌ Error: {e}")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, miembro: discord.Member, *, razon: str = "Sin razón") -> None:
        """Expulsa a un miembro del servidor.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a expulsar
            razon: Razón de la expulsión
        """
        try:
            await miembro.kick(reason=razon)
            embed = self._make_embed("Kick", miembro, ctx.author, razon=razon)
            await ctx.send(embed=embed)
            await self._send_log(ctx, embed)
        except discord.HTTPException:
            await ctx.send("❌ No pude expulsarlo.")

    @commands.command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, miembro: discord.Member, tiempo: str, *, razon: str = "Sin razón") -> None:
        """Aplica un timeout a un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a timeout
            tiempo: Duración del timeout
            razon: Razón del timeout
        """
        segundos = _parse_time(tiempo)
        if not segundos:
            return await ctx.send("❌ Tiempo inválido. Ejemplo: 10m, 1h")

        until = discord.utils.utcnow() + timedelta(seconds=segundos)
        await miembro.timeout(until, reason=razon)
        embed = self._make_embed("Timeout", miembro, ctx.author, razon=razon, tiempo=tiempo)
        await ctx.send(embed=embed)
        await self._send_log(ctx, embed)

    @commands.command(name="untimeout")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, miembro: discord.Member) -> None:
        """Remueve el timeout de un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a deshacer timeout
        """
        await miembro.timeout(None)
        embed = self._make_embed("UnTimeout", miembro, ctx.author)
        await ctx.send(embed=embed)
        await self._send_log(ctx, embed)

    @commands.command(name="voicemute")
    @commands.has_permissions(move_members=True)
    async def voicemute(self, ctx: commands.Context, miembro: discord.Member) -> None:
        """Mutea a un miembro en voz.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a mutear
        """
        try:
            await miembro.edit(mute=True)
            embed = self._make_embed("Voice Mute", miembro, ctx.author)
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("❌ No pude mutear en voz.")

    @commands.command(name="voiceunmute")
    @commands.has_permissions(move_members=True)
    async def voiceunmute(self, ctx: commands.Context, miembro: discord.Member) -> None:
        """Desmutea a un miembro en voz.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro a desmutear
        """
        try:
            await miembro.edit(mute=False)
            embed = self._make_embed("Voice Unmute", miembro, ctx.author)
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("❌ No pude desmutear en voz.")


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de moderación en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(Moderacion(bot))