import os
import discord
from discord.ext import commands
from main import Canales

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="s?", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comandos de árbol sincronizados")
    except Exception as e:
        print(f"❌ Error sincronizando comandos: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Uso incorrecto. Usa `s?help {ctx.command.name}`")
    else:
        await ctx.send(f"❌ Error: {error}")
        print(f"Error: {error}")

async def main():
    async with bot:
        await bot.add_cog(Canales(bot))
        token = os.getenv("DISCORD_BOT_TOKEN")
        if not token:
            print("❌ Error: No se encontró DISCORD_BOT_TOKEN en las variables de entorno")
            return
        await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
