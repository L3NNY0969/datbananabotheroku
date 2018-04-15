import discord
import sys
import os
import io
import asyncio
import aiohttp
import random
import subprocess
import json
import ezjson
import inspect
import traceback
from contextlib import redirect_stdout
from collections import Counter
from inspect import getsource
from discord.ext import commands


class Developer:
    def __init__(self, bot):
       self.bot = bot
       self.sessions = set()


    def dev_check(self, id):
        with open('data/devs.json') as f:
            devs = json.load(f)
            if id in devs:
                return True
        return False


    def owner_check(self, id):
        if id == 277981712989028353:
            return True
        return False
       

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content.strip('` \n')


    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'
       
       
    @commands.command()
    async def restart(self, ctx):
        """Makes the bot shut UP and then shut DOWN, then start up again."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        msg = await ctx.send("Shutting down...")
        await asyncio.sleep(1)
        await msg.edit(content="Goodbye! :wave:")
        await self.bot.logout()
        
        
    @commands.command()
    async def changename(self, ctx, name=None):
        """Changes my name. Please make it good!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        if name is None:
            return await ctx.send("Hmm...my name cannot be blank!")
        else:
            await self.bot.user.edit(username=f'{name}')


    @commands.command()
    async def exec(self, ctx, *, code):
        """Executes code like the Command Line."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        e = discord.Embed(color=discord.Color(value=0x00ff00), title='Running code...')
        e.description = f'```{code}```'
        msg = await ctx.send(embed=e)
        lol = subprocess.run(f"{code}", cwd='/app', stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
        em = discord.Embed(color=discord.Color(value=0x00ff00), title='Ran on the Command Prompt!')
        if lol == '':
            code = 'The output is empty. (This is not a Command Prompt message.)'
        if len(lol) > 1850:
            em.description = f"Ran on the Command Line ```{code}``` Output: \nThe process details are too large to fit in a message."
            await msg.edit(embed=em)
        else:
            em.description = f"Ran on the Command Line: ```{code}``` Output: \n\n```{lol}```"
            await msg.edit(embed=em)

    @commands.command()
    async def update(self, ctx):
        """Updates the bot. Ez!"""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        msg = await ctx.send("Bot updating... :arrows_counterclockwise:")
        try:
            lol = subprocess.run("git pull", cwd='/app', stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')
            for cog in self.bot.cogs:
                cog = cog.lower()
                self.bot.unload_extension(f"cogs.{cog}")
                self.bot.load_extension(f"cogs.{cog}")
            await msg.edit(content=f"All cogs reloaded, and READY TO ROLL! :white_check_mark: \n\nLog:\n```{lol}```")
        except Exception as e:
            await msg.edit(content=f"An error occured. :x: \n\nDetails: \n{e}")


    @commands.command()
    async def loadcog(self, ctx, cog=None):
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        if cog is None:
            await ctx.send("Please enter a cog to load it!")
        else:
            msg = await ctx.send(f"Loading cog `{cog}`... :arrows_counterclockwise:")
            try:
                self.bot.load_extension(f"cogs.{cog}")
                await msg.edit(content="Loaded the cog! :white_check_mark:")
            except Exception as e:
                await msg.edit(content=f"An error occured. Details: \n{e}")


    @commands.command()
    async def unloadcog(self, ctx, cog=None):
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        if cog is None:
            await ctx.send("Please enter a cog to unload it!")
        else:
            msg = await ctx.send(f"Unloading cog `{cog}`... :arrows_counterclockwise:")
            try:
                self.bot.unload_extension(f"cogs.{cog}")
                await msg.edit(content="Unloaded the cog! :white_check_mark:")
            except Exception as e:
                await msg.edit(content=f"An error occured. Details: \n{e}")


    @commands.command()
    async def reloadcog(self, ctx, cog=None):
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        if cog is None:
            await ctx.send("Please enter a cog to reload it!")
        else:
            msg = await ctx.send(f"Reloading cog `{cog}`... :arrows_counterclockwise:")
            try:
                self.bot.unload_extension(f"cogs.{cog}")
                self.bot.load_extension(f"cogs.{cog}")
                await msg.edit(content="Reloaded the cog! :white_check_mark:")
            except Exception as e:
                await msg.edit(content=f"An error occured. Details: \n{e}")


    @commands.command()
    async def source(self, ctx, command=None):
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        cmd = self.bot.get_command(command)
        if cmd is None:
            return await ctx.send("Could not find that command.")
        await ctx.send(f"```py\n{getsource(cmd.callback)}```")



    @commands.command(pass_context=True, hidden=True)
    async def repl(self, ctx):
        """Launches an interactive REPL session."""
        if not self.dev_check(ctx.author.id):
            return await ctx.send("HALT! This command is for the devs only. Sorry. :x:")
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return

        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')

        def check(m):
            return m.author.id == ctx.author.id and \
                   m.channel.id == ctx.channel.id and \
                   m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self.sessions.remove(ctx.channel.id)
                break

            cleaned = self.cleanup_code(response.content)

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self.sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    await ctx.send(self.get_syntax_error(e))
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f'Unexpected error: `{e}`')


def setup(bot): 
    bot.add_cog(Developer(bot))   
    

