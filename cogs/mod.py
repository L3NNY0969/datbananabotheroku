import discord
import sys
import os
import io
import asyncio
import json
import ezjson
from discord.ext import commands


class mod:
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        
        
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def dm(self, ctx, user: discord.Member, *, msg: str):
        """Escort your DM to someone thru the bot. Usage: *dm [tag person] [msg]"""
        try:
            await user.send(msg)
            await ctx.message.delete()            
            await ctx.send("SuccESS! Your DM has made it! :white_check_mark: ")
        except commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with DM'ing people without permissions.")
        except:
            await ctx.send("Error :x:. Make sure your message is shaped in this way: *dm [tag person] [msg]")


    
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        """It's time to stop. Sends that warning. Usage: *warn [tag person] [reason]"""
        try:
            color = discord.Color(value=0xf44242)
            em = discord.Embed(color=color, title=f"WARNING: by {ctx.message.author.name} from **{ctx.author.guild.name}**.", description=f"{reason}")
            await user.send(embed=em)
            await ctx.message.delete()
            await ctx.send("User has been DM'd :white_check_mark:. Pray that the user is a gud boi now. :pray:")
        except discord.ext.commands.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with warning people without permissions.")
        except:
            await ctx.send("Something happened and the DM could not make it :x:. The user could be blocking DMs from the server, or you did not use the format correctly. Usage: *warn [tag person] [reason].")    
       
    @commands.command()
    @commands.has_permissions(manage_messages = True)
    async def purge(self, ctx, num: int):
        """Deletes a # of msgs. *purge [# of msgs].""" 
        try: 
            if num is None:
                await ctx.send("How many messages would you like me to delete? Usage: *purge [number of msgs]")
            else:
                try:
                    float(num)
                except ValueError:
                    return await ctx.send("The number is invalid. Make sure it is valid! Usage: *purge [number of msgs]")
                await ctx.channel.purge(limit=num+1)
                msg = await ctx.send("Purged successfully :white_check_mark:", delete_after=3)
        except discord.Forbidden:
            await ctx.send("Purge unsuccessful. The bot does not have Manage Msgs permission.")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with purging without permissions.")
    
    
    @commands.command()
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, user: discord.Member = None, *, reason=None):
        """Kicks a member into the world outside your server."""
        if user is None:
            await ctx.send("To boot the member, use the command like this: \n*kick [@user] [reason]")
        try:
            await user.kick(reason=reason)
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Kicked!')
            em.add_field(name='User', value=user.name)
            em.add_field(name='Kicked By', value=ctx.author.name)
            if reason is None:
                reason = 'No reason given.'
            else:
                reason = reason
            em.add_field(name='Reason', value=reason)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to use the boot.")
        except commands.errors.MissingPermissions:
            await ctx.send("Nice try. You need `Kick Members` Permission to use this!")
        
        
    
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: discord.Member = None, *, reason=None):
        """Swings the mighty Ban Hammer on that bad boy."""
        if user is None:
            await ctx.send("To swing the ban hammer, use the command like this: \n*ban [@user] [days of msgs to delete] [reason]")
        try:
            await user.ban(reason=reason)
            color = discord.Color(value=0x00ff00)
            em = discord.Embed(color=color, title='Banned!')
            em.add_field(name='User', value=user.name)
            em.add_field(name='Banned By', value=ctx.author.name)
            reason = reason if reason is not None else 'No reason given.'
            em.add_field(name='Reason', value=reason)
            em.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        except commands.errors.MissingPermissions:
            await ctx.send("Nice try. You need `Ban Members` Permissions to use this!")



    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def mute(self, ctx, user: discord.Member, mutetime=None):
        '''Forces someone to shut up. Usage: *mute [user] [time in mins]'''
        try:
            if mutetime is None:
                await ctx.channel.set_permissions(user, send_messages=False)
                await ctx.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
            else:
                try:
                    mutetime =int(mutetime)
                    mutetime = mutetime * 60
                except ValueError:
                    return await ctx.send("Your time is an invalid number. Make sure...it is a number.")
                await ctx.channel.set_permissions(user, send_messages=False)
                await ctx.channel.send(f"{user.mention} is now forced to shut up. :zipper_mouth: ")
                await asyncio.sleep(mutetime)
                await ctx.channel.set_permissions(user, send_messages=True)
                await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            return await ctx.send("I could not mute the user. Make sure I have the manage channels permission.")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def servermute(self, ctx, user: discord.Member = None):
        '''Forces someone to shut up through the entire server. OUCH.'''
        if user is None:
            await ctx.send("Bruh. Tag a user to mute them...")
        else:
            msg = await ctx.send("Muting user...")
            try:
                lol = discord.utils.get(ctx.guild.roles, name='Muted')
                await user.add_roles(lol)
            except:
                try:
                    role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(permissions=68420672)) 
                    # Given permissions: Change nickname, read messages, use external emojis, add reactions, 
                    # voice: view channel, voice: connect. EVERYTHING ELSE IS DISABLED.
                    await user.add_roles(role)
                except discord.Forbidden:
                    return await msg.edit(content="Don't have enough permissions. For flawless bot functions, give the Administrator permission to the bot.")
            await msg.edit(content="The user has been muted for this server. :zipper_mouth:")


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def serverunmute(self, ctx, user: discord.Member = None):
        '''Un-shuts someone up from the entire server. YEEE.'''
        if user is None:
            await ctx.send("Bruh. Tag a user to unmute them...")
        else:
            msg = await ctx.send("Unmuting user...")
            try:
                await user.remove_roles("Muted")
            except discord.Forbidden:
                return await ctx.send("Uh-oh! Not enough permissions!")
            await msg.edit(content="The user has been unmuted for this server. :grin:")



    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unmute(self, ctx, user: discord.Member):
        '''Allows someone to un-shut up. Usage: *unmute [user]'''
        try:
            await ctx.channel.set_permissions(user, send_messages=True)
            await ctx.channel.send(f"{user.mention} is now un-shutted up.")
        except discord.Forbidden:
            await ctx.send("Couldn't unmute the user. Uh-oh...")
        except commands.errors.MissingPermissions:
            await ctx.send("Aw, come on! You thought you could get away with shutting someone up without permissions.")              
    

    @commands.command(aliases=['welcome'])
    async def welcomemsg(self, ctx, action=None):
        if action is None:
            em = discord.Embed(color=discord.Color(value=0x00ff00), title='Welcome Messages')
            try:
                x = await self.bot.db.datbananabot.modlog.find_one({"id": str(ctx.guild.id)})
                if x['channel'] is False:
                    em.description = 'Welcome messages are disabled for this server.'
                else:
                    em.description = f"Welcome messages are turned on for this server, set in <#{x['channel']}>.\n\nMessage: {x['message']}"
            except KeyError:
                em.description = 'Welcome messages are disabled for this server.'
            await ctx.send(embed=em)
        else:
            if action.lower() == 'on':
                await ctx.send("Please mention the channel to set welcome messages in.")
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                if not x.content.startswith("<#") and not x.content.endswith(">"):
                    return await ctx.send("Please properly mention the channel.")
                channel = x.content.strip("<#").strip(">")
                try:
                    channel = int(channel)
                except ValueError:
                    return await ctx.send("Did you properly mention a channel? Probably not.")
                await ctx.send("Please enter the message to send when someone joins.\n\n```Variables: \n{name}: The user's name.\n{mention}: Mention the user.\n{members}: The amount of members currently in the server.```")
                try:
                    x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
                except asyncio.TimeoutError:
                    return await ctx.send("Request timed out. Please try again.")
                await self.bot.db.datbananabot.welcome.insert_one({"id": str(ctx.guild.id), "channel": channel, "message": x.content})
                await ctx.send("Successfully turned on welcome messages for this guild.")
            elif action.lower() == 'off':
                await self.bot.db.datbananabot.welcome.insert_one({"id": str(ctx.guild.id), "channel": False, "message": None})
                await ctx.send("Successfully turned off welcome messages for this guild.")


    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def modlog(self, ctx, action=None):
        if action is None:
            x = await self.bot.db.datbananabot.modlog.find_one({"id": str(ctx.guild.id)})
            em = discord.Embed(color=discord.Color(value=0x00ff00), title="Mod Log Status")
            try:
                x['channel']
                em.description = f"Mod logs are enabled in this server, in <#{x['channel']}>."
            except KeyError:
                em.description = 'Mod logs are turned off for this server.'
            return await ctx.send(embed=em)
        if action.lower() == 'on':
            await ctx.send("Please mention the channel for mod logs to be sent in.")
            try:
                x = await self.bot.wait_for("message", check=lambda x: x.channel == ctx.channel and x.author == ctx.author, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send("Request timed out. Please try again.")
            if not x.content.startswith("<#") and not x.content.endswith(">"):
                return await ctx.send("Please properly mention the channel.")
            channel = x.content.strip("<#").strip(">")
            try:
                channel = int(channel)
            except ValueError:
                return await ctx.send("Did you properly mention a channel? Probably not.")
            await self.bot.db.datbananabot.modlog.insert_one({"id": str(ctx.guild.id), "channel": channel})
            return await ctx.send(f"Successfully turned on Mod Logs in <#{channel}>. Enjoy! :white_check_mark:")
        if action.lower() == 'off':
            await self.bot.db.datbananabot.modlog.insert_one({"id": str(ctx.guild.id), "channel": False})
            return await ctx.send("Turned off Mod Logs. Whew...")
        else:
            return await ctx.send("That ain't an action. Please enter either `on` or `off`.")


    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def prefix(self, ctx, prefix=None):
        em = discord.Embed(color=discord.Color(value=0x00ff00), title="Bot Prefix")
        if prefix is None:
            em.description = f"The bot's prefix for server **{ctx.guild.name}** is set to `{ctx.prefix}`."
            return await ctx.send(embed=em)
        if prefix.lower() == 'clear':
            await self.bot.db.datbananabot.prefix.update_one({"id": str(ctx.guild.id)}, {"$set": {"prefix": "="}}, upsert=True)
            em.description = f"The bot's prefix is now set to the default: `*`."
            return await ctx.send(embed=em)
        else:
            await self.bot.db.datbananabot.prefix.update_one({"id": str(ctx.guild.id)}, {"$set": {"prefix": prefix}}, upsert=True)
            em.description = f"The bot's prefix for this server is set to: `{prefix}`."
            return await ctx.send(embed=em)
        
            
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def hackban(self, ctx, id = None, reason=None):
        if id is None:
            return await ctx.send("Please enter the ID of a person to ban them.")
        try:
            id = int(id)
        except ValueError:
            return await ctx.send("Did you enter a valid user ID?")
        lol = discord.Object(id)
        try:
            await ctx.guild.ban(lol, reason=reason)
        except discord.Forbidden:
            await ctx.send("Oops! I don't have enough permissions to swing this ban hammer.")
        color = discord.Color(value=0x00ff00)
        em = discord.Embed(color=color, title='Banned!')
        em.add_field(name='Banned By', value=ctx.author.name)
        reason = reason if reason is not None else 'No reason given.'
        em.add_field(name='Reason', value=reason)
        await ctx.send(embed=em)
        







def setup(bot): 
    bot.add_cog(mod(bot))        

