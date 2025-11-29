import discord
from discord.ext import commands
from discord import Forbidden, HTTPException
from typing import Dict, List, Optional


# CANAL DE LOGS FIJO
LOG_CHANNEL_ID: int = 1438789570819919974


class Warns(commands.Cog):
    """Cog con sistema de advertencias para moderación."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de advertencias.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    # -----------------------
    # Embed profesional
    # -----------------------
    def _embed(
        self,
        titulo: str,
        miembro: discord.Member,
        moderador: discord.User | discord.Member,
        razon: Optional[str] = None
    ) -> discord.Embed:
        """Crea un embed estándar para acciones de advertencias.
        
        Args:
            titulo: Título del embed
            miembro: Miembro al que se le aplica la advertencia
            moderador: Moderador que aplica la acción
            razon: Razón de la advertencia (opcional)
            
        Returns:
            Embed creado
        """
        e = discord.Embed(title=titulo, color=discord.Color.orange())
        e.add_field(name="Usuario", value=f"{miembro.mention} (`{miembro.id}`)", inline=False)
        e.add_field(name="Moderador", value=f"{moderador.mention} (`{moderador.id}`)", inline=False)
        if razon:
            e.add_field(name="Razón", value=razon, inline=False)
        e.set_footer(text=f"Sistema de Warns • Solicitado por {moderador}")
        return e

    # -------------------------------------------
    # Obtener logs desde el canal usando el ID fijo
    # -------------------------------------------
    async def get_warns(self, guild: discord.Guild, user_id: int) -> List[Dict]:
        """Obtiene todas las advertencias de un usuario desde el canal de logs.
        
        Args:
            guild: Servidor donde buscar las advertencias
            user_id: ID del usuario a buscar
            
        Returns:
            Lista de advertencias encontradas
        """
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel or not isinstance(log_channel, discord.TextChannel):
            return []

        warns: List[Dict] = []
        try:
            async for msg in log_channel.history(limit=5000):
                if msg.author.bot and msg.content.startswith("WARN |"):
                    partes = msg.content.split(" | ")

                    data: Dict = {}
                    for p in partes:
                        if p.startswith("USER: "):
                            data["user"] = int(p.replace("USER: ", ""))
                        elif p.startswith("MOD: "):
                            data["mod"] = int(p.replace("MOD: ", ""))
                        elif p.startswith("ID: "):
                            data["id"] = int(p.replace("ID: ", ""))
                        elif p.startswith("RAZON: "):
                            data["razon"] = p.replace("RAZON: ", "")

                    if data.get("user") == user_id:
                        warns.append({"msg": msg, **data})
        except (Forbidden, HTTPException):
            return []

        return warns

    # -----------------------
    # Comando: aplicar warn
    # -----------------------
    @commands.command(name="warn")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: commands.Context, miembro: discord.Member, *, razon: str = "Sin razón") -> None:
        """Aplica una advertencia a un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro al que se le aplicará la advertencia
            razon: Razón de la advertencia
        """
        if not isinstance(ctx.guild, discord.Guild):
            await ctx.send("❌ Este comando solo funciona en servidores.")
            return

        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel or not isinstance(log_channel, discord.TextChannel):
            await ctx.send("❌ El canal de logs no existe o el bot no tiene acceso a él.")
            return

        warns = await self.get_warns(ctx.guild, miembro.id)
        new_id = len(warns) + 1

        embed = self._embed("⚠️ Advertencia aplicada", miembro, ctx.author, razon)
        await ctx.send(embed=embed)

        # Guardar en logs
        try:
            await log_channel.send(
                f"WARN | USER: {miembro.id} | MOD: {ctx.author.id} | ID: {new_id} | RAZON: {razon}"
            )
        except (Forbidden, HTTPException):
            await ctx.send("⚠️ No pude guardar la advertencia en el canal de logs.")
            return

        # Notificar por DM
        try:
            await miembro.send(
                f"⚠️ Has sido advertido en **{ctx.guild.name}**\nRazón: {razon}"
            )
        except (Forbidden, HTTPException):
            pass

    # -----------------------
    # Ver advertencias
    # -----------------------
    @commands.command(name="warnings")
    @commands.has_permissions(kick_members=True)
    async def warnings(self, ctx: commands.Context, miembro: discord.Member) -> None:
        """Muestra todas las advertencias de un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro cuyas advertencias se mostrarán
        """
        if not isinstance(ctx.guild, discord.Guild):
            await ctx.send("❌ Este comando solo funciona en servidores.")
            return

        warns = await self.get_warns(ctx.guild, miembro.id)

        if not warns:
            embed = discord.Embed(
                title="✅ Sin advertencias",
                description=f"{miembro.mention} no tiene advertencias.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"⚠️ Advertencias de {miembro}",
            description=f"Total: {len(warns)} advertencia(s)",
            color=discord.Color.orange()
        )

        for w in warns:
            mod = ctx.guild.get_member(w["mod"])
            mod_name = mod.mention if mod else f"Moderador desconocido (`{w['mod']}`)"
            embed.add_field(
                name=f"📌 ID {w['id']}",
                value=f"**Razón:** {w['razon']}\n**Moderador:** {mod_name}",
                inline=False
            )

        embed.set_footer(text=f"Solicitado por {ctx.author}")
        await ctx.send(embed=embed)

    # -----------------------
    # Remover advertencia por ID
    # -----------------------
    @commands.command(name="warnremove")
    @commands.has_permissions(kick_members=True)
    async def warnremove(self, ctx: commands.Context, miembro: discord.Member, warn_id: int) -> None:
        """Remueve una advertencia específica de un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro del cual remover la advertencia
            warn_id: ID de la advertencia a remover
        """
        if not isinstance(ctx.guild, discord.Guild):
            await ctx.send("❌ Este comando solo funciona en servidores.")
            return

        warns = await self.get_warns(ctx.guild, miembro.id)

        for w in warns:
            if w["id"] == warn_id:
                try:
                    await w["msg"].delete()
                except (Forbidden, HTTPException):
                    pass

                embed = self._embed(
                    "🗑️ Advertencia eliminada",
                    miembro,
                    ctx.author,
                    f"Advertencia ID {warn_id} removida."
                )
                await ctx.send(embed=embed)
                return

        embed = discord.Embed(
            title="❌ Advertencia no encontrada",
            description=f"No existe una advertencia con ID {warn_id} para {miembro.mention}.",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Solicitado por {ctx.author}")
        await ctx.send(embed=embed)

    # -----------------------
    # Limpiar TODAS las advertencias
    # -----------------------
    @commands.command(name="warnclear")
    @commands.has_permissions(kick_members=True)
    async def warnclear(self, ctx: commands.Context, miembro: discord.Member) -> None:
        """Elimina todas las advertencias de un miembro.
        
        Args:
            ctx: Contexto del comando
            miembro: Miembro cuyas advertencias serán eliminadas
        """
        if not isinstance(ctx.guild, discord.Guild):
            await ctx.send("❌ Este comando solo funciona en servidores.")
            return

        warns = await self.get_warns(ctx.guild, miembro.id)

        if not warns:
            embed = discord.Embed(
                title="ℹ️ Sin advertencias",
                description=f"{miembro.mention} no tiene advertencias para eliminar.",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
            return

        count = 0
        for w in warns:
            try:
                await w["msg"].delete()
                count += 1
            except (Forbidden, HTTPException):
                pass

        embed = self._embed(
            "🧹 Advertencias eliminadas",
            miembro,
            ctx.author,
            f"Se eliminaron {count} advertencia(s) de {miembro.mention}."
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de advertencias en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(Warns(bot))