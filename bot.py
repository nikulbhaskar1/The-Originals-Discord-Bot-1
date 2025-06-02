import discord
from discord.ext import commands
import asyncio
import logging
import os
from config import Config
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Re-enabled with permissions
intents.guilds = True
intents.members = False  # Disabled privileged intent

bot = commands.Bot(
    command_prefix='!',  # Keep prefix for compatibility
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# Global variables for tracking
muted_users = {}  # {user_id: {guild_id: role_id}}

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Set bot status
    activity = discord.Activity(type=discord.ActivityType.watching, name="for moderation")
    await bot.change_presence(activity=activity)
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} slash commands')
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You don't have the required permissions to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Missing required argument: `{error.param}`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        logger.error(f'Unexpected error: {error}')
        embed = discord.Embed(
            title="❌ Error",
            description="An unexpected error occurred. Please try again later.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.tree.command(name='help', description='Display help information')
async def help_command(interaction: discord.Interaction):
    """Display help information"""
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Multi-purpose Discord bot with global moderation capabilities",
        color=discord.Color.blue()
    )
    
    # Basic moderation commands
    embed.add_field(
        name="🔨 Basic Moderation",
        value="`/ban <user> [reason]` - Ban a user\n"
              "`/kick <user> [reason]` - Kick a user\n"
              "`/mute <user> [reason]` - Mute a user\n"
              "`/unmute <user>` - Unmute a user",
        inline=False
    )
    
    # Owner-only commands
    if interaction.user.id == Config.OWNER_ID:
        embed.add_field(
            name="👑 Owner Commands",
            value="`/globalban <user_id> [reason]` - Ban user from all servers\n"
                  "`/globalkick <user_id> [reason]` - Kick user from all servers\n"
                  "`/globalmute <user_id> [reason]` - Mute user in all servers\n"
                  "`/globalunmute <user_id>` - Unmute user from all servers\n"
                  "`/servers` - List all servers bot is in\n"
                  "`/leaveserver <server_id>` - Leave a specific server\n"
                  "`/shutdown` - Shutdown the bot",
            inline=False
        )
    
    embed.add_field(
        name="ℹ️ Information",
        value=f"Commands: Slash commands only\n"
              f"Owner: <@{Config.OWNER_ID}>",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

async def load_cogs():
    """Load all cogs"""
    cogs = ['cogs.moderation_slash', 'cogs.owner_slash']
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f'Loaded cog: {cog}')
        except Exception as e:
            logger.error(f'Failed to load cog {cog}: {e}')

async def main():
    """Main function to run the bot"""
    async with bot:
        await load_cogs()
        await bot.start(Config.TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Bot shutdown initiated by user')
    except Exception as e:
        logger.error(f'Bot crashed: {e}')
