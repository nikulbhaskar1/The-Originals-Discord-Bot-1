import discord
from discord.ext import commands
from utils.logger import setup_logger
from config import Config

logger = setup_logger()

class ModerationSlash(commands.Cog):
    """Slash command moderation features"""
    
    def __init__(self, bot):
        self.bot = bot
        self.muted_users = {}  # {user_id: {guild_id: role_id}}
    
    async def create_mute_role(self, guild):
        """Create or find mute role in guild"""
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
                        
                logger.info(f'Created mute role in {guild.name}')
            except discord.Forbidden:
                return None
                
        return mute_role
    
    @discord.app_commands.command(name='ban', description='Ban a user from the server')
    @discord.app_commands.describe(member='The member to ban', reason='Reason for the ban')
    async def ban_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Ban a user from the server"""
        # Check permissions
        author_member = interaction.guild.get_member(interaction.user.id)
        if not author_member.guild_permissions.ban_members and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to ban members.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Owner protection
        if member.id == Config.OWNER_ID:
            embed = discord.Embed(
                title="🛡️ Owner Protection",
                description="Cannot moderate the bot owner!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Check if target has higher role
        if member.top_role >= author_member.top_role and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot ban someone with a higher or equal role.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.ban(reason=reason)
            
            embed = discord.Embed(
                title="🔨 User Banned",
                description=f"**{member}** has been banned.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user} banned {member} in {interaction.guild.name}. Reason: {reason}')
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to ban this user.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name='kick', description='Kick a user from the server')
    @discord.app_commands.describe(member='The member to kick', reason='Reason for the kick')
    async def kick_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Kick a user from the server"""
        # Check permissions
        author_member = interaction.guild.get_member(interaction.user.id)
        if not author_member.guild_permissions.kick_members and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to kick members.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Owner protection
        if member.id == Config.OWNER_ID:
            embed = discord.Embed(
                title="🛡️ Owner Protection",
                description="Cannot moderate the bot owner!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Check if target has higher role
        if member.top_role >= author_member.top_role and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot kick someone with a higher or equal role.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.kick(reason=reason)
            
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"**{member}** has been kicked.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user} kicked {member} in {interaction.guild.name}. Reason: {reason}')
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to kick this user.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name='mute', description='Mute a user in the server')
    @discord.app_commands.describe(member='The member to mute', reason='Reason for the mute')
    async def mute_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """Mute a user in the server"""
        # Check permissions
        author_member = interaction.guild.get_member(interaction.user.id)
        if not author_member.guild_permissions.manage_roles and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to manage roles.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Owner protection
        if member.id == Config.OWNER_ID:
            embed = discord.Embed(
                title="🛡️ Owner Protection",
                description="Cannot moderate the bot owner!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Check if target has higher role
        if member.top_role >= author_member.top_role and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You cannot mute someone with a higher or equal role.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        mute_role = await self.create_mute_role(interaction.guild)
        if not mute_role:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to create or manage the mute role.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if mute_role in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description="This user is already muted.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.add_roles(mute_role, reason=reason)
            
            # Store mute info
            if member.id not in self.muted_users:
                self.muted_users[member.id] = {}
            self.muted_users[member.id][interaction.guild.id] = mute_role.id
            
            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"**{member}** has been muted.",
                color=discord.Color.dark_grey()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user} muted {member} in {interaction.guild.name}. Reason: {reason}')
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to mute this user.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name='unmute', description='Unmute a user in the server')
    @discord.app_commands.describe(member='The member to unmute')
    async def unmute_user(self, interaction: discord.Interaction, member: discord.Member):
        """Unmute a user in the server"""
        # Check permissions
        author_member = interaction.guild.get_member(interaction.user.id)
        if not author_member.guild_permissions.manage_roles and interaction.user.id != Config.OWNER_ID:
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to manage roles.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role or mute_role not in member.roles:
            embed = discord.Embed(
                title="❌ Error",
                description="This user is not muted.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        
        try:
            await member.remove_roles(mute_role, reason="Unmuted by moderator")
            
            # Remove from mute tracking
            if member.id in self.muted_users and interaction.guild.id in self.muted_users[member.id]:
                del self.muted_users[member.id][interaction.guild.id]
                if not self.muted_users[member.id]:
                    del self.muted_users[member.id]
            
            embed = discord.Embed(
                title="🔊 User Unmuted",
                description=f"**{member}** has been unmuted.",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'{interaction.user} unmuted {member} in {interaction.guild.name}')
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unmute this user.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationSlash(bot))
