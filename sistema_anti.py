import discord
from discord.ext import commands
from discord import Forbidden, HTTPException
from typing import Dict


class SistemaAnti(commands.Cog):
    """Cog con sistemas anti-abuso para moderación automática del servidor."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de sistemas anti-abuso.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

        self.antilink_enabled: bool = False
        self.whitelist_domains: list[str] = []
        self.antispam_enabled: bool = False
        self.anticaps_enabled: bool = False
        self.filtered_words: list[str] = []

        self.spam_cache: Dict[int, int] = {}

    # -----------------------
    # ANTI LINK
    # -----------------------
    @commands.command(name="antilink")
    @commands.has_permissions(manage_messages=True)
    async def antilink(self, ctx: commands.Context, mode: str) -> None:
        """Activa o desactiva el sistema anti-links.
        
        Args:
            ctx: Contexto del comando
            mode: 'on' para activar, 'off' para desactivar
        """
        mode = mode.lower()
        if mode == "on":
            self.antilink_enabled = True
            embed = discord.Embed(
                title="🔗 Anti-link activado",
                description="Los links serán eliminados automáticamente.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        elif mode == "off":
            self.antilink_enabled = False
            embed = discord.Embed(
                title="🔗 Anti-link desactivado",
                description="Los links serán permitidos.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Usa: `s?antilink on/off`")

    @commands.command(name="whitelist")
    @commands.has_permissions(manage_messages=True)
    async def whitelist(self, ctx: commands.Context, action: str, dominio: str) -> None:
        """Agrega o remueve dominios de la whitelist de links.
        
        Args:
            ctx: Contexto del comando
            action: 'add' para agregar, 'remove' para remover
            dominio: Dominio a agregar/remover (ej: discord.com)
        """
        action = action.lower()
        
        if action == "add":
            if dominio in self.whitelist_domains:
                await ctx.send(f"⚠️ El dominio `{dominio}` ya está en la whitelist.")
                return
            
            self.whitelist_domains.append(dominio)
            embed = discord.Embed(
                title="🟢 Dominio agregado",
                description=f"Dominio `{dominio}` añadido a whitelist.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
            
        elif action == "remove":
            if dominio not in self.whitelist_domains:
                await ctx.send(f"⚠️ El dominio `{dominio}` no está en la whitelist.")
                return
            
            self.whitelist_domains.remove(dominio)
            embed = discord.Embed(
                title="🔴 Dominio removido",
                description=f"Dominio `{dominio}` eliminado de whitelist.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Usa: `s?whitelist add/remove dominio`")

    # -----------------------
    # ANTI SPAM
    # -----------------------
    @commands.command(name="antispam")
    @commands.has_permissions(manage_messages=True)
    async def antispam(self, ctx: commands.Context, mode: str) -> None:
        """Activa o desactiva el sistema anti-spam.
        
        Args:
            ctx: Contexto del comando
            mode: 'on' para activar, 'off' para desactivar
        """
        mode = mode.lower()
        if mode == "on":
            self.antispam_enabled = True
            embed = discord.Embed(
                title="💬 Anti-spam activado",
                description="Se eliminarán los mensajes repetitivos.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        elif mode == "off":
            self.antispam_enabled = False
            embed = discord.Embed(
                title="💬 Anti-spam desactivado",
                description="Se permitirán mensajes repetitivos.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Usa: `s?antispam on/off`")

    # -----------------------
    # ANTI CAPS
    # -----------------------
    @commands.command(name="anticaps")
    @commands.has_permissions(manage_messages=True)
    async def anticaps(self, ctx: commands.Context, mode: str) -> None:
        """Activa o desactiva el sistema anti-mayúsculas.
        
        Args:
            ctx: Contexto del comando
            mode: 'on' para activar, 'off' para desactivar
        """
        mode = mode.lower()
        if mode == "on":
            self.anticaps_enabled = True
            embed = discord.Embed(
                title="🔠 Anti-caps activado",
                description="Se eliminarán mensajes en mayúsculas.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        elif mode == "off":
            self.anticaps_enabled = False
            embed = discord.Embed(
                title="🔠 Anti-caps desactivado",
                description="Se permitirán mensajes en mayúsculas.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Usa: `s?anticaps on/off`")

    # -----------------------
    # FILTRO DE PALABRAS
    # -----------------------
    @commands.command(name="filter")
    @commands.has_permissions(manage_messages=True)
    async def filter(self, ctx: commands.Context, action: str, palabra: str | None = None) -> None:
        """Gestiona el filtro de palabras prohibidas.
        
        Args:
            ctx: Contexto del comando
            action: 'add', 'remove', o 'list'
            palabra: Palabra a filtrar (no requerido para 'list')
        """
        action = action.lower()
        
        if action == "list":
            if not self.filtered_words:
                await ctx.send("📃 No hay palabras filtradas.")
                return
            
            lista = ", ".join(self.filtered_words)
            embed = discord.Embed(
                title="📃 Palabras filtradas",
                description=lista,
                color=discord.Color.blue()
            )
            embed.add_field(name="Total", value=str(len(self.filtered_words)), inline=False)
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)

        if not palabra:
            await ctx.send("❌ Usa: `s?filter add/remove palabra`")
            return

        if action == "add":
            if palabra in self.filtered_words:
                await ctx.send(f"⚠️ La palabra **{palabra}** ya está filtrada.")
                return
            
            self.filtered_words.append(palabra)
            embed = discord.Embed(
                title="🔴 Palabra agregada",
                description=f"Palabra **{palabra}** añadida al filtro.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
            
        elif action == "remove":
            if palabra not in self.filtered_words:
                await ctx.send(f"⚠️ La palabra **{palabra}** no está en el filtro.")
                return
            
            self.filtered_words.remove(palabra)
            embed = discord.Embed(
                title="🟢 Palabra removida",
                description=f"Palabra **{palabra}** eliminada del filtro.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Usa: `s?filter add/remove/list palabra`")

    # -----------------------
    # EVENTO: FILTRADO
    # -----------------------
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        """Listener para detectar y filtrar mensajes según los sistemas anti-abuso.
        
        Args:
            msg: Mensaje enviado
        """
        if msg.author.bot:
            return

        contenido = msg.content.lower()

        # Anti-link
        if self.antilink_enabled:
            if "http://" in contenido or "https://" in contenido or "www." in contenido:
                if not any(site in contenido for site in self.whitelist_domains):
                    try:
                        await msg.delete()
                    except (Forbidden, HTTPException):
                        pass
                    try:
                        await msg.channel.send(
                            f"❌ {msg.author.mention} No puedes enviar links aquí.",
                            delete_after=5
                        )
                    except (Forbidden, HTTPException):
                        pass
                    return

        # Anti-caps
        if self.anticaps_enabled and len(msg.content) > 5:
            if msg.content.upper() == msg.content:
                try:
                    await msg.delete()
                except (Forbidden, HTTPException):
                    pass
                try:
                    await msg.channel.send(
                        f"❌ {msg.author.mention} No escribas todo en mayúsculas.",
                        delete_after=5
                    )
                except (Forbidden, HTTPException):
                    pass
                return

        # Filtro de palabras
        for bad in self.filtered_words:
            if bad in contenido:
                try:
                    await msg.delete()
                except (Forbidden, HTTPException):
                    pass
                try:
                    await msg.channel.send(
                        f"❌ {msg.author.mention} Esa palabra está prohibida.",
                        delete_after=5
                    )
                except (Forbidden, HTTPException):
                    pass
                return

        # Anti-spam
        if self.antispam_enabled:
            uid = msg.author.id
            self.spam_cache.setdefault(uid, 0)
            self.spam_cache[uid] += 1

            if self.spam_cache[uid] >= 5:
                try:
                    await msg.delete()
                except (Forbidden, HTTPException):
                    pass
                self.spam_cache[uid] = 0
                try:
                    await msg.channel.send(
                        f"❌ {msg.author.mention} No hagas spam.",
                        delete_after=5
                    )
                except (Forbidden, HTTPException):
                    pass
                return

        await self.bot.process_commands(msg)


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de sistemas anti-abuso en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(SistemaAnti(bot))