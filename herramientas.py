import discord
from discord.ext import commands

class Herramientas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, mensaje):
        await ctx.message.delete()
        await ctx.send(mensaje)

    @commands.command()
    async def sayembed(self, ctx, *, mensaje):
        await ctx.message.delete()
        embed = discord.Embed(description=mensaje, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, canal: discord.TextChannel, *, mensaje):
        embed = discord.Embed(
            title="📢 Anuncio",
            description=mensaje,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Enviado por {ctx.author}")
        await canal.send(embed=embed)
        await ctx.send("✅ Anuncio enviado.")


async def setup(bot):
    await bot.add_cog(Herramientas(bot))