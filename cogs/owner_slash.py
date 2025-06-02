import discord
from discord.ext import commands
import asyncio
from utils.logger import setup_logger
from config import Config

logger = setup_logger()

class OwnerSlash(commands.Cog):
    """Owner-only slash commands with global moderation capabilities"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @discord.app_commands.command(name='globalban', description='Ban a user from all servers the bot is in')
    @discord.app_commands.describe(user_id='The user ID to globally ban', reason='Reason for the ban')
    async def global_ban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Ban a user from all servers the bot is in"""
        # Owner check
        if interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Please provide a valid user ID.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Owner protection
        if user_id_int == Config.OWNER_ID:
            embed = discord.Embed(
                title="🛡️ Owner Protection",
                description="Cannot ban the bot owner!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user = await self.bot.fetch_user(user_id_int)
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Error",
                description="User not found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer()
        
        banned_guilds = []
        failed_guilds = []
        
        for guild in self.bot.guilds:
            try:
                member = guild.get_member(user_id_int)
                if member:
                    await member.ban(reason=f"Global ban by owner: {reason}")
                    banned_guilds.append(guild.name)
                    logger.info(f'Global ban: {user} banned from {guild.name}')
            except discord.Forbidden:
                failed_guilds.append(guild.name)
            except Exception as e:
                logger.error(f'Error banning {user} from {guild.name}: {e}')
                failed_guilds.append(guild.name)
        
        embed = discord.Embed(
            title="🌍 Global Ban Executed",
            description=f"**{user}** has been globally banned.",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned from", value=f"{len(banned_guilds)} servers", inline=True)
        embed.add_field(name="Failed", value=f"{len(failed_guilds)} servers", inline=True)
        
        if banned_guilds:
            embed.add_field(
                name="Success",
                value="\n".join(banned_guilds[:10]) + ("..." if len(banned_guilds) > 10 else ""),
                inline=False
            )
        
        if failed_guilds:
            embed.add_field(
                name="Failed Servers",
                value="\n".join(failed_guilds[:10]) + ("..." if len(failed_guilds) > 10 else ""),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        logger.info(f'{interaction.user} executed global ban on {user}. Reason: {reason}')
    
    @discord.app_commands.command(name='globalkick', description='Kick a user from all servers the bot is in')
    @discord.app_commands.describe(user_id='The user ID to globally kick', reason='Reason for the kick')
    async def global_kick(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Kick a user from all servers the bot is in"""
        # Owner check
        if interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Please provide a valid user ID.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Owner protection
        if user_id_int == Config.OWNER_ID:
            embed = discord.Embed(
                title="🛡️ Owner Protection",
                description="Cannot kick the bot owner!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user = await self.bot.fetch_user(user_id_int)
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Error",
                description="User not found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer()
        
        kicked_guilds = []
        failed_guilds = []
        
        for guild in self.bot.guilds:
            try:
                member = guild.get_member(user_id_int)
                if member:
                    await member.kick(reason=f"Global kick by owner: {reason}")
                    kicked_guilds.append(guild.name)
                    logger.info(f'Global kick: {user} kicked from {guild.name}')
            except discord.Forbidden:
                failed_guilds.append(guild.name)
            except Exception as e:
                logger.error(f'Error kicking {user} from {guild.name}: {e}')
                failed_guilds.append(guild.name)
        
        embed = discord.Embed(
            title="🌍 Global Kick Executed",
            description=f"**{user}** has been globally kicked.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Kicked from", value=f"{len(kicked_guilds)} servers", inline=True)
        embed.add_field(name="Failed", value=f"{len(failed_guilds)} servers", inline=True)
        
        if kicked_guilds:
            embed.add_field(
                name="Success",
                value="\n".join(kicked_guilds[:10]) + ("..." if len(kicked_guilds) > 10 else ""),
                inline=False
            )
        
        if failed_guilds:
            embed.add_field(
                name="Failed Servers",
                value="\n".join(failed_guilds[:10]) + ("..." if len(failed_guilds) > 10 else ""),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        logger.info(f'{interaction.user} executed global kick on {user}. Reason: {reason}')
    
    @discord.app_commands.command(name='globalmute', description='Mute a user in all servers the bot is in')
    @discord.app_commands.describe(user_id='The user ID to globally mute', reason='Reason for the mute')
    async def global_mute(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Mute a user in all servers the bot is in"""
        # Owner check
        if interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Please provide a valid user ID.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Owner protection
        if user_id_int == Config.OWNER_ID:
            embed = discord.Embed(
                title="🛡️ Owner Protection",
                description="Cannot mute the bot owner!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user = await self.bot.fetch_user(user_id_int)
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Error",
                description="User not found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer()
        
        muted_guilds = []
        failed_guilds = []
        
        for guild in self.bot.guilds:
            try:
                member = guild.get_member(user_id_int)
                if member:
                    # Get or create mute role
                    mute_role = discord.utils.get(guild.roles, name="Muted")
                    if not mute_role:
                        try:
                            mute_role = await guild.create_role(
                                name="Muted",
                                color=discord.Color.dark_grey(),
                                reason="Mute role for moderation"
                            )
                            
                            # Set permissions for mute role
                            for channel in guild.channels:
                                try:
                                    if isinstance(channel, discord.TextChannel):
                                        await channel.set_permissions(
                                            mute_role,
                                            send_messages=False,
                                            add_reactions=False,
                                            speak=False
                                        )
                                    elif isinstance(channel, discord.VoiceChannel):
                                        await channel.set_permissions(
                                            mute_role,
                                            speak=False,
                                            connect=False
                                        )
                                except discord.Forbidden:
                                    continue
                        except discord.Forbidden:
                            failed_guilds.append(guild.name)
                            continue
                    
                    if mute_role not in member.roles:
                        await member.add_roles(mute_role, reason=f"Global mute by owner: {reason}")
                        muted_guilds.append(guild.name)
                        logger.info(f'Global mute: {user} muted in {guild.name}')
            except discord.Forbidden:
                failed_guilds.append(guild.name)
            except Exception as e:
                logger.error(f'Error muting {user} in {guild.name}: {e}')
                failed_guilds.append(guild.name)
        
        embed = discord.Embed(
            title="🌍 Global Mute Executed",
            description=f"**{user}** has been globally muted.",
            color=discord.Color.dark_grey()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Muted in", value=f"{len(muted_guilds)} servers", inline=True)
        embed.add_field(name="Failed", value=f"{len(failed_guilds)} servers", inline=True)
        
        if muted_guilds:
            embed.add_field(
                name="Success",
                value="\n".join(muted_guilds[:10]) + ("..." if len(muted_guilds) > 10 else ""),
                inline=False
            )
        
        if failed_guilds:
            embed.add_field(
                name="Failed Servers",
                value="\n".join(failed_guilds[:10]) + ("..." if len(failed_guilds) > 10 else ""),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        logger.info(f'{interaction.user} executed global mute on {user}. Reason: {reason}')
    
    @discord.app_commands.command(name='globalunmute', description='Unmute a user from all servers the bot is in')
    @discord.app_commands.describe(user_id='The user ID to globally unmute')
    async def global_unmute(self, interaction: discord.Interaction, user_id: str):
        """Unmute a user from all servers the bot is in"""
        # Owner check
        if interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user_id_int = int(user_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Please provide a valid user ID.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            user = await self.bot.fetch_user(user_id_int)
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Error",
                description="User not found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        await interaction.response.defer()
        
        unmuted_guilds = []
        failed_guilds = []
        
        for guild in self.bot.guilds:
            try:
                member = guild.get_member(user_id_int)
                if member:
                    mute_role = discord.utils.get(guild.roles, name="Muted")
                    if mute_role and mute_role in member.roles:
                        await member.remove_roles(mute_role, reason="Global unmute by owner")
                        unmuted_guilds.append(guild.name)
                        logger.info(f'Global unmute: {user} unmuted in {guild.name}')
            except discord.Forbidden:
                failed_guilds.append(guild.name)
            except Exception as e:
                logger.error(f'Error unmuting {user} in {guild.name}: {e}')
                failed_guilds.append(guild.name)
        
        embed = discord.Embed(
            title="🌍 Global Unmute Executed",
            description=f"**{user}** has been globally unmuted.",
            color=discord.Color.green()
        )
        embed.add_field(name="Unmuted in", value=f"{len(unmuted_guilds)} servers", inline=True)
        embed.add_field(name="Failed", value=f"{len(failed_guilds)} servers", inline=True)
        
        if unmuted_guilds:
            embed.add_field(
                name="Success",
                value="\n".join(unmuted_guilds[:10]) + ("..." if len(unmuted_guilds) > 10 else ""),
                inline=False
            )
        
        if failed_guilds:
            embed.add_field(
                name="Failed Servers",
                value="\n".join(failed_guilds[:10]) + ("..." if len(failed_guilds) > 10 else ""),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        logger.info(f'{interaction.user} executed global unmute on {user}')
    
    @discord.app_commands.command(name='servers', description='List all servers the bot is in')
    async def list_servers(self, interaction: discord.Interaction):
        """List all servers the bot is in"""
        # Owner check
        if interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if not self.bot.guilds:
            embed = discord.Embed(
                title="📊 Server List",
                description="Bot is not in any servers.",
                color=discord.Color.blue()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        servers_info = []
        for guild in self.bot.guilds:
            servers_info.append(f"**{guild.name}** (ID: {guild.id}) - {guild.member_count} members")
        
        # Split into chunks if too many servers
        chunk_size = 20
        server_chunks = [servers_info[i:i + chunk_size] for i in range(0, len(servers_info), chunk_size)]
        
        embed = discord.Embed(
            title="📊 Server List",
            description=f"Bot is in **{len(self.bot.guilds)}** servers total\n\n" + "\n".join(server_chunks[0]),
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Send additional chunks if needed
        for i, chunk in enumerate(server_chunks[1:], 1):
            embed = discord.Embed(
                title=f"📊 Server List (Page {i+1})",
                description="\n".join(chunk),
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name='leaveserver', description='Leave a specific server')
    @discord.app_commands.describe(server_id='The server ID to leave')
    async def leave_server(self, interaction: discord.Interaction, server_id: str):
        """Leave a specific server"""
        # Owner check
        if interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="🔒 Access Denied",
                description="Only the bot owner can use this command.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            server_id_int = int(server_id)
        except ValueError:
            embed = discord.Embed(
                title="❌ Error",
                description="Please provide a valid server ID.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        guild = self.bot.get_guild(server_id_int)
        if not guild:
            embed = discord.Embed(
                title="❌ Error",
                description="Bot is not in that server or server not found.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        guild_name = guild.name
        
        try:
            await guild.leave()
            embed = discord.Embed(
                title="🚪 Left Server",
                description=f"Success
