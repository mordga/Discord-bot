import discord
from discord.ext import commands
from discord import PermissionOverwrite, HTTPException, Forbidden, TextChannel
from typing import Optional


class Canales(commands.Cog):
    """Comandos de gestión de canales (lock/unlock, slowmode, ocultar/mostrar, mute/unmute)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _embed(self, titulo: str, ctx: commands.Context, extra: Optional[str] = None) -> discord.Embed:
        """Crea un embed estándar para los comandos del cog."""
        author = ctx.author
        e = discord.Embed(title=titulo, color=discord.Color.blurple())
        channel = ctx.channel
        if isinstance(channel, TextChannel):
            e.add_field(name="Canal", value=f"{channel.mention}", inline=False)
        else:
            e.add_field(name="Canal", value=f"#{channel}", inline=False)
        if extra:
            e.add_field(name="Info", value=extra, inline=False)

        # tratar de obtener un avatar (compatibilidad con varias versiones)
        icon_url = None
        try:
            icon_url = getattr(author, "avatar", None)
            if icon_url:
                icon_url = icon_url.url
            else:
                icon_url = author.display_avatar.url
        except Exception:
            icon_url = None

        e.set_footer(text=f"Solicitado por {author}", icon_url=icon_url)
        return e

    async def _apply_overwrite(self, ctx: commands.Context, **perm_changes) -> Optional[str]:
        """
        Aplica cambios en PermissionOverwrite para el rol @everyone.
        Devuelve None si todo va bien, o un mensaje de error en caso contrario.
        """
        if ctx.guild is None:
            return "❌ Este comando solo puede usarse dentro de un servidor."

        channel = ctx.channel
        if not isinstance(channel, TextChannel):
            return "❌ Este comando solo funciona en canales de texto."

        try:
            everyone = ctx.guild.default_role
            overwrite: PermissionOverwrite = channel.overwrites_for(everyone) or PermissionOverwrite()
            for name, value in perm_changes.items():
                setattr(overwrite, name, value)
            await channel.set_permissions(everyone, overwrite=overwrite)
            return None
        except Forbidden:
            return "❌ No tengo permisos para modificar los permisos del canal."
        except HTTPException as e:
            return f"❌ Error al actualizar permisos: {e}"

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context):
        """Bloquea el canal para @everyone (sin enviar mensajes)."""
        err = await self._apply_overwrite(ctx, send_messages=False)
        if err:
            return await ctx.send(err)
        await ctx.send(embed=self._embed("🔒 Canal bloqueado", ctx))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context):
        """Desbloquea el canal para @everyone (restaura el permiso send_messages)."""
        err = await self._apply_overwrite(ctx, send_messages=None)
        if err: return await ctx.send(err)
        await ctx.send(embed=self._embed("🔓 Canal desbloqueado", ctx))

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: commands.Context, tiempo: str):
        """
        Activa/desactiva slowmode del canal.
        Uso: s?slowmode 5  -> 5 segundos
              s?slowmode off -> desactiva
        Valida rangos entre 0 y 21600 (6 horas), valor máximo impuesto por la API de Discord.
        """
        if ctx.guild is None:
            return await ctx.send("❌ Este comando solo puede usarse dentro de un servidor.")

        channel = ctx.channel
        if not isinstance(channel, TextChannel):
            return await ctx.send("❌ Este comando solo funciona en canales de texto.")

        if tiempo.lower() in {"off", "0"}:
            try:
                await channel.edit(slowmode_delay=0)
            except Forbidden:
                return await ctx.send("❌ No tengo permisos para editar el canal.")
            except HTTPException as e:
                return await ctx.send(f"❌ Error al editar el canal: {e}")
            return await ctx.send(embed=self._embed("⏳ Slowmode desactivado", ctx))

        if not tiempo.isdigit():
            return await ctx.send("❌ Usa un número o 'off'. Ej: s?slowmode 5")

        segundos = int(tiempo)
        if segundos < 0:
            return await ctx.send("❌ El tiempo debe ser mayor o igual a 0.")
        if segundos > 21600:
            return await ctx.send("❌ El slowmode máximo permitido es 21600 segundos (6 horas).")

        try:
            await channel.edit(slowmode_delay=segundos)
        except Forbidden:
            return await ctx.send("❌ No tengo permisos para editar el canal.")
        except HTTPException as e:
            return await ctx.send(f"❌ Error al editar el canal: {e}")

        await ctx.send(embed=self._embed("⏳ Slowmode activado", ctx, f"{segundos} segundos"))

    @commands.command(name="channelhide")
    @commands.has_permissions(manage_channels=True)
    async def channelhide(self, ctx: commands.Context):
        """Oculta el canal para @everyone (view_channel=False)."""
        err = await self._apply_overwrite(ctx, view_channel=False)
        if err:
            return await ctx.send(err)
        await ctx.send(embed=self._embed("🙈 Canal ocultado", ctx))

    @commands.command(name="channelshow")
    @commands.has_permissions(manage_channels=True)
    async def channelshow(self, ctx: commands.Context):
        """
        Muestra el canal para @everyone. Por defecto establece view_channel=True.
        Si prefieres restaurar el permiso a su valor por defecto usa view_channel=None manualmente.
        """
        err = await self._apply_overwrite(ctx, view_channel=True)
        if err:
            return await ctx.send(err)
        await ctx.send(embed=self._embed("👀 Canal visible", ctx))

    @commands.command(name="channelmute")
    @commands.has_permissions(manage_channels=True)
    async def channelmute(self, ctx: commands.Context):
        """Impide enviar mensajes en el canal para @everyone (send_messages=False)."""
        err = await self._apply_overwrite(ctx, send_messages=False)
        if err:
            return await ctx.send(err)
        await ctx.send(embed=self._embed("🔇 Canal muteado", ctx))

    @commands.command(name="channelunmute")
    @commands.has_permissions(manage_channels=True)
    async def channelunmute(self, ctx: commands.Context):
        """Restaura send_messages para @everyone (send_messages=None)."""
        err = await self._apply_overwrite(ctx, send_messages=None)
        if err:
            return await ctx.send(err)
        await ctx.send(embed=self._embed("🔊 Canal desmuteado", ctx))


async def setup(bot: commands.Bot):
    await bot.add_cog(Canales(bot))