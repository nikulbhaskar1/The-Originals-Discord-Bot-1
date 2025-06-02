from discord.ext import commands
import discord
from config import Config

def is_owner():
    """Check if user is the bot owner"""
    def predicate(ctx):
        return ctx.author.id == Config.OWNER_ID
    return commands.check(predicate)

def is_owner_or_has_permissions(**perms):
    """Check if user is owner or has the required permissions"""
    def predicate(ctx):
        if ctx.author.id == Config.OWNER_ID:
            return True
        
        # Check if user has required permissions
        user_perms = ctx.channel.permissions_for(ctx.author)
        return all(getattr(user_perms, perm, False) for perm in perms)
    
    return commands.check(predicate)

async def can_moderate(ctx, target_member):
    """Check if the author can moderate the target member"""
    # Owner can moderate anyone except themselves
    if ctx.author.id == Config.OWNER_ID:
        return target_member.id != Config.OWNER_ID
    
    # Can't moderate the owner
    if target_member.id == Config.OWNER_ID:
        return False
    
    # Can't moderate someone with higher or equal role
    if target_member.top_role >= ctx.author.top_role:
        return False
    
    return True
