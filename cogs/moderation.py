import discord
import os
from discord.ext import commands
import psycopg
import time
from typing import Union

DB_URI = os.getenv("DB_URI")


class Moderation(commands.Cog): 
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help="""Changes current server's prefix
                      Permissions Required: `Manage Server`
                      
                      Ex:
                      {0}setprefix `!`""",
                      description="Changes Current server's Prefix")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx: commands.Context, *, new_prefix: str):
        async with await psycopg.AsyncConnection.connect(DB_URI) as db:
            async with db.cursor() as cursor:
                await cursor.execute("UPDATE GUILD set GUILD_PREFIX = %s WHERE GUILD_ID = %s", (new_prefix, ctx.guild.id))
                await db.commit()
                await ctx.send("Prefix updated to `{0}`".format(new_prefix))
                
                
    @commands.command(help="""Clears the chat.
                      Permissions Required: `Manage Messages`
                      
                      Ex:
                      {0}clear
                      {0}clear all
                      {0}clear 100""",
                      description="Clears the chat")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, input = None):
        def is_me(m):
            m = True
            return m
        if input == None:
            input = 10
        elif not input.isdigit():
            if input.lower() == "all":
                input = 250
        else:
            input = int(input)
        deleted = await ctx.channel.purge(limit=input, check=is_me)
        message = await ctx.send(f'Deleted {len(deleted)} message(s) `This message will disappear after 3 seconds.`')
        time.sleep(3)
        await message.delete()
        
    @commands.command(help="""kicks a user.
                      Permissions Required: `Kick Members`
                      It can kick Many Members
                      The preferred way is using Mention
                      
                      Ex:
                      {0}kick `user id`
                      {0}kick `user mention`""", description="Kicks a member or Many Members")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, members: commands.Greedy[discord.Member], *, reason:str = None):
        for member in members:
            await member.kick(reason=reason)
        if reason != None:
            await ctx.reply("**{0} has been kicked successfully For reason: {1}**".format(", ".join(member.name for member in members),reason))
        else:
            await ctx.reply("**{0} has been kicked successfully**".format(", ".join(member.name for member in members)))

        
    @commands.command(help="""bans a user.
                      Permissions Required: `Ban Members`
                      
                      Ex:
                      {0}ban `user id` -> bans a member whether they're in the server or not.
                      {0}ban `user mention`""", description="Bans a member")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: Union[discord.Member, int, str], *,reason: str = None):
        if type(member) == int:
            member = await self.bot.fetch_user(member)
        elif type(member) == str:
            member = ctx.guild.get_member_named(member)
            if member == None:
                return await ctx.send("Please Enter a valid Member Name")
        try:
            if await ctx.guild.fetch_ban(member):
                return await ctx.send("{0} is already banned".format(member.name))
        except:
            try:
                if reason == None:
                    reason = "No Reason provided"
                await ctx.guild.ban(member, delete_message_days=7, reason="banned by {0}\n for reason: {1}".format(ctx.author, reason))  
                if reason == "No Reason provided":       
                    await ctx.reply("**{0} has been banned successfully**".format(member.name))
                else:
                    await ctx.reply("**{0} has been banned successfully for reason: {1}**".format(member.name, reason))
            except Exception as e:
                if member != None:
                    await ctx.send("Couldn't ban {0}".format(member))
                else:
                    await ctx.send("Enter a valid member name/ID or mention")
                
            
    
    @commands.command(help="""unbans a user.
                      Permissions Required: `Ban Members`
                      
                      Ex:
                      {0}unban `user id`""", description="Unbans a member or Many Members")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, member_id:int ,*,reason: str = None):
        member = await self.bot.fetch_user(member_id)
        try:
            if await ctx.guild.fetch_ban(member):
                try:
                    await ctx.guild.unban(member, reason="By: {0}\nReason: {1}".format(ctx.author.name, reason))
                    return await ctx.send("{0} Has been unbanned successfully".format(member.name))
                except Exception as e:
                    return await ctx.send("**Error**\nCouldn't Unabn {0}".format(str(member)))
        except:
            await ctx.send("{0} isn't even banned.".format(member.name))
            
    @commands.command(help="""Gives/Removes a role from a user.
                      Permissions Required: `Manage Roles`
                      
                      Ex:
                      {0}role all @role -> Gives/Remove everyone in the server specific role
                      {0}role bots @role -> Gives/Remove all bots in the server specific role
                      {0}role members @role -> Gives/Remove all members in the server specific role
                      {0}role `user id` @role -> Gives/Remove a user in the server specific role
                      {0}role `@user` @role -> Gives/Remove a user in the server specific role
                      {0}role `user name` @role -> Gives/Remove a user in the server specific role""", description="Gives/Removes a role from a user.")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx: commands.Context, member: Union[discord.Member, int, str], role: discord.Role):
        if type(member) == int:
            member = await self.bot.fetch_user(id)
        elif type(member) == str:
            condition = True
            if member.lower() == "bots":
                for member in ctx.guild.members:
                    if member.bot:
                        if not member.get_role(role.id):
                            condition = False
                            await member.add_roles(role, reason="Updating all bots in the server\nBy: {0}".format(ctx.author.name))
                            
                if condition:
                    for member in ctx.guild.members:
                        if member.bot:
                            await member.remove_roles(role, reason="Updating all bots in the server\nBy: {0}".format(ctx.author.name))
                await ctx.send("All Bots have been updated successfully.")
                return
            
            elif member.lower() == "members":
                for member in ctx.guild.members:
                    if not member.bot:
                        if not member.get_role(role.id):
                            condition = False
                            await member.add_roles(role, reason="Updating all members in the server\nBy: {0}".format(ctx.author.name))
                if condition:
                    for member in ctx.guild.members:
                        if not member.bot:
                            await member.remove_roles(role, reason="Updating all members in the server\nBy: {0}".format(ctx.author.name))
                await ctx.send("All Members except Bots have been updated successfully.")
                return

            elif member.lower() == "all":
                for member in ctx.guild.members:
                    if not member.get_role(role.id):
                        condition = False
                        await member.add_roles(role, reason="Updating all members in the server\nBy: {0}".format(ctx.author.name))
                if condition:
                    for member in ctx.guild.members:
                        await member.remove_roles(role, reason="Updating all members in the server\nBy: {0}".format(ctx.author.name))
                await ctx.send("All Members have been updated successfully.")
                return
            else:
                member = ctx.guild.get_member_named(member)
                if member == None:
                    return await ctx.send("Please enter a valid nickname")
        if not member.get_role(role.id):
            await member.add_roles(role, reason="Updating a member\nBy: {0}".format(ctx.author.name))
            await ctx.send("{0} Has been updated Successfully".format(member.name))
        else:
            await member.remove_roles(role, reason="Updating a member\nBy: {0}".format(ctx.author.name))
            await ctx.send("{0} Has been updated Successfully".format(member.name))
        
    @commands.command(help="""Locks a channel/Category.
                      Permissions Required: `Manage Channels`
                      
                      Ex:
                      {0}lock -> locks current channel
                      {0}lock `channel name` -> locks a specific channel
                      {0}lock `channel id` -> locks a specific channel
                      {0}lock `#channel` -> locks a specific channel
                      {0}lock `#category` -> locks all channels in a specific category
                      {0}lock `category id` -> locks all channels in a specific category""", description="Locks a channel/Category.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context, channel : Union[discord.TextChannel, discord.CategoryChannel] = None):
        if channel == None:
            channel = ctx.channel
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        if type(channel) == discord.TextChannel:
            await ctx.send("{0} has been locked".format(channel.mention))
            await channel.set_permissions(ctx.guild.default_role,
                                        overwrite=overwrite,
                                        reason="Channel Updated by {0}".format(ctx.author.name))
        elif type(channel) == discord.CategoryChannel:
            await ctx.send("All channels in {0} have been locked".format(channel.mention))
            for child_channel in channel.text_channels:
                await child_channel.set_permissions(ctx.guild.default_role,
                                            overwrite=overwrite,
                                            reason="Channel Updated by {0}".format(ctx.author.name))
        
    
    @commands.command(help="""unlocks a channel/Category.
                      Permissions Required: `Manage Channels`
                      
                      Ex:
                      {0}unlock -> unlocks current channel
                      {0}unlock `channel name` -> unlocks a specific channel
                      {0}unlock `channel id` -> unlocks a specific channel
                      {0}unlock `#channel` -> unlocks a specific channel
                      {0}unlock `#category` -> unlocks all channels in a specific category
                      {0}unlock `category id` -> unlocks all channels in a specific category""", description="unlocks a channel/Category.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context, channel : Union[discord.TextChannel, discord.CategoryChannel] = None):
        if channel == None:
            channel = ctx.channel
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        if type(channel) == discord.TextChannel:
            await channel.set_permissions(ctx.guild.default_role,
                                        overwrite=overwrite,
                                        reason="Channel Updated by {0}".format(ctx.author.name))
            await ctx.send("{0} has been unlocked".format(channel.mention))
        elif type(channel) == discord.CategoryChannel:
            for child_channel in channel.text_channels:
                await child_channel.set_permissions(ctx.guild.default_role,
                                            overwrite=overwrite,
                                            reason="Channel Updated by {0}".format(ctx.author.name))
            await ctx.send("All channels in {0} have been unlocked".format(channel.mention))

#------------------------- ERROR HANDLING --------------------#
    @setprefix.error
    async def setprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the permission to Change Prefix.")
        else:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
        
    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the permission to Clear Chat.")
        elif isinstance(error.original, discord.Forbidden):
            await ctx.send("The Bot Doesn't have permissions to Kick members.")
        else:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
        
    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the permission to Kick Members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please Enter a valid member ID/Mention")
        elif isinstance(error.original, discord.Forbidden):
            await ctx.send("The Bot Doesn't have permissions to Kick members.")
        else:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
    
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the permission to Ban Members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please Enter a valid member ID/Mention")
        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send("Only Member mention, ID, name are only valid")
        elif isinstance(error.original, discord.Forbidden):
            await ctx.send("The Bot Doesn't have permissions to Ban members.")
        else:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
        

    
    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the permission to unban Members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please Enter a valid member ID")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("IDs Only are only allowed")
        elif isinstance(error.original, discord.Forbidden):
            await ctx.send("The Bot Doesn't have permissions to unban members.")
        else:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
    
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permissions to update Members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please Enter a valid member ID/Mention/Name and a valid Role Mention")
        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send("Members only are allowed")
        elif isinstance(error.original, discord.Forbidden):
            await ctx.send("The Bot Doesn't have permissions to update members.")
        else:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
    
    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send("You don't have permissions to Manage Channels.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Please Enter a valid Channel ID/Mention or Category ID/mention")
        elif isinstance(error, commands.BadUnionArgument):
            return await ctx.send("Channels/Categories only are allowed")
        try:
            if isinstance(error.original, discord.Forbidden):
                await ctx.send("The Bot Doesn't have permissions to Manage Channels.")
        except:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
            
    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.send("You don't have permissions to Manage Channels.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send("Please Enter a valid Channel ID/Mention or Category ID/mention")
        elif isinstance(error, commands.BadUnionArgument):
            return await ctx.send("Channels/Categories only are allowed")
        try:
            if isinstance(error.original, discord.Forbidden):
                await ctx.send("The Bot Doesn't have permissions to Manage Channels.")
        except:
            await ctx.send("An error occured please report using </report:1162168670169075843>")
     
        
def setup(bot):
    bot.add_cog(Moderation(bot)) 