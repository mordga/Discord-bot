import discord
from discord.ext import commands
from discord import Forbidden, HTTPException


class Roles(commands.Cog):
    """Cog con comandos para gestionar roles de miembros."""

    def __init__(self, bot: commands.Bot) -> None:
        """Inicializa el Cog de roles.
        
        Args:
            bot: Instancia del bot de Discord
        """
        self.bot = bot

    def _make_embed(self, titulo: str, descripcion: str, color: discord.Color = discord.Color.blue()) -> discord.Embed:
        """Crea un embed estándar para los comandos de roles.
        
        Args:
            titulo: Título del embed
            descripcion: Descripción del embed
            color: Color del embed
            
        Returns:
            Embed creado
        """
        embed = discord.Embed(title=titulo, description=descripcion, color=color)
        return embed

    @commands.command(name="rol")
    @commands.has_permissions(manage_roles=True)
    async def rol(self, ctx: commands.Context, member: discord.Member, *, rol: discord.Role) -> None:
        """Agrega un rol a un miembro.
        
        Args:
            ctx: Contexto del comando
            member: Miembro al que se le agregará el rol
            rol: Rol a agregar
        """
        try:
            await member.add_roles(rol)
            embed = self._make_embed(
                "🟨 Rol agregado",
                f"Rol **{rol.name}** agregado a **{member.mention}**.",
                discord.Color.green()
            )
            embed.add_field(name="Miembro", value=member.mention, inline=False)
            embed.add_field(name="Rol", value=rol.mention, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        except Forbidden:
            await ctx.send("❌ No tengo permisos para agregar roles.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al agregar el rol: {e}")

    @commands.command(name="removerrol")
    @commands.has_permissions(manage_roles=True)
    async def removerrol(self, ctx: commands.Context, member: discord.Member, *, rol: discord.Role) -> None:
        """Remueve un rol de un miembro.
        
        Args:
            ctx: Contexto del comando
            member: Miembro al que se le removerá el rol
            rol: Rol a remover
        """
        try:
            await member.remove_roles(rol)
            embed = self._make_embed(
                "🟥 Rol removido",
                f"Rol **{rol.name}** removido de **{member.mention}**.",
                discord.Color.red()
            )
            embed.add_field(name="Miembro", value=member.mention, inline=False)
            embed.add_field(name="Rol", value=rol.mention, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=False)
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
        except Forbidden:
            await ctx.send("❌ No tengo permisos para remover roles.")
        except HTTPException as e:
            await ctx.send(f"❌ Error al remover el rol: {e}")

    @commands.command(name="rolesmiembro")
    async def rolesmiembro(self, ctx: commands.Context, member: discord.Member) -> None:
        """Muestra todos los roles de un miembro.
        
        Args:
            ctx: Contexto del comando
            member: Miembro del cual listar los roles
        """
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        
        if not roles:
            await ctx.send(f"❌ {member.mention} no tiene roles asignados.")
            return
        
        embed = self._make_embed(
            f"👤 Roles de {member.name}",
            "\n".join(roles),
            discord.Color.blue()
        )
        embed.add_field(name="Total de roles", value=str(len(roles)), inline=False)
        embed.set_footer(text=f"Solicitado por {ctx.author}")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Carga el Cog de roles en el bot.
    
    Args:
        bot: Instancia del bot de Discord
    """
    await bot.add_cog(Roles(bot))